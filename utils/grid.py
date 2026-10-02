"""Réseau électrique sous forme de tableaux indexés par bus."""

from functools import cached_property
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import pypsa
import scipy.linalg as sla
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from utils import paths
from utils.inerties import get_inertia_constant
from utils.network import remove_non_synchronous_areas

F_NOMINAL = 50.0                    # Fréquence nominale (Hz)
OMEGA_S = 2 * np.pi * F_NOMINAL     # Pulsation synchrone (rad/s)


class Grid:
    """
    Réseau électrique vu comme un graphe pondéré.

    L'index de `buses` fixe l'ordre des nœuds : les matrices (incidence, laplacien, inertie)
    et les signaux sous forme de np.ndarray suivent tous cet ordre.
    Ne pas réordonner ni filtrer `buses` après création (les matrices sont mises en cache).

    Unités : PyPSA exprime x_pu sur une base de 1 MVA, donc b = 1/x_pu est en MW/rad
    et les puissances (ΔP...) sont en MW.

    Attributes:
        buses (pd.DataFrame): Un nœud par ligne, index = identifiant du bus.
            Colonnes : x (longitude), y (latitude), country,
            puis S, E, H après add_inertia.
        branches (pd.DataFrame): Une arête par ligne, colonnes bus0, bus1 et b (susceptance 1/x_pu).
            Les lignes et transformateurs en parallèle sont regroupés : leurs b s'additionnent.
    """

    def __init__(self,
                 network_path: Path = paths.CLUSTERED_NETWORK,
                 powerplants_path: Path = paths.POWERPLANTS):
        """
        Chaîne complète : chargement du réseau PyPSA, retrait des zones non synchrones,
        construction du graphe, puis calcul des inerties.
        """
        n = remove_non_synchronous_areas(pypsa.Network(network_path))
        self.buses, self.branches = self._df_from_pypsa(n)
        self.add_inertia(powerplants_path)

    @classmethod
    def from_df(cls, buses: pd.DataFrame, branches: pd.DataFrame) -> "Grid":
        """Grid construit directement à partir des tableaux (sans inerties sauf colonne E fournie)."""
        grid = cls.__new__(cls)   # contourne __init__, qui lit les fichiers
        grid.buses, grid.branches = buses, branches
        return grid

    @classmethod
    def from_pypsa(cls, n: pypsa.Network) -> "Grid":
        """
        Grid construit à partir d'un réseau PyPSA déjà chargé (sans inerties : appeler add_inertia).
        Le réseau n'est pas modifié, hors calcul de ses valeurs dépendantes (x_pu).
        """
        return cls.from_df(*cls._df_from_pypsa(n))

    @staticmethod
    def _df_from_pypsa(n: pypsa.Network) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Tableaux buses et branches à partir des bus, lignes et transformateurs d'un réseau PyPSA.
        Les liaisons HVDC (links) ne sont pas prises en compte.
        """
        n.calculate_dependent_values()
        buses = n.buses[["x", "y", "country"]].copy()

        branches = pd.concat([n.lines[["bus0", "bus1", "x_pu"]],
                              n.transformers[["bus0", "bus1", "x_pu"]]])
        # Orienter chaque paire de bus dans le même sens pour regrouper les branches parallèles
        swap = branches.bus0 > branches.bus1
        branches.loc[swap, ["bus0", "bus1"]] = branches.loc[swap, ["bus1", "bus0"]].to_numpy()
        branches = (branches.assign(b=1 / branches.x_pu)
                    .groupby(["bus0", "bus1"], as_index=False).b.sum())
        return buses, branches

    def add_inertia(self, path_to_powerplants_csv: Path):
        """
        Calcule l'inertie par nœud à partir des centrales qui y sont raccordées.
        Ajoute à self.buses les colonnes :
        - 'S' : capacité installée totale (MW)
        - 'E' : énergie cinétique stockée, somme des H_i * S_i (MW·s)
        - 'H' : constante d'inertie équivalente E / S (s), 0 s'il n'y a aucune centrale

        Les centrales dont le bus n'est pas dans le réseau (zones non synchrones) sont ignorées.
        """
        plants = pd.read_csv(path_to_powerplants_csv)
        plants["H"] = [get_inertia_constant(t, f) for t, f in zip(plants.Technology, plants.Fueltype)]
        plants["E"] = plants.H * plants.Capacity

        in_grid = plants.bus.isin(self.buses.index)
        print(f"{(~in_grid).sum()} centrales hors du réseau ignorées "
              f"({plants.Capacity[~in_grid].sum() / 1e3:.0f} GW)")
        per_bus = (plants[in_grid].groupby("bus")[["Capacity", "E"]].sum()
                   .reindex(self.buses.index, fill_value=0.0))

        self.buses["S"] = per_bus.Capacity
        self.buses["E"] = per_bus.E
        self.buses["H"] = (per_bus.E / per_bus.Capacity).where(per_bus.Capacity > 0, 0.0)
        # Les modes dépendent de M : invalider le cache s'il existe
        self.__dict__.pop("_modes_computation", None)

    @cached_property
    def incidence(self) -> sp.csr_array:
        """Matrice d'incidence K (branches x bus) : +1 sur bus0, -1 sur bus1."""
        i0 = self.buses.index.get_indexer(self.branches.bus0)
        i1 = self.buses.index.get_indexer(self.branches.bus1)
        if (i0 < 0).any() or (i1 < 0).any():
            raise ValueError("Certaines branches sont raccordées à un bus absent de `buses`.")
        rows = np.arange(len(self.branches))
        data = np.r_[np.ones(len(rows)), -np.ones(len(rows))]
        return sp.csr_array((data, (np.r_[rows, rows], np.r_[i0, i1])),
                            shape=(len(self.branches), len(self.buses)))

    @cached_property
    def L(self) -> sp.csr_array:
        """Laplacien pondéré L = Kᵀ diag(b) K (bus x bus), en MW/rad."""
        K = self.incidence
        return (K.T @ sp.diags_array(self.branches.b.to_numpy()) @ K).tocsr()

    @property
    def M(self) -> sp.dia_array:
        """
        Matrice d'inertie diagonale M = diag(2 E / ω_s) (bus x bus), en MW·s²/rad.
        Cohérente avec L dans l'équation d'oscillation M δ'' + L δ = ΔP.
        Non mise en cache : suit les colonnes E de buses si add_inertia est rappelée.
        """
        if "E" not in self.buses:
            raise AttributeError("Inerties absentes : appeler add_inertia d'abord.")
        return sp.diags_array(2 * self.buses.E.to_numpy() / OMEGA_S)

    @cached_property
    def _modes_computation(self) -> dict:
        """
        Équation d'oscillation linéarisée sans amortissement : M δ'' + L δ = ΔP.

        Les nœuds sans inertie (M = 0, indice l) n'ont pas de dynamique propre : leurs équations
        sont algébriques et on les élimine par réduction de Kron. Sur les nœuds avec inertie (indice g) :
            δ_l   = L_ll⁻¹ (ΔP_l − L_lg δ_g)
            L_red = L_gg − L_gl L_ll⁻¹ L_lg          (laplacien réduit)
            P_red = ΔP_g − L_gl L_ll⁻¹ ΔP_l          (perturbation reportée sur les nœuds avec inertie)
        Le système réduit M_g δ_g'' + L_red δ_g = P_red est diagonalisé par le problème aux valeurs
        propres généralisé L_red v = λ M_g v, dont les modes vérifient Vᵀ M_g V = I.

        Calculé une fois, au premier accès (invalidé par add_inertia).
        """
        m = self.M.diagonal()
        g = m > 0
        l = ~g

        L = self.L
        L_gg, L_gl = L[g][:, g], L[g][:, l]
        # Factorisation de L_ll réutilisée pour chaque perturbation
        lu_ll = spla.splu(L[l][:, l].tocsc())
        kron = lu_ll.solve(L[l][:, g].toarray())    # L_ll⁻¹ L_lg

        L_red = L_gg.toarray() - L_gl @ kron
        L_red = (L_red + L_red.T) / 2   # symétrique aux erreurs d'arrondi près
        eigenvalues, modes = sla.eigh(L_red, np.diag(m[g]))
        # Le réseau est connexe : une seule valeur propre nulle (≈ 1e-8 par erreurs d'arrondi)
        if not (eigenvalues[1] > 1e3 * abs(eigenvalues[0])):
            raise ValueError("Le mode 0 n'est pas isolé : le réseau réduit n'est pas connexe ?")
        eigenvalues[0] = 0.0

        return {"inertial": g, "eigenvalues": eigenvalues, "modes": modes,
                "lu_ll": lu_ll, "kron": kron, "L_gl": L_gl}

    @property
    def inertial(self) -> np.ndarray:
        """Masque booléen des nœuds avec inertie (M > 0), dans l'ordre de buses."""
        return self._modes_computation["inertial"]

    @property
    def eigenvalues(self) -> np.ndarray:
        """
        λ_k (1/s²) du problème L_red v = λ M_g v, pulsation ω_k = √λ_k.
        λ_0 = 0 : mode du centre d'inertie (tout le réseau accélère ensemble).
        """
        return self._modes_computation["eigenvalues"]

    @property
    def modes(self) -> np.ndarray:
        """V (nœuds avec inertie x modes), M_g-orthonormés."""
        return self._modes_computation["modes"]

    @property
    def frequencies(self) -> np.ndarray:
        """Fréquences propres des modes (Hz)."""
        return np.sqrt(self.eigenvalues) / (2 * np.pi)

    def step_response(self, delta_P, t) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Réponse à un échelon de puissance ΔP appliqué à t = 0, à partir de l'équilibre (δ = δ' = 0).

        En coordonnées modales q = Vᵀ M_g δ_g, chaque mode est un oscillateur q_k'' + λ_k q_k = p_k,
        avec p = Vᵀ P_red :
            mode 0     : q_0 = p_0 t² / 2                       (dérive du centre d'inertie)
            modes k ≥ 1 : q_k = p_k / λ_k · (1 − cos ω_k t)

        Args:
            delta_P: Perturbation (MW) par nœud, pd.Series indexée par bus ou tableau dans l'ordre de buses.
                Négative pour une perte de production.
            t (np.ndarray): Instants (s).

        Returns:
            (delta, freq): DataFrames bus x instants : écart d'angle δ (rad)
            et écart de fréquence Δf = δ' / 2π (Hz).
        """
        s = self._modes_computation
        g = s["inertial"]
        l = ~g
        dP = self.to_array(delta_P).astype(float)
        t = np.asarray(t, dtype=float)

        # Perturbation reportée sur les nœuds avec inertie, puis projetée sur les modes
        Lll_inv_P_l = s["lu_ll"].solve(dP[l])
        p = s["modes"].T @ (dP[g] - s["L_gl"] @ Lll_inv_P_l)

        lam = s["eigenvalues"][1:, None]
        omega = np.sqrt(lam)
        q = np.empty((len(p), len(t)))
        dq = np.empty((len(p), len(t)))
        q[0], dq[0] = p[0] * t**2 / 2, p[0] * t
        q[1:] = p[1:, None] / lam * (1 - np.cos(omega * t))
        dq[1:] = p[1:, None] / omega * np.sin(omega * t)

        delta = np.empty((len(dP), len(t)))
        speed = np.empty((len(dP), len(t)))
        delta[g], speed[g] = s["modes"] @ q, s["modes"] @ dq
        # Nœuds sans inertie : relation algébrique (ΔP constant pour t > 0)
        delta[l] = Lll_inv_P_l[:, None] - s["kron"] @ delta[g]
        speed[l] = -s["kron"] @ speed[g]

        columns = pd.Index(t, name="t")
        return (pd.DataFrame(delta, index=self.buses.index, columns=columns),
                pd.DataFrame(speed / (2 * np.pi), index=self.buses.index, columns=columns))

    def to_array(self, values) -> np.ndarray:
        """Signal dans l'ordre de buses (accepte une pd.Series indexée par bus ou un tableau)."""
        if isinstance(values, pd.Series):
            return values.reindex(self.buses.index).to_numpy()
        values = np.asarray(values)
        if len(values) != len(self.buses):
            raise ValueError(f"Signal de longueur {len(values)} pour {len(self.buses)} bus.")
        return values

    def to_networkx(self) -> nx.Graph:
        """Graphe NetworkX (attribut d'arête 'weight' = b), pour les algorithmes de graphe."""
        G = nx.Graph()
        G.add_nodes_from(self.buses.index)
        G.add_weighted_edges_from(self.branches[["bus0", "bus1", "b"]].itertuples(index=False))
        return G
