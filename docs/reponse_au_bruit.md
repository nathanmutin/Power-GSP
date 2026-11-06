# Réponse du réseau électrique à un bruit blanc

## Modèle du bruit

On insère un bruit blanc stationnaire dans la puissance injectée à chaque nœud du réseau. Pour profiter de la décomposition modale, on suppose que le bruit est appliqué sur les nœuds avec inertie, indépendant pour chaque nœud, et dont la variance et proportionelle à l'inertie de chaque nœud :

```math
\Delta p_{red}(t)  \sim \mathcal{N}(0, \sigma^2 \, M_g)
```

## Réponse modale au bruit

Après décomposition modale, on obtient des oscillateurs indépendants :

```math
\ddot {\hat \delta}_k + 2 \zeta_k \omega_k \dot {\hat \delta}_k + \omega_k^2 \hat \delta_k = \hat a_k
```

et $`\hat a_k = v_k^T M_g^{1/2} a = v_k^T M_g^{-1/2} \Delta p_{red}`$.

Donc, la base $`(v_k)_k`$ étant orthonormée, on a $`\hat a_k \sim \mathcal{N}(0, (v_k^T M_g^{-1/2}) (\sigma^2 M_g) (M_g^{-1/2} v_k)) = \mathcal{N}(0, \sigma^2)`$.

Ainsi, chaque oscillateur est soumis à un bruit blanc stationnaire de même variance $`\sigma^2`$.

On peut alors utiliser les résultats de [la section précédente](./white_noise.md) pour calculer la variance de $`\hat \delta_k`$ et de $`\dot {\hat \delta}_k`$.

En effet on peut réécrire l'équation de l'oscillateur sous la forme d'un système du premier ordre :

```math
\begin{aligned}
\begin{bmatrix}
\dot {\hat \delta}_k \\
\ddot {\hat \delta}_k
\end{bmatrix}
=
\underbrace{
\begin{bmatrix}
0 & 1 \\
-\omega_k^2 & -2 \zeta_k \omega_k
\end{bmatrix}
}_{A_k}
\begin{bmatrix}
\hat \delta_k \\
\dot {\hat \delta}_k
\end{bmatrix}
+
\underbrace{
\begin{bmatrix}
0 \\
\hat a_k
\end{bmatrix}
}_{\xi_k(t)}
\end{aligned}
```

avec $`\xi_k (t) \sim \mathcal{N}(0, \begin{bmatrix} 0 & 0 \\ 0 & \sigma^2 \end{bmatrix})`$

L'équation de Lyapunov pour la matrice de covariance $`P_k = \mathbb{E}[\begin{bmatrix} \hat \delta_k \\ \dot {\hat \delta}_k \end{bmatrix} \begin{bmatrix} \hat \delta_k & \dot {\hat \delta}_k \end{bmatrix}]`$ est alors :

```math
A_k P_k + P_k A_k^T + Q_k = 0
```

la première équation scalaire (la première ligne et la première colonne) donne
$`\mathbb{E}[\hat \delta_k \dot {\hat \delta}_k] = 0`$,
la matrice $`P_k`$ est donc diagonale.

l'équation correspondant à la deuxième ligne et la deuxième colonne donne :

```math
-2 \zeta_k \omega_k \mathbb{E}[\dot{\hat \delta_k}^2] -2 \zeta_k \omega_k \mathbb{E}[\dot{\hat \delta_k}^2] + \sigma^2 = 0
```

d'où on obtient la variance de $`\dot {\hat \delta}_k`$ :

```math
\mathbb{E}[\dot{\hat \delta_k}^2] = \frac{\sigma^2}{4 \zeta_k \omega_k}
```

puis l'équation correspondant à la première ligne et la deuxième colonne donne :

```math
\mathbb{E}[\dot{\hat \delta_k}^2] - \omega_k^2 \mathbb{E}[\hat{\delta_k}^2] = 0
```

d'où on obtient la variance de $`\hat {\delta}_k`$ :

```math
\mathbb{E}[\hat{\delta_k}^2] = \frac{\sigma^2}{4 \zeta_k \omega_k^3}
```