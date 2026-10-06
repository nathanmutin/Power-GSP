# Power Grid Signal Processing

## Organization du code

| Dossier | Contenu |
|---------|---------|
| `pypsa-eur` | Clone de pypsa-eur |
| `pypsa-eur/resources`  | Données téléchargées depuis pypsa-eur |
| `config` | Fichiers de configuration pour le télécargement des données |
| `doc.md` | Aspect théorique du modèle |
| `run.ipynb` | Notebook pour exécuter le modèle |
| `utils` | Fonctions utilitaires pour le traitement des données |


## Installation (Windows)

```bash
winget install prefix-dev.pixi
git submodule update --init --recursive
cd pypsa-eur
pixi install -e dev
```

Dans VS Code, choisir le noyau `pypsa-eur\.pixi\envs\dev\python.exe` pour les notebooks.

## Téléchargement des données

```bash
cd pypsa-eur
cp ../config/build_powerplants.py scripts/build_powerplants.py
pixi run -e dev snakemake --cores 4 resources/power_gsp/networks/base.nc  resources/power_gsp/powerplants.csv --configfile ../config/pypsa-eur.yaml
```
