# Réponse du réseau électrique à un bruit blanc

## Modèle du bruit

On insère un bruit blanc stationnaire dans la puissance injectée à chaque nœud du réseau. Pour profiter de la décomposition modale, on suppose que le bruit est appliqué sur les nœuds avec inertie, indépendant pour chaque nœud, et d'intensité proportionnelle à l'inertie de chaque nœud :

```math
\mathbb{E}[\Delta p_{red}(t) \, \Delta p_{red}(t')^T] = \sigma^2 M_g \, \delta(t-t')
```

Le bruit aux temps $`t`$ et $`t'`$ est donc indépendant si $`t \neq t'`$.

## Réponse modale au bruit

Après décomposition modale, on obtient des oscillateurs indépendants :

```math
\ddot {\hat \delta}_k + 2 \zeta_k \omega_k \dot {\hat \delta}_k + \omega_k^2 \hat \delta_k = \hat a_k
```

et $`\hat a = V^T M_g^{1/2} a = V^T M_g^{-1/2} \Delta p_{red}`$.

Donc, la base $`(v_k)_k`$ étant orthonormée :

```math
\mathbb{E}[\hat a(t) \, \hat a(t')^T] = (V^T M_g^{-1/2}) (\sigma^2 M_g) (M_g^{-1/2} V) \, \delta(t-t') = \sigma^2 I \, \delta(t-t')
```

Ainsi, chaque oscillateur est soumis à un bruit blanc gaussien stationnaire de même intensité $`\sigma^2`$. De plus, chaque bruit $`\hat a_k`$ est indépendant des autres.

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

avec $`\mathbb{E}[\xi_k(t) \, \xi_k(t')^T] = Q_k \, \delta(t-t')`$ et $`Q_k = \begin{bmatrix} 0 & 0 \\ 0 & \sigma^2 \end{bmatrix}`$.

L'équation de Lyapunov pour la matrice de covariance $`P_k = \mathbb{E}[\begin{bmatrix} \hat \delta_k \\ \dot {\hat \delta}_k \end{bmatrix} \begin{bmatrix} \hat \delta_k & \dot {\hat \delta}_k \end{bmatrix}]`$ est alors :

```math
A_k P_k + P_k A_k^T + Q_k = 0
```

La première équation scalaire (première ligne, première colonne) donne
$`\mathbb{E}[\hat \delta_k \dot {\hat \delta}_k] = 0`$ :
la matrice $`P_k`$ est donc diagonale.

L'équation correspondant à la deuxième ligne et la deuxième colonne donne, les termes en $`\mathbb{E}[\hat \delta_k \dot {\hat \delta}_k]`$ étant nuls :

```math
-2 \zeta_k \omega_k \mathbb{E}[\dot{\hat \delta}_k^2] -2 \zeta_k \omega_k \mathbb{E}[\dot{\hat \delta}_k^2] + \sigma^2 = 0
```

d'où on obtient la variance de $`\dot {\hat \delta}_k`$ :

```math
\mathbb{E}[\dot{\hat \delta}_k^2] = \frac{\sigma^2}{4 \zeta_k \omega_k}
```

Puis l'équation correspondant à la première ligne et la deuxième colonne donne, pour la même raison :

```math
\mathbb{E}[\dot{\hat \delta}_k^2] - \omega_k^2 \mathbb{E}[\hat{\delta}_k^2] = 0
```

d'où on obtient la variance de $`\hat {\delta}_k`$ :

```math
\mathbb{E}[\hat{\delta}_k^2] = \frac{\sigma^2}{4 \zeta_k \omega_k^3}
```

Ce résultat est valable pour tout $`\zeta_k > 0`$, y compris en régime sur-amorti ; pour $`\zeta_k = 0`$, la variance est infinie. Le régime stationnaire s'établit en un temps de l'ordre de $`1/(\zeta_k \omega_k)`$.

De plus, les oscillateurs étant indépendants, on a $`\mathbb{E}[\hat{\delta}_k\hat{\delta}_l] = 0`$ et $`\mathbb{E}[\dot{\hat{\delta}}_k\dot{\hat{\delta}}_l] = 0`$ pour $`k \neq l`$.

Le mode 0 ($`\omega_0 = 0`$) n'a pas de régime stationnaire. Les sommes qui suivent portent donc sur $`k \geq 1`$.

## Capacité des lignes

Étudions maintenant la conséquence de ce bruit sur les lignes du réseau. La capacité d'une ligne est limitée thermiquement par le courant qui la traverse. Avec les hypothèses de pertes négligeables, de tension constante et de shunt négligeable, le transit de puissance active dans la ligne $`(i,j)`$ vaut :

```math
F_{ij} = b_{ij} \sin(\theta_i - \theta_j)
```

Le module du courant vaut $`2 b_{ij} |\sin((\theta_i - \theta_j)/2)|`$ : les deux coïncident au premier ordre, et on compare comme d'habitude le transit $`F_{ij}`$ à une capacité $`F_{ij}^{max}`$.

En utilisant la décomposition $`\theta_i = \theta_i^* + \delta_i`$, on obtient :

```math
\begin{aligned}
F_{ij} &= b_{ij} \sin(\theta_i^* - \theta_j^* + \delta_i - \delta_j) \\
&= b_{ij} \sin(\theta_i^* - \theta_j^*) \cos(\delta_i - \delta_j) + b_{ij} \cos(\theta_i^* - \theta_j^*) \sin(\delta_i - \delta_j) \\
&\approx F_{ij}^* + b_{ij} \cos(\theta_i^* - \theta_j^*) (\delta_i - \delta_j)
\end{aligned}
```

