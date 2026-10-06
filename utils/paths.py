"""Chemins du projet : sorties du workflow PyPSA-Eur (run power_gsp)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "pypsa-eur" / "resources" / "power_gsp"
NETWORKS = RESOURCES / "networks"

BASE_NETWORK = NETWORKS / "base.nc"
BASE_EXTENDED_NETWORK = NETWORKS / "base_extended.nc"
SIMPLIFIED_NETWORK = NETWORKS / "simplified.nc"
CLUSTERED_NETWORK = NETWORKS / "clustered.nc"

COUNTRY_SHAPES = RESOURCES / "country_shapes.geojson"

BUSMAP_SIMPLIFY_NETWORK = RESOURCES / "busmap_simplify_network.csv"
BUSMAP_CLUSTER_NETWORK = RESOURCES / "busmap_cluster_network.csv"
POWERPLANTS = RESOURCES / "powerplants.csv"