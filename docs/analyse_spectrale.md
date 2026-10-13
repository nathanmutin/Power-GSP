# Analyse modale de la swing equation

On cherche à résoudre

```math
M\ddot\delta + L\delta = \Delta p, \qquad \delta(0) = \dot\delta(0) = 0
```

avec $`L = L(\theta^*)`$ et $`M = \text{diag}(m_i)`$, où l'inertie d'un nœud agrège celle de toutes les machines $`k`$ qui y sont raccordées :

```math
m_i = \frac{2}{\Omega_0}\sum_{k \in i} H_k s_k
```

Comme $`L`$ est symétrique réelle, on serait tenté de la diagonaliser, $`L = U\Lambda U^T`$, et de projeter sur ses vecteurs propres. Mais cela ne découple pas les équations : $`U^T M U`$ n'est pas diagonale, sauf si toutes les inerties sont égales ($`M \propto I`$). Il faut donc diagonaliser $`L`$ et $`M`$ simultanément. Pour cela, on s'occupe d'abord des nœuds sans inertie.

## Nœuds sans inertie : réduction de Kron

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

## Décomposition spectrale du laplacien réduit

On cherche à résoudre le problème aux valeurs propres généralisé

```math
L_{red}\, \delta = \lambda M_g \delta
```

Comme $`M_g`$ diagonale définie positive, on peut facilement la factoriser $`M_g = M_g^{1/2} M_g^{1/2}`$ et réécrire le problème comme un problème aux valeurs propres standard :

```math
\underbrace{M_g^{-1/2} L_{red} M_g^{-1/2}}_\text{laplacien normalisé}\underbrace{(M_g^{1/2} \delta)}_{eigenvector} = \lambda \underbrace{(M_g^{1/2} \delta)}_{eigenvector}
```

La matrice $`M_g^{-1/2} L_{red} M_g^{-1/2}`$ est toujours symétrique, semi-définie positive mais ses lignes ne sont plus de somme nulle.

Le théorème spectral assure que les valeurs propres sont réelles et positives (par positivité de $`M_g^{-1/2} L_{red} M_g^{-1/2}`$), et que les vecteurs propres sont orthogonaux. On peut donc choisir une base de vecteurs propres $`V`$ telle que :

```math
V^T V = I, \qquad M_g^{-1/2} L_{red} M_g^{-1/2} = V \Lambda V^T
```

Le réseau étant connexe, une seule valeur propre est nulle : $`\lambda_0 = 0`$, associée au vecteur $`v_0 \propto M_g^{1/2} \mathbb{1}`$ c'est-à-dire tel que pour tout $`i`$ : $`v_{0,i} = \sqrt{m_{g,i} / \sum_j m_{g,j}}`$.

## Découplage modal

On divise l'équation réduite par les inerties pour faire apparaître l'accélération angulaire imposée par la perturbation, $`a = M_g^{-1}\Delta p_{red} \space [\text{rad.s}^{-2}]`$ :

```math
\ddot\delta_g + M_g^{-1}L_{red}\,\delta_g = a
```

On passe en coordonnées modales en appliquant à tout vecteur nodal $`x`$ la même transformation :

```math
\hat x = V^T M_g^{1/2} \, x, \qquad x = M_g^{-1/2} V \hat x
```

Appliquée aux deux membres, avec $`V^T M_g^{1/2} M_g^{-1} L_{red} = V^T M_g^{-1/2} L_{red} = \Lambda V^T M_g^{1/2}`$, elle donne des oscillateurs indépendants :

```math
\ddot {\hat \delta}_k + \lambda_k \hat \delta_k = \hat a_k
```

Chaque mode $`k \geq 1`$ oscille à la pulsation $`\omega_k = \sqrt{\lambda_k}`$, soit à la fréquence

```math
f_k = \frac{\sqrt{\lambda_k}}{2\pi}
```

## Réponse à un échelon de puissance

Pour $`\Delta p`$ constant à partir de $`t = 0`$ et un réseau initialement à l'équilibre :

```math
\begin{aligned}
&\hat \delta_0(t) = \hat a_0 \, \frac{t^2}{2} \\
&\hat \delta_k(t) = \frac{\hat a_k}{\lambda_k}\left(1 - \cos\sqrt{\lambda_k} t\right), \qquad k \geq 1
\end{aligned}
```

On revient ensuite aux nœuds avec $`\delta_g = M_g^{-1/2} V \hat \delta`$, puis aux nœuds sans inertie avec la relation de Kron. L'écart de fréquence au nœud $`i`$ est

```math
\Delta f_i = \frac{1}{2\pi}\frac{d\delta_i}{dt}
```

Pour un nœud $`i`$ avec inertie :

```math
\begin{aligned}
\Delta f_i(t)
&= \frac{1}{2\pi}\sum_k \frac{v_{k, i}}{\sqrt{m_i}} \frac{d\hat \delta_k}{dt} \\
&= \frac{1}{2\pi} \left( \frac{\sum_j \Delta p_{red,j}}{\sum_j m_j} \, t + \sum_{k \geq 1} \frac{v_{k,i}}{\sqrt{m_i}} \frac{\hat a_k}{\sqrt{\lambda_k}}\sin\sqrt{\lambda_k} t \right)
\end{aligned}
```

car $`\hat a_0 = v_0^T M_g^{-1/2} \Delta p_{red} = \sum_j \sqrt{\frac{m_j}{\sum_l m_l}}\,\frac{\Delta p_{red,j}}{\sqrt{m_j}} = \frac{\sum_j \Delta p_{red,j}}{\sqrt{\sum_j m_j}}`$ et $`\frac{v_{0,i}}{\sqrt{m_i}} = \frac{1}{\sqrt{\sum_j m_j}}`$ pour tout $`i`$, d'où $`\frac{v_{0,i}}{\sqrt{m_i}}\,\hat a_0 = \frac{\sum_j \Delta p_{red,j}}{\sum_j m_j}`$ : la dérive du centre d'inertie, identique en tout nœud.