Ainsi, la variance de $`F_{ij}`$ vaut :

```math
\mathbb{E}[(F_{ij}-F_{ij}^*)^2] = b_{ij}^2 \cos^2(\theta_i^* - \theta_j^*) \mathbb{E}[(\delta_i - \delta_j)^2]
```

Décomposons $`\delta_i - \delta_j = \sum_{k \geq 1} (\Phi_{k,i} - \Phi_{k,j}) \hat{\delta}_k`$, où $`\Phi_k`$ est la forme en angle du mode $`k`$ : $`\Phi_k = M_g^{-1/2} v_k`$ sur les nœuds avec inertie, prolongée aux nœuds sans inertie par la relation de Kron. Le bruit n'étant appliqué qu'aux nœuds avec inertie, ce prolongement est exact. On obtient :

```math
\begin{aligned}
\mathbb{E}[(\delta_i - \delta_j)^2] &= \sum_{k \geq 1} (\Phi_{k,i} - \Phi_{k,j})^2 \mathbb{E}[\hat{\delta}_k^2] + \sum_{k\neq l} (\Phi_{k,i} - \Phi_{k,j})(\Phi_{l,i} - \Phi_{l,j}) \cancel{\mathbb{E}[\hat{\delta}_k\hat{\delta}_l]} \\
&= \sum_{k \geq 1} (\Phi_{k,i} - \Phi_{k,j})^2 \frac{\sigma^2}{4 \zeta_k \omega_k^3}
\end{aligned}
```

Soit $`K \in \mathbb{R}^{|lignes| \times |nœuds|}`$ la matrice d'incidence : $`K_{e,i} = 1`$ si le nœud $`i`$ est l'extrémité positive de la ligne $`e`$, $`K_{e,i} = -1`$ si le nœud $`i`$ est l'extrémité négative de la ligne $`e`$, et $`K_{e,i} = 0`$ sinon. On note $`K_e`$ la $`e`$-ième ligne de $`K`$ écrite en colonne. Pour la ligne $`e = (i,j)`$, on a $`\Phi_{k,i} - \Phi_{k,j} = (K \Phi_k)_e = K_e^T \Phi_k`$, puis

```math
\begin{aligned}
\mathbb{E}[(\delta_i - \delta_j)^2] &= \sum_{k \geq 1} (K_e^T \Phi_k)^2 \frac{\sigma^2}{4 \zeta_k \omega_k^3} \\
&= K_e^T \left( \sum_{k \geq 1} \frac{\sigma^2}{4 \zeta_k \omega_k^3} \Phi_k \Phi_k^T \right) K_e \\
\end{aligned}
```

Posons $`\Sigma_k = \frac{\sigma}{2 \sqrt{\zeta_k \omega_k^3}}`$, $`\Sigma = \text{diag}(\Sigma_1, \dots, \Sigma_{n_g - 1})`$ et $`\Phi = (\Phi_1, \dots, \Phi_{n_g - 1})`$ de taille $`|nœuds| \times (n_g - 1)`$, où $`n_g`$ est le nombre de nœuds avec inertie (un mode par nœud avec inertie, mode 0 exclu). Comme $`\sum_{k \geq 1} \Sigma_k^2 \Phi_k \Phi_k^T = \Phi \Sigma^2 \Phi^T`$, on obtient :

```math
\mathbb{E}[(\delta_i - \delta_j)^2] = K_e^T \Phi \Sigma^2 \Phi^T K_e
```

Avec $`c_e = b_{ij} \cos(\theta_i^* - \theta_j^*)`$ pour la ligne $`e = (i,j)`$, la variance du transit dans la ligne vaut donc :

```math
\mathbb{E}[(F_e-F_e^*)^2] = c_e^2 K_e^T \Phi \Sigma^2 \Phi^T K_e = (c_e K_e)^T \Phi \Sigma^2 \Phi^T (c_e K_e)
```

On obtient un résultat similaire pour la covariance entre deux lignes $`e`$ et $`f`$ :

```math
\mathbb{E}[(F_{e}-F_{e}^*)(F_{f}-F_{f}^*)] = (c_e K_e)^T \Phi \Sigma^2 \Phi^T (c_f K_f)
```

de telle sorte que, avec $`C = \text{diag}(c_e)`$, la matrice de covariance des transits dans les lignes est :

```math
\mathbb{E}[(F-F^*)(F-F^*)^T] = C K \Phi \Sigma^2 \Phi^T K^T C = (C K \Phi \Sigma)(C K \Phi \Sigma)^T
```

Les modes $`\Phi`$ sont ceux du réseau linéarisé autour de $`\theta^*`$, dont le laplacien a pour poids les $`c_e`$. À vide ($`\theta^* = 0`$), $`C = \text{diag}(b_e)`$.

La somme des variances des transits dans les lignes est la trace de cette matrice de covariance, soit $`{||C K \Phi \Sigma||_F}^2`$.

Enfin, si on veut étudier l'influence d'un mode particulier $`k`$ sur les transits, on peut considérer la matrice de covariance due à ce seul mode :

```math
\mathbb{E}[(F-F^*)(F-F^*)^T]_k = (C K \Phi_k \Sigma_k)(C K \Phi_k \Sigma_k)^T
```

Les modes étant indépendants, la matrice de covariance totale est exactement la somme de ces contributions.
