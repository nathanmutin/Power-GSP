# Modèle dynamique du réseau électrique

## Modélisation

### Représentation du réseau

On considère un nœud $`i`$ connecté à ses voisins $`j`$, avec :
- admittances de ligne $`\underline{Y}_{ij} \space [\Omega^{-1}]`$
- admittance à la terre $`\underline{Y}_{i0} \space [\Omega^{-1}]`$
- courant injecté au nœud (production ou consommation) $`\underline{I}_i \space [A]`$
- tension au nœud $`\underline{V}_i = \mathcal{V}_i e^{j\theta_i} \space [V]`$

Loi des nœuds, le courant injecté est :

```math
\underline{I}_i = \underline{I}_{i0} + \sum_{j\neq i} \underline{I}_{ij}
```

avec

```math
\begin{aligned}
&\underline{I}_{i0}=(\underline{V}_i - 0) \underline{Y}_{i0} \\
&\underline{I}_{ij}=(\underline{V}_i-\underline{V}_j)\underline{Y}_{ij}
\end{aligned}
```

Ainsi

```math
\underline{I}_i = \left(\underline{Y}_{i0} + \sum_{j\neq i} \underline{Y}_{ij}\right)\underline{V}_i - \sum_{j\neq i} \underline{Y}_{ij}\underline{V}_j
```

#### Simplification et notation matricielle
On suppose que les pertes dans les lignes sont négligeables, ainsi $`\underline{Y}_{ij} = - j \frac{1}{X_{ij}}`$ avec $`X_{ij}`$ la réactance de ligne, et $`\underline{Y}_{i0} = j B_{i0}`$ avec $`B_{i0}`$ la susceptance shunt au nœud (positive, car essentiellement due à la capacité des lignes par rapport à la terre). Ainsi

```math
[I]=[Y][V]
```

avec

```math
[Y]_{ii}= j \space \underbrace{\left(B_{i0}-\sum_{j\neq i} \frac{1}{X_{ij}}\right)}_{= B_{ii}}, \qquad [Y]_{ij}=j \space \underbrace{\frac{1}{X_{ij}}}_{= B_{ij}}
```

### Puissance injectée

La puissance apparente injectée au nœud $`i`$ vaut:

```math
\underline{S}_i = P_i + j Q_i= \underline{V}_i \underline{I}_i^*
```

donc

```math
\begin{aligned}
P_i
&= \text{Re}\Big( \underline{V}_i \underline{I}_i^* \Big) \\
&= \text{Re}\Big( \underline{V}_i \left( \sum_{j} [Y]_{ij}^* \underline{V}_j^* \right) \Big) \\
&= \sum_{j}\text{Re}\Big( [Y]_{ij}^* \underline{V}_i \underline{V}_j^* \Big) \\
&= \sum_{j}\text{Re}\Big(- j B_{ij} \mathcal{V}_i \mathcal{V}_j e^{j(\theta_i - \theta_j)} \Big) \\
&= \sum_j \mathcal{V}_i \mathcal{V}_j B_{ij}\sin(\theta_i-\theta_j)
\end{aligned}
```

### Grandeurs per unit

Pour modéliser l'ensemble du réseau, on ramène chaque grandeur électrique à une grandeur sans dimension (per unit) en prenant pour référence les grandeurs nominales de chaque sous-système (ligne, transformateur, générateur).

Dans PyPSA, le "base power" est commun à tout le système et vaut $`S_b = 1 \space MVA`$ ([doc PyPSA](https://docs.pypsa.org/v0.34.0/user-guide/design.html#unit-conventions))
La "base tension" dépend, elle, du sous-système considéré. Par exemple, pour une ligne très haute tension on peut prendre $`V_b = 380 \space kV`$, de telle sorte que sa réactance en per unit sera :

```math
x_{pu} = \frac{S_b}{V_b^2} X
```

Pour la suite, on essaie de se tenir à la règle suivante : les grandeurs en unités physiques sont en majuscules et celles exprimées en per unit sont en minuscules.

Travailler en grandeurs per unit permet de s'affranchir des conversions de part et d'autre des transformateurs. Ainsi, une résistance de $`0.1 \text{ pu}`$ dissipera la même puissance qu'elle soit en haute ou basse tension, ce qui n'est pas le cas lorsque l'on raisonne en ohms.

Exprimée en per unit, la puissance réelle injectée au nœud $`i`$ est :

```math
p_i = \sum_j v_i v_j b_{ij}\sin(\theta_i-\theta_j)
```

### Nœuds générateurs

On part de la seconde loi de Newton appliquée à une machine tournante

```math
\frac{d E_K}{dt}=P_m-P_e
```

avec :
- $`E_K = \frac{1}{2} J \Omega_m^2`$ : l'énergie cinétique de rotation
- $`P_m`$ : puissance mécanique
- $`P_e`$ : puissance électrique

On s'intéresse aux déviations de la vitesse de rotation par rapport à la vitesse nominale $`\Omega_{m0} = \frac{\Omega_0}{p} = \frac{2\pi \times 50 \text{ Hz}}{p}`$ où $`p`$ est le nombre de paires de pôles du générateur. Ainsi il est intéressant de poser

```math
\Omega_m = \Omega_{m0} + \frac{d\theta_{m}}{dt} \quad \text{avec} \quad |\frac{d\theta_{m}}{dt}| \ll \Omega_{m0}
```

alors

```math
\begin{aligned}
\frac{d E_K}{dt}
&= J \Omega_m \frac{d \Omega_m}{dt} \\
&\approx J \Omega_{m0} \frac{d^2 \theta_{m}}{dt^2}
\end{aligned}
```

Pour faire apparaître le déphasage électrique $`\theta`$ on remarque que $`\theta = p \theta_m = \frac{\Omega_0}{\Omega_{m0}} \theta_m`$ 

```math
\frac{d E_K}{dt}
\approx \frac{J \Omega_{m0}^2}{\Omega_{0}} \frac{d^2 \theta}{dt^2} = \frac{2 H S}{\Omega_{0}} \frac{d^2 \theta}{dt^2}
```

Avec $`H = \frac{E_K}{S} = \frac{J \Omega_{m0}^2}{2S} \space [s]`$ le coefficient d'inertie du générateur qui varie de 0 à 6 secondes selon la technologie ([voir Table 1](https://eepublicdownloads.entsoe.eu/clean-documents/SOC%20documents/Inertia%20and%20RoCoF_v17_clean.pdf)).

Pour travailler en grandeurs per unit on divise par la puissance de base $`S_b = 1 \space MVA`$

```math
\frac{2 H s}{\Omega_{0}} \frac{d^2 \theta}{dt^2} = p_m - p_e \quad \text{(per unit)}
```

La puissance électrique $`p_e`$ fournie par la machine au réseau n'est autre que la puissance injectée $`p_i`$ qui, sous l'hypothèse classique $`v_i\simeq v_j\simeq 1 \text{ pu}`$, vaut :

```math
p_{e} = p_{i} \approx \sum_j b_{ij}\sin(\theta_i-\theta_j)
```

La puissance mécanique est, elle, fixée par l'opérateur de la centrale, on considèrera pour ce modèle qu'elle reste constante. On obtient alors pour équation

```math
\frac{2 H s}{\Omega_{0}} \frac{d^2 \theta}{dt^2} + \sum_j b_{ij}\sin(\theta_i-\theta_j) = p_{m}
```

### Nœuds de charge

Pour l'instant, on ne modélise pas leur dynamique.

## Linéarisation

On suppose un fonctionnement en régime permanent $`\theta_i^*`$, $`p_i^*`$ perturbé au temps $`t = 0`$ par la perte de puissance sur certains générateurs $`p_{m}(t) = p_{m}^* + \mathbb{1}_{t>0}\Delta p`$

Autour du point de fonctionnement :

```math
\theta_i(t)=\theta_i^*+\delta_i(t)
```

On obtient

```math
\frac{2 H_{i} s_{i}}{\Omega_{0}}\frac{d^2 \delta_{i}}{dt^2}
+ \sum_j b_{ij}\cos(\theta_i^*-\theta_j^*)(\delta_i-\delta_j)
= \Delta p_i
```

### Laplacien linéarisé

Remarquons que le terme $`j = i`$ de la somme est nul, on peut donc s'en passer et réécrire la somme sous forme matricielle avec le laplacien $`L(\theta^*)`$ défini par :

```math
\begin{aligned}
&L_{ii}=\sum_{j\neq i} b_{ij}\cos(\theta_i^*-\theta_j^*) \\
&L_{ij}=-b_{ij}\cos(\theta_i^*-\theta_j^*)
\end{aligned}
```

et introduire la matrice diagonale des inerties $`M = \text{diag}\left(\frac{2 H_i s_i}{\Omega_0}\right)  [rad^{-1}.s^2]`$.


Ainsi :

```math
M\ddot\delta+ L(\theta^*)\delta = \Delta p
```
