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

Avec $`H = \frac{E_K}{S} = \frac{J \Omega_{m0}^2}{2S}`$ le coefficient d'inertie du générateur qui varie de 0 à 6 selon la technologie ([voir Figure 1](https://eepublicdownloads.entsoe.eu/clean-documents/SOC%20documents/Inertia%20and%20RoCoF_v17_clean.pdf)).

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

Ainsi :

```math
M\ddot\delta+ L(\theta^*)\delta = \Delta p
```

## Analyse modale

On cherche à résoudre

```math
M\ddot\delta + L\delta = \Delta p, \qquad \delta(0) = \dot\delta(0) = 0
```

avec $`L = L(\theta^*)`$ et $`M = \text{diag}(m_i)`$, où l'inertie d'un nœud agrège celle de toutes les machines $`k`$ qui y sont raccordées :

```math
m_i = \frac{2}{\Omega_0}\sum_{k \in i} H_k s_k
```

Comme $`L`$ est symétrique réelle, on serait tenté de la diagonaliser, $`L = U\Lambda U^T`$, et de projeter sur ses vecteurs propres. Mais cela ne découple pas les équations : $`U^T M U`$ n'est pas diagonale, sauf si toutes les inerties sont égales ($`M \propto I`$). Il faut donc diagonaliser $`L`$ et $`M`$ simultanément. Pour cela, on s'occupe d'abord des nœuds sans inertie.

### Nœuds sans inertie : réduction de Kron

Les nœuds de charge, ainsi que les nœuds dont la production passe uniquement par de l'électronique de puissance (éolien, solaire, batteries), ont $`m_i = 0`$. Leur équation n'a pas de terme dynamique : elle devient une contrainte algébrique. On sépare les nœuds en deux groupes, avec inertie ($`g`$) et sans inertie ($`l`$) :

```math
\begin{pmatrix} M_g & 0 \\ 0 & 0 \end{pmatrix}
\begin{pmatrix} \ddot\delta_g \\ \ddot\delta_l \end{pmatrix}
+
\begin{pmatrix} L_{gg} & L_{gl} \\ L_{lg} & L_{ll} \end{pmatrix}
\begin{pmatrix} \delta_g \\ \delta_l \end{pmatrix}
=
\begin{pmatrix} \Delta p_g \\ \Delta p_l \end{pmatrix}
```

Les dernières lignes donnent les angles des nœuds sans inertie en fonction des autres :

```math
\delta_l = L_{ll}^{-1}\left(\Delta p_l - L_{lg}\delta_g\right)
```

$`L_{ll}`$ est inversible pour un réseau connexe ([idée de preuve ici](https://www.youtube.com/watch?v=AnnZypKlhjg)). En reportant dans la première ligne :

```math
M_g\ddot\delta_g + L_{red}\,\delta_g = \Delta p_{red}
```

avec

```math
\begin{aligned}
&L_{red} &&= L_{gg} - L_{gl}L_{ll}^{-1}L_{lg} \\
&\Delta p_{red} &&= \Delta p_g - L_{gl}L_{ll}^{-1}\Delta p_l
\end{aligned}
```

$`L_{red}`$ (complément de Schur de $`L_{ll}`$ dans $`L`$) est encore un laplacien : symétrique, semi-définie positive, de lignes de somme nulle. Elle décrit un réseau équivalent ne contenant que les nœuds avec inertie (Kron reduction du graphe).

Voir [Kron Reduction of Graphs with Applications to Electrical Networks](http://arxiv.org/abs/1102.2950)

### Problème aux valeurs propres généralisé

On résout

```math
L_{red}\, v_k = \lambda_k M_g v_k
```

Comme $`L_{red}`$ est symétrique et $`M_g`$ diagonale définie positive, les valeurs propres $`\lambda_k`$ sont réelles et positives, et les vecteurs propres peuvent être choisis $`M_g`$-orthonormés. En notant $`V = (v_0, v_1, \dots)`$ et $`\Lambda = \text{diag}(\lambda_k)`$ :

```math
V^T M_g V = I, \qquad V^T L_{red} V = \Lambda
```

Le réseau étant connexe, une seule valeur propre est nulle : $`\lambda_0 = 0`$, associée au vecteur uniforme $`v_0 = \mathbb{1}/\sqrt{\sum_g m_g}`$.

### Coordonnées modales

On divise l'équation réduite par les inerties pour faire apparaître l'accélération angulaire imposée par la perturbation, $`a = M_g^{-1}\Delta p_{red} \space [\text{rad/s}^2]`$ :

```math
\ddot\delta_g + M_g^{-1}L_{red}\,\delta_g = a
```

On passe en coordonnées modales en appliquant à tout vecteur nodal $`x`$ la même transformation :

```math
\hat x = V^T M_g\, x, \qquad x = V \hat x \qquad (\text{car } V^{-1} = V^T M_g)
```

Appliquée aux deux membres, avec $`V^T M_g M_g^{-1} L_{red} V = V^T L_{red} V = \Lambda`$, elle donne des oscillateurs indépendants :

```math
\ddot {\hat \delta}_k + \lambda_k \hat \delta_k = \hat a_k, \qquad \hat a = V^T M_g\, a = V^T \Delta p_{red}
```

Chaque mode $`k \geq 1`$ oscille à la pulsation $`\omega_k = \sqrt{\lambda_k}`$, soit à la fréquence

```math
f_k = \frac{\sqrt{\lambda_k}}{2\pi}
```

### Réponse à un échelon de puissance

Pour $`\Delta p`$ constant à partir de $`t = 0`$ et un réseau initialement à l'équilibre :

```math
\begin{aligned}
&\hat \delta_0(t) = \hat a_0 \, \frac{t^2}{2} \\
&\hat \delta_k(t) = \frac{\hat a_k}{\lambda_k}\left(1 - \cos\sqrt{\lambda_k} t\right), \qquad k \geq 1
\end{aligned}
```

On revient ensuite aux nœuds avec $`\delta_g = V \hat \delta`$, puis aux nœuds sans inertie avec la relation de Kron. L'écart de fréquence au nœud $`i`$ est

```math
\Delta f_i = \frac{1}{2\pi}\frac{d\delta_i}{dt}
```

Pour un nœud générateur $`g`$ :

```math
\begin{aligned}
\Delta f_g(t)
&= \frac{1}{2\pi}\sum_k v_{gk} \frac{d\hat \delta_k}{dt} \\
&= \frac{1}{2\pi} \left( v_{g0} \, \hat a_0 \, t + \sum_{k \geq 1} v_{gk} \frac{\hat a_k}{\sqrt{\lambda_k}}\sin\sqrt{\lambda_k} t \right)
\end{aligned}
```
