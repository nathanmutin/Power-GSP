import numpy as np
import pypsa
import pandas as pd
from pathlib import Path
from functools import cached_property
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import scipy.linalg as sla

from utils import paths
from utils.network import remove_non_synchronous_areas
from utils.inerties import get_inertia_constants

F_NOMINAL = 50.0                    # Fréquence nominale (Hz)
OMEGA_S = 2 * np.pi * F_NOMINAL     # Pulsation synchrone (rad/s)


class Grid:
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
        
        self.rayleigh_alpha = 0
        self.rayleigh_beta = 0

    def invalidate_cache(self):
        """
        Plusieurs properties sont calculées la première fois qu'on y accède et mises en cache.
        Cette fonction supprime le cache.
        Par exemple, après avoir modifié les inerties, il faut recalculer les modes.
        """
        for name in self.__class__.__dict__:
            self.invalidate_cached_property(name)
    
    def invalidate_cached_property(self, property_name: str):
        """
        Supprime le cache d'une propriété calculée la première fois qu'on y accède.
        Par exemple, après avoir modifié les inerties, il faut recalculer les modes.
        """
        attr = getattr(self.__class__, property_name)
        if isinstance(attr, cached_property):
            try:
                delattr(self, property_name)
            except AttributeError:
                pass

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
    
    def to_array(self, series: pd.Series) -> np.ndarray:
        """
        Convertit une pd.Series indexée par bus en np.ndarray dans l'ordre de self.buses.index.
        """
        # If already a numpy array of the right length, return it
        if isinstance(series, np.ndarray):
            if len(series) != len(self.buses):
                raise ValueError(f"Le tableau numpy a une longueur de {len(series)}, mais le réseau a {len(self.buses)} buses.")
            return series
            
        
        missing = self.buses.index.difference(series.index)
        if len(missing):
            raise ValueError(f"{len(missing)} bus absents du signal, "
                                f"par ex. {list(missing[:5])}")
        return series.reindex(self.buses.index).to_numpy()

    def add_inertia(self, path_to_powerplants_csv: Path):
        """
        Calcule l'inertie par nœud à partir des centrales qui y sont raccordées.
        Ajoute à self.buses les colonnes :
        - 'S' : capacité installée totale (MW)
        - 'S_sync' : capacité des centrales synchrones, H > 0 (MW)
        - 'E' : énergie cinétique stockée, somme des H_i * S_i (MW·s)
        - 'H' : constante d'inertie équivalente E / S (s), 0 s'il n'y a aucune centrale

        Les centrales dont le bus n'est pas dans le réseau (zones non synchrones) sont ignorées.
        """
        # Première chose à faire
        self.invalidate_cache()
        
        plants = pd.read_csv(path_to_powerplants_csv)
        plants["H"] = get_inertia_constants(plants.Technology, plants.Fueltype)
        plants["E"] = plants.H * plants.Capacity
        plants["S_sync"] = plants.Capacity.where(plants.H > 0, 0.0)

        in_grid = plants.bus.isin(self.buses.index)
        print(f"{(~in_grid).sum()} centrales hors du réseau ignorées "
              f"({plants.Capacity[~in_grid].sum() / 1e3:.0f} GW)")
        per_bus = (plants[in_grid].groupby("bus")[["Capacity", "S_sync", "E"]].sum()
                   .reindex(self.buses.index, fill_value=0.0))

        self.buses["S"] = per_bus.Capacity
        self.buses["S_sync"] = per_bus.S_sync
        self.buses["E"] = per_bus.E
        self.buses["H"] = (per_bus.E / per_bus.Capacity).where(per_bus.Capacity > 0, 0.0)

    @cached_property
    def incidence(self) -> sp.csr_array:
        """Matrice d'incidence K (branches x bus) : +1 sur bus0, -1 sur bus1."""
        i0 = self.buses.index.get_indexer(self.branches.bus0)
        i1 = self.buses.index.get_indexer(self.branches.bus1)
        if (i0 < 0).any() or (i1 < 0).any():
            raise ValueError("Certaines branches sont raccordées à un bus absent de `buses`.")
        
        # Pour construire une matrice sparse il faut fournir:
        # data, row_ind and col_ind tels que
        # a[row_ind[k], col_ind[k]] = data[k]
        rows = np.arange(len(self.branches))
        # la première moitié des k correspond à +1 (bus0),
        # la deuxième moitié à -1 (bus1)
        row_ind = np.r_[rows, rows]
        col_ind = np.r_[i0, i1]
        data = np.r_[np.ones(len(rows)), -np.ones(len(rows))]
        return sp.csr_array((data, (row_ind, col_ind)),
                            shape=(len(self.branches), len(self.buses)))

    @cached_property
    def L(self) -> sp.csr_array:
        """Laplacien pondéré L = Kᵀ diag(b) K (bus x bus), en MW/rad."""
        K = self.incidence
        return (K.T @ sp.diags_array(self.branches.b.to_numpy()) @ K).tocsr()

    @cached_property
    def M(self) -> sp.dia_array:
        """
        Matrice d'inertie diagonale M = diag(2 E / ω_s) (bus x bus), en MW·s²/rad.
        """
        if "E" not in self.buses:
            raise AttributeError("Inerties absentes : appeler add_inertia d'abord.")
        return sp.diags_array(2 * self.buses.E.to_numpy() / OMEGA_S)
    
    @cached_property
    def lu_L_ll(self) -> spla.SuperLU:
        """
        Factorisation LU de L_ll (nœuds sans inertie) pour la réduction de Kron.
        """
        m = self.M.diagonal()
        l = (m == 0)
        L_ll = self.L[l, :][:, l]
        return spla.splu(sp.csc_array(L_ll))
    
    @cached_property
    def L_reduced(self) -> sp.csr_array:
        """
        Laplacien réduit L_red = L_gg − L_gl L_ll⁻¹ L_lg (nœuds avec inertie).
        """
        m = self.M.diagonal()
        g = (m > 0)
        l = ~g
        L_gg, L_gl = self.L[g, :][:, g], self.L[g, :][:, l]
        return L_gg - L_gl @ self.lu_L_ll.solve(L_gl.toarray().T)
    
    def l_from_g_values(self, g_nodes: np.ndarray) -> np.ndarray:
        """
        Pour un vecteur de valeurs sur les nœuds avec inertie, calcule les valeurs correspondantes
        sur les nœuds sans inertie par réduction de Kron : x_l = L_ll⁻¹ (−L_lg x_g).
        """
        m = self.M.diagonal()
        g = (m > 0)
        l = ~g
        L_lg = self.L[l, :][:, g]
        return -self.lu_L_ll.solve(L_lg @ g_nodes)
    
    @cached_property
    def _modes_computation(self) -> dict:
        """
        Équation d'oscillation linéarisée sans amortissement : M δ'' + L δ = ΔP.

        Les nœuds sans inertie (M = 0, indice l) n'ont pas de dynamique propre : leurs équations
        sont algébriques et on les élimine par réduction de Kron. Sur les nœuds avec inertie (indice g) :
            δ_l   = L_ll⁻¹ (ΔP_l − L_lg δ_g)
            L_red = L_gg − L_gl L_ll⁻¹ L_lg          (laplacien réduit)
            P_red = ΔP_g − L_gl L_ll⁻¹ ΔP_l          (perturbation reportée sur les nœuds avec inertie)
        Le système réduit M_g δ_g'' + L_red δ_g = P_red se ramène au problème aux valeurs propres
        standard de A = M_g^{-1/2} L_red M_g^{-1/2} (symétrique, semi-définie positive) :
            A V = V Λ,   Vᵀ V = I
        et se découple en coordonnées modales δ̂ = Vᵀ M_g^{1/2} δ_g (voir docs/analyse_spectrale.md).

        Calculé une fois, au premier accès
        """
        m = self.M.diagonal()
        # Indices des nœuds avec et sans inertie, g et l
        g = m > 0
        l = ~g
        
        inv_sqrt_m = 1 / np.sqrt(m[g])  # diagonale de M_g^{-1/2}
        # A = M_g^{-1/2} L_red M_g^{-1/2}
        A = inv_sqrt_m[:, None] * self.L_reduced * inv_sqrt_m[None, :]
        A = (A + A.T) / 2   # symétrique aux erreurs d'arrondi près
        # Résolution du problème aux valeurs propres standard pour A symétrique
        lambdas, V = sla.eigh(A)
    
        # Le réseau est connexe : une seule valeur propre nulle (≈ 1e-8 par erreurs d'arrondi)
        if not (lambdas[1] > 1e3 * abs(lambdas[0])):
            raise ValueError("Le mode 0 n'est pas isolé : le réseau réduit n'est pas connexe ?")
        lambdas[0] = 0.0
        
        V_full = np.empty((len(m), len(lambdas)))
        V_full[g,:] = V
        V_full[l,:] = self.l_from_g_values(V)

        # Formes des modes en angle : M_g^{1/2} V, prolongées aux nœuds sans inertie par Kron
        phis = np.empty((len(m), len(lambdas)))
        phis[g] = inv_sqrt_m[:, None] * V
        phis[l] = self.l_from_g_values(phis[g])
        return {"lambdas": lambdas, "V": V, "V_full": V_full, "phis": phis}

    @property
    def eigenvalues(self) -> np.ndarray:
        """
        λ_k (1/s²), valeurs propres de A = M_g^{-1/2} L_red M_g^{-1/2}, pulsation ω_k = √λ_k.
        λ_0 = 0 : mode du centre d'inertie (tout le réseau accélère ensemble).
        """
        return self._modes_computation["lambdas"]
    
    @property
    def pulsations(self) -> np.ndarray:
        """
        ω_k = √λ_k (rad/s), pulsations propres du système linéarisé sans amortissement.
        ω_0 = 0 : mode du centre d'inertie (tout le réseau accélère ensemble).
        """
        return np.sqrt(self.eigenvalues)
    
    @property
    def frequencies(self) -> np.ndarray:
        """
        f_k = ω_k / (2π) (Hz), fréquences propres du système linéarisé sans amortissement.
        f_0 = 0 : mode du centre d'inertie (tout le réseau accélère ensemble).
        """
        return self.pulsations / (2 * np.pi)
    
    @property
    def eigenvectors(self) -> np.ndarray:
        """
        V_k, vecteurs propres de A = M_g^{-1/2} L_red M_g^{-1/2}, normalisés Vᵀ V = I.
        """
        return self._modes_computation["V"]

    @property
    def full_eigenvectors(self) -> np.ndarray:
        return self._modes_computation["V_full"]
    
    @property
    def modes(self) -> np.ndarray:
        """
        φ_k, formes des modes en angle, prolongées aux nœuds sans inertie par Kron.
        """
        return self._modes_computation["phis"]
    
    def set_rayleigh_coefficients(self, alpha: float, beta: float):
        """
        Coefficients α et β de l'amortissement de Rayleigh ζ_k = α / (2 ω_k) + β ω_k / 2
        """
        # remove cached damping_ratios if they exist
        self.invalidate_cached_property("damping_ratios")
        self.invalidate_cached_property("D_reduced")
        self.rayleigh_alpha = alpha
        self.rayleigh_beta = beta
    
    @cached_property
    def damping_ratios(self) -> np.ndarray:
        """
        ζ_k, coefficients d'amortissement de Rayleigh pour chaque mode.
        Pas d'amortissement pour le mode 0 (centre d'inertie) : ζ_0 = 0.
        """
        zeta = np.zeros_like(self.pulsations)
        oscillating = self.pulsations > 0
        zeta[oscillating] = self.rayleigh_alpha / (2 * self.pulsations[oscillating]) + self.rayleigh_beta * self.pulsations[oscillating] / 2
        return zeta
    
    @cached_property
    def D_reduced(self) -> sp.csr_array:
        """
        Matrice d'amortissement réduite D_red = alpha M_g + beta L_red (nœuds avec inertie).
        """
        Mg = sp.diags_array(self.M.diagonal()[self.M.diagonal() > 0])
        return self.rayleigh_alpha * Mg + self.rayleigh_beta * self.L_reduced        