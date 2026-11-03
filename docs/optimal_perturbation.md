# Perturbation optimale du laplacien

On cherche à renforcer $`k`$ lignes du réseau, c'est-à-dire à augmenter leur susceptance $`b_\ell = 1/x_\ell`$ (donc à diminuer leur impédance), afin d'augmenter la pulsation du mode inter-zones le plus lent, $`\omega_1 = \sqrt{\lambda_1}`$.

## Pourquoi maximiser $`\lambda_1`$

Pour un échelon de puissance, le mode $`k`$ contribue à l'écart d'angle en $`\hat a_k / \lambda_k`$ et à l'écart de fréquence en $`\hat a_k / \sqrt{\lambda_k}`$ (voir [analyse spectrale](analyse_spectrale.md)). Augmenter $`\lambda_1`$ réduit donc l'amplitude du mode le plus lent. Le modèle étant sans amortissement, cela ne dit rien de son taux d'amortissement.

## Formulation

Le laplacien s'écrit $`L = B^T D B`$, où $`B`$ (lignes x nœuds) est la matrice d'incidence et $`D = \text{diag}(b)`$ contient les susceptances des lignes. Un renforcement $`d`$ (une composante par ligne, en MW/rad) donne :

```math
L(d) = B^T \text{diag}(b + d)\, B
```

Les pulsations au carré $`\lambda_k(d)`$ sont les valeurs propres de $`M_g^{-1/2} L_{red}(d)\, M_g^{-1/2}`$ (voir [analyse spectrale](analyse_spectrale.md)), et non celles de $`L(d)`$, qui ne tiennent pas compte des inerties et ne sont pas des pulsations. Le problème s'écrit :

```math
\begin{aligned}
&\text{maximiser } \lambda_1(d) \\
&\text{sous } \|d\|_0 \leq k, \qquad 0 \leq d_\ell \leq d_\ell^{max}
\end{aligned}
```

où $`\|d\|_0`$ est le nombre de lignes renforcées. La borne $`d^{max}`$ définit le type de renforcement : $`d_\ell^{max} = \beta`$ pour un même renfort absolu sur chaque ligne, $`d_\ell^{max} = b_\ell`$ pour un doublement de la ligne.

## Approximation au premier ordre

Si $`\lambda_1`$ est simple, sa dérivée par rapport à la susceptance d'une ligne est ([perturbation d'un laplacien](laplacian_perturbation.md)) :

```math
\frac{\partial \lambda_1}{\partial b_\ell} = \left( (B \Phi_1)_\ell \right)^2 = (\Phi_{i,1} - \Phi_{j,1})^2 \qquad \text{pour la ligne } \ell = (i, j)
```

où $`\Phi_1`$ est la forme en angle du mode 1 prolongée à tous les nœuds : $`\Phi_{g,1} = M_g^{-1/2} v_1`$ sur les nœuds avec inertie, $`\Phi_{l,1} = -L_{ll}^{-1} L_{lg} \Phi_{g,1}`$ sur les autres (`Grid.mode_shapes`). Cette formule vaut aussi pour les lignes reliées à des nœuds éliminés par la réduction de Kron. On a alors

```math
\lambda_1(d) \approx \lambda_1(0) + \sum_\ell d_\ell \,(B \Phi_1)_\ell^2
```

Chaque terme est positif et croissant en $`d_\ell`$ : à l'optimum, chaque ligne renforcée l'est au maximum, $`d_\ell = d_\ell^{max}`$, et la contrainte $`\|d\|_0 \leq k`$ retient les $`k`$ lignes de plus grand gain $`d_\ell^{max} (B \Phi_1)_\ell^2`$. Le classement dépend donc du type de renforcement : une ligne déjà forte, traversant la ligne de partage du mode, l'emporte pour un doublement.

## Validité de l'approximation

- Elle suppose $`\lambda_1`$ simple, et un renforcement petit devant l'écart $`\lambda_2 - \lambda_1`$. Si $`\lambda_1`$ croise $`\lambda_2`$, le mode le plus lent change de forme.
- Elle surestime toujours le gain. Pour une ligne entre deux nœuds avec inertie, de perturbation $`A_1 = M_g^{-1/2} L_1 M_g^{-1/2}`$, la correction d'ordre 2 vaut $`\sum_{j \geq 2} \frac{(v_j^T A_1 v_1)^2}{\lambda_1 - \lambda_j} \leq 0`$ (le terme $`j = 0`$ est nul car $`L_1 \mathbb{1} = 0`$).

## Version convexe

$`\lambda_1(d)`$ est le minimum du quotient de Rayleigh $`\delta^T L(d)\, \delta / \delta^T M \delta`$ sur les $`\delta`$ tels que $`\mathbb{1}^T M \delta = 0`$. C'est un minimum de fonctions affines de $`d`$, donc une fonction concave de $`d`$. En remplaçant la contrainte $`\|d\|_0 \leq k`$ par un budget, on obtient un problème convexe, qui s'écrit comme un programme semi-défini (Ghosh & Boyd, 2006) :

```math
\begin{aligned}
&\text{maximiser } t \\
&\text{sous } B^T \text{diag}(b + d)\, B \succeq t \left( M - \frac{M \mathbb{1} \mathbb{1}^T M}{\mathbb{1}^T M \mathbb{1}} \right), \qquad \sum_\ell d_\ell \leq \text{budget}, \qquad 0 \leq d_\ell \leq d_\ell^{max}
\end{aligned}
```

Il donne une borne supérieure sur le gain atteignable, qui permet de juger la solution gloutonne. Sa taille (nombre de nœuds) le rend coûteux sur le réseau complet : en pratique, on le résout sur une liste réduite de lignes candidates.

## Ressources

- A. Ghosh, S. Boyd, *Growing Well-Connected Graphs*, IEEE CDC 2006 : [lien](https://stanford.edu/~boyd/papers/growing_fast_graphs.html)
