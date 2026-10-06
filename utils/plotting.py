import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection
from matplotlib.colors import CenteredNorm, LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D

SURFACE, INK, INK_2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
SEQUENTIAL = LinearSegmentedColormap.from_list("bleu", ["#6da7ec", "#4485d5", "#0d366b"])
DIVERGING = LinearSegmentedColormap.from_list("bleu_rouge", ["#2a78d6", "#f0efec", "#e34948"])

EXTENT = (-10.5, 40.5, 35.0, 60.5)   # lon_min, lon_max, lat_min, lat_max


def apply_style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 9,
        "text.color": INK, "axes.labelcolor": INK_2, "axes.titlecolor": INK, "axes.titlesize": 10,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "grid.linestyle": "-", "axes.axisbelow": True,
        "xtick.color": AXIS, "ytick.color": AXIS, "xtick.labelcolor": INK_2, "ytick.labelcolor": INK_2,
        "legend.frameon": False, "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
    })


def base_map(ax, country_shapes):
    """Axes de carte : frontières des pays en fond"""
    country_shapes.boundary.plot(ax=ax, color=AXIS, linewidth=0.5, zorder=0)
    # Ajuster l'aspect de la carte pour corriger la distorsion due à la projection
    ax.set_aspect(1 / np.cos(np.radians(48)))
    ax.set_axis_off()
    return ax


def segments(buses, bus0, bus1):
    """Segments droits entre les nœuds de départ et d'arrivée (coordonnées x = lon, y = lat)."""
    start = buses.loc[bus0, ["x", "y"]].to_numpy()
    end = buses.loc[bus1, ["x", "y"]].to_numpy()
    return np.stack([start, end], axis=1)


def draw_branches(ax, buses, branches, color, linewidth=0.6, zorder=1, label=None):
    collection = LineCollection(segments(buses, branches.bus0, branches.bus1), colors=color,
                                linewidths=linewidth, zorder=zorder, label=label, capstyle="round")
    ax.add_collection(collection)

    return collection


def draw_network(ax, network, shapes):
    """
    Carte du réseau électrique : lignes et liaisons HVDC sur fond de pays.

    Args:
        ax (matplotlib.axes.Axes): Axes de la figure.
        network (pypsa.Network): Réseau PyPSA.
        shapes (geopandas.GeoDataFrame): Formes des pays.
    """
    base_map(ax, shapes)

    # Trier les lignes par tension croissante pour un affichage plus esthétique
    lines = network.lines.sort_values(by="v_nom")
    buses = network.buses
    hvdc = network.links[network.links.carrier == "DC"]
    legend_handles = []

    voltage_norm = Normalize(vmin=lines.v_nom.min(), vmax=lines.v_nom.max())
    draw_branches(
        ax,
        buses,
        lines,
        SEQUENTIAL(voltage_norm(lines.v_nom.to_numpy())),
        linewidth=0.45 + 1.05 * voltage_norm(lines.v_nom.to_numpy()),
        zorder=1,
    )
    draw_branches(ax, buses, hvdc, SERIES[1], linewidth=1.6, zorder=6)

    # Jolie légende
    voltage_values = [lines.v_nom.min(), 220, 380, 400, lines.v_nom.max()]
    # Supprimer les doublons et les valeurs en dehors de la plage de tension du réseau
    voltage_values = list(dict.fromkeys(
        value for value in voltage_values
        if lines.v_nom.min() <= value <= lines.v_nom.max()
    ))
    legend_handles.extend(
        Line2D(
            [0],
            [0],
            color=SEQUENTIAL(voltage_norm(value)),
            linewidth=0.45 + 1.05 * voltage_norm(value),
            label=f"{value:g} kV",
        )
        for value in voltage_values
    )
    if len(hvdc):
        legend_handles.append(Line2D([0], [0], color=SERIES[1], linewidth=1.6,
                                    label="HVDC"))
    ax.legend(handles=legend_handles, title="Lignes", loc="upper left")

    # Cropping de la carte pour ne pas aller au-delà des limites du réseau
    xmin, xmax = buses.x.min() - 1, buses.x.max() + 1
    ymin, ymax = buses.y.min() - 1, buses.y.max() + 1
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    return ax



def draw_graph(ax, grid, shapes):
    """Fond de carte avec les branches du réseau en gris, cadré sur les bus."""
    base_map(ax, shapes)
    draw_branches(ax, grid.buses, grid.branches, "lightgray", linewidth=0.5, zorder=1)
    ax.set_xlim(grid.buses.x.min() - 1, grid.buses.x.max() + 1)
    ax.set_ylim(grid.buses.y.min() - 1, grid.buses.y.max() + 1)
    return ax


def draw_graph_signals(ax, grid, values, shapes, norm: Normalize = None, cmap='coolwarm',
                       label: str = None):
    """
    Signal sur les nœuds du réseau, représenté par la couleur des nœuds.
    Si label est donné, ajoute une barre de couleur avec ce titre.
    Renvoie le scatter, utilisable pour une barre commune : fig.colorbar(sc, ax=axes).
    """
    draw_graph(ax, grid, shapes)
    # Une nouvelle normalisation par appel : une CenteredNorm partagée garderait l'échelle du premier signal
    norm = CenteredNorm() if norm is None else norm
    sc = ax.scatter(grid.buses.x, grid.buses.y, c=grid.to_array(values), norm=norm, cmap=cmap,
                    s=2, zorder=2)
    if label is not None:
        ax.figure.colorbar(sc, ax=ax, label=label, shrink=0.6)
    return sc


def animate_graph_signals(grid, signals, shapes, norm: Normalize = None, cmap='coolwarm',
                          label: str = None, interval: int = 50, figsize=(8, 6)):
    """
    Animation d'un signal temporel sur les nœuds du réseau, représenté par la couleur des nœuds.

    Args:
        signals (pd.DataFrame): Bus x instants, comme renvoyé par Grid.step_response.
        norm: Normalisation commune à toutes les images. Par défaut, centrée sur 0
            avec pour demi-amplitude le 99e percentile de |signal| sur toute la durée
            (les valeurs au-delà saturent la couleur).
        label (str): Titre de la barre de couleur.
        interval (int): Durée d'une image (ms).

    Returns:
        FuncAnimation : dans un notebook, HTML(anim.to_jshtml()) ;
        dans un fichier, anim.save("oscillations.gif", writer="pillow").
    """
    values = np.column_stack([grid.to_array(signals[c]) for c in signals.columns])
    times = signals.columns.to_numpy()
    # 99e percentile : quelques nœuds extrêmes ne doivent pas écraser l'échelle
    norm = CenteredNorm(halfrange=np.percentile(np.abs(values), 99)) if norm is None else norm

    fig, ax = plt.subplots(figsize=figsize)
    sc = draw_graph_signals(ax, grid, values[:, 0], shapes, norm=norm, cmap=cmap, label=label)

    def update(i):
        sc.set_array(values[:, i])
        ax.set_title(f"t = {times[i]:.2f} s")
        return sc,

    anim = FuncAnimation(fig, update, frames=len(times), interval=interval)
    plt.close(fig)   # sinon le notebook affiche aussi une image fixe
    return anim


def draw_graph_signals_area(ax, grid, values, shapes):
    """Signal sur les nœuds du réseau, représenté par la surface des nœuds (proportionnelle à |valeur|)."""
    draw_graph(ax, grid, shapes)
    values = np.abs(grid.to_array(values))
    ax.scatter(grid.buses.x, grid.buses.y, s=100 * values / values.max(), zorder=2)
