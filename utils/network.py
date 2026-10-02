"""
Fonctions pour la gestion du réseau PyPSA.
"""

import pandas as pd
import pypsa

def remove_buses(n: pypsa.Network, buses: list) -> None:
    """
    Fonction bien utile pour retirer des nœuds du réseau,
    avec tous les composants qui y sont raccordés.
    """
    buses = pd.Index(buses)
    for component in n.components:
        static = component.static
        bus_columns = [c for c in static.columns if c == "bus" or (c.startswith("bus") and c[3:].isdigit())]
        if component.name == "Bus" or static.empty or not bus_columns:
            continue
        attached = static.index[static[bus_columns].isin(buses).any(axis=1)]
        if len(attached):
            n.remove(component.name, attached)
    n.remove("Bus", buses)
    
def remove_non_synchronous_areas(n: pypsa.Network) -> pypsa.Network:
    """
    Supprime les zones non synchrones par rapport au réseau continental européen dans un réseau PyPSA.

    Args:
        n (pypsa.Network): Réseau PyPSA.

    Returns:
        pypsa.Network: Réseau PyPSA sans les zones non synchrones.
    """
    n2 = n.copy()
    
    # Suppression des lignes HVDC
    dc_buses = n2.buses.query("carrier == 'DC'").index
    remove_buses(n2, dc_buses)
    
    # Identifier la zone principale du réseau (la plus grande composante connexe)
    n2.determine_network_topology()
    main = n2.buses.sub_network.value_counts().idxmax()
    
    # Supprimer les bus AC des zones non synchrones
    non_sync_buses = n2.buses[n2.buses.sub_network != main].index
    remove_buses(n2, non_sync_buses)

    return n2