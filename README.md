# Power Grid Signal Processing

## Organization du code

| Dossier | Contenu |
|---------|---------|
| `pypsa-eur` | Clone de pypsa-eur |
| `pypsa-eur/resources`  | Données téléchargées depuis pypsa-eur |
| `config` | Fichiers de configuration pour le télécargement des données |
| `docs` | Aspects théoriques |
| `run.ipynb` | Notebook pour exécuter le modèle |
| `utils` | Fonctions utilitaires pour le traitement des données |

## Documentation

À lire dans l'ordre :

| Document | Contenu |
|----------|---------|
| [Modèle dynamique du réseau](docs/power_grid_model.md) | Représentation du réseau, puissance injectée, grandeurs per unit, équation d'oscillation des générateurs, linéarisation |
| [Analyse spectrale](docs/analyse_spectrale.md) | Réduction de Kron, laplacien normalisé par l'inertie, découplage modal, réponse à un échelon |
| [Perturbation d'un laplacien](docs/laplacian_perturbation.md) | Développement en perturbation des valeurs et vecteurs propres de L₀ + εL₁ |
| [Perturbation optimale du laplacien](docs/optimal_perturbation.md) | Recherche de la perturbation qui  minimise l'importance des oscillations |


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
