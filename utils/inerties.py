"""
Constantes d'inertie pour différentes technologies de production d'énergie.
et une fonction pour obtenir la constante d'inertie H pour une technologie
et un type de combustible donnés.
"""

# https://eepublicdownloads.entsoe.eu/clean-documents/SOC%20documents/Inertia%20and%20RoCoF_v17_clean.pdf
INERTIA_CONSTANTS = {
    "nuclear": 5.9,
    "lignite": 3.8,
    "peat": 3.8,
    "hard_coal": 4.2,
    "gas": 4.2,
    "coal-derived_gas": 4.2,
    "oil": 4.3,
    "oil_shale": 4.3,
    "hydro_run_of_river": 2.7,
    "hydro_reservoir": 3.7,
    "hydro_pumped_storage": 3.5,
    "wind_onshore": 0.0,
    "wind_offshore": 0.0,
    "solar": 0.0,
    "other_renewable": 3.5,
    "geothermal": 3.5,
    "waste": 3.8,
    "marine": 3.8,
    "biomass": 3.3,
    "other": 3.8,
    # Hors document ENTSO-E : raccordées par onduleur, pas d'inertie synchrone
    "battery": 0.0,
    # Hors document ENTSO-E : solaire thermodynamique, turbine à vapeur synchrone
    "solar_thermal": 3.8,
}

# Correspondance entre les colonnes Technology et Fueltype du fichier powerplants.csv et les clés du dictionnaire INERTIA_CONSTANTS
TECHNOLOGY_FUELTYPE_MAPPING = {
    "Onshore_Wind": "wind_onshore",
    "PV_Solar": "solar",
    "Combustion Engine_Bioenergy": "biomass",
    "OCGT_Natural Gas": "gas",
    "Combustion Engine_Oil": "oil",
    "Run-Of-River_Hydro": "hydro_run_of_river",
    "Offshore_Wind": "wind_offshore",
    "Reservoir_Hydro": "hydro_reservoir",
    "Li_Battery": "battery",
    "CCGT_Natural Gas": "gas",
    "Pumped Storage_Hydro": "hydro_pumped_storage",
    "Steam Turbine_Waste": "waste",
    "Steam Turbine_Bioenergy": "biomass",
    "Steam Turbine_Nuclear": "nuclear",
    "Steam Turbine_Other": "other",
    "Steam Turbine_Lignite": "lignite",
    "Steam Turbine_Oil": "oil",
    "Steam Turbine_Hard Coal": "hard_coal",
    "Combustion Engine_Waste": "waste",
    "Pb_Battery": "battery",
    "Steam Turbine_Geothermal": "geothermal",
    "Csp_Solar": "solar_thermal",
    "Molten Salt_Heat Storage": "solar_thermal",
    "CSP_Solar": "solar_thermal",
    "NiCd_Battery": "battery",
    "NaS_Battery": "battery",
    "V_Battery": "battery",
    "NaNiCl_Battery": "battery",
    "Reservoir_Solar": "solar",
    "Combustion Engine_Other": "other",
    "Li_Bioenergy": "battery",
    "CAES_Mechanical Storage": "other",
    "Li_Waste": "battery",
    "Steam Turbine_Solar": "solar_thermal",
    "nan_Hydro": "hydro_run_of_river",
    "nan_Waste": "waste",
    "nan_Bioenergy": "biomass",
    "nan_Hydogen": "other_renewable",
    "nan_Oil": "oil",
    "nan_Solar": "solar",
    "nan_Hard Coal": "hard_coal",
    "nan_Hydrogen Storage": "other_renewable",
    "nan_Heat Storage": "other_renewable",
    "nan_Lignite": "lignite",
    "nan_Wind": "wind_onshore",
    "nan_Other": "other",
    "nan_Battery": "battery",
    "nan_Mechanical Storage": "other",
}

def get_inertia_constant(technology, fueltype):
    """
    Retourne la constante d'inertie H pour une technologie et un type de combustible donnés.
    
    Args:
        technology (str): Technologie de production d'énergie.
        fueltype (str): Type de combustible utilisé.
    
    Returns:
        float: Constante d'inertie H correspondante.
    """
    key = TECHNOLOGY_FUELTYPE_MAPPING.get(f"{technology}_{fueltype}")
    if key is None:
        print(f"Technologie ou type de combustible inconnu : {technology}_{fueltype}. Utilisation de la valeur par défaut.")
        return INERTIA_CONSTANTS["other"]
        
    return INERTIA_CONSTANTS[key]