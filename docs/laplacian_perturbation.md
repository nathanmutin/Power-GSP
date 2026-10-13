# Spectral decomposition of a perturbed laplacian matrix

Consider a laplacian matrix $`L_0`$ and a perturbation $`L_1`$ such that

```math
L_\epsilon = L_0 + \epsilon L_1
```

is still a laplacian matrix.

The goal is to find the eigenvalues and eigenvectors of $`L_\epsilon`$, given the eigenvalues and eigenvectors of $`L_0`$ and $`L_1`$.

## Spectral decomposition of $`L_0`$ and $`L_1`$

$`L_0`$ and $`L_1`$ are real symmetric matrices, so they can be diagonalized as

```math
\begin{aligned}
L_0 V_0 &= V_0 \Lambda_0 \\
L_1 V_1 &= V_1 \Lambda_1
\end{aligned}
```

where $`V_0`$ and $`V_1`$ are orthogonal matrices containing the eigenvectors of $`L_0`$ and $`L_1`$, respectively, and $`\Lambda_0`$ and $`\Lambda_1`$ are diagonal matrices containing the corresponding eigenvalues.

## Expansion of eigenvalues and eigenvectors

We can expand the eigenvalues and eigenvectors of $`L_\epsilon`$ in a power series in $`\epsilon`$:

```math
\begin{aligned}
&L_\epsilon V_\epsilon = V_\epsilon \Lambda_\epsilon \\
&\text{where} \\
&\Lambda_\epsilon = \Lambda_\epsilon^{(0)} + \epsilon \Lambda_\epsilon^{(1)} + \epsilon^2 \Lambda_\epsilon^{(2)} + \dots \\
&V_\epsilon = V_\epsilon^{(0)} + \epsilon V_\epsilon^{(1)} + \epsilon^2 V_\epsilon^{(2)} + \dots
\end{aligned}
```

Expanding the equation $`L_\epsilon V_\epsilon = V_\epsilon \Lambda_\epsilon`$ and collecting terms of the same order in $`\epsilon`$, we can derive equations for the coefficients $`\Lambda_\epsilon^{(n)}`$ and $`V_\epsilon^{(n)}`$.

```math
\begin{aligned}
&\text{order } \epsilon^0:
L_0 V_\epsilon^{(0)}
&&= V_\epsilon^{(0)} \Lambda_\epsilon^{(0)} \\

&\text{order } \epsilon^1:
L_0 V_\epsilon^{(1)} + L_1 V_\epsilon^{(0)}
&&= V_\epsilon^{(0)} \Lambda_\epsilon^{(1)} + V_\epsilon^{(1)} \Lambda_\epsilon^{(0)} \\

&\text{order } \epsilon^2:
L_0 V_\epsilon^{(2)} + L_1 V_\epsilon^{(1)}
&&= V_\epsilon^{(0)} \Lambda_\epsilon^{(2)} + V_\epsilon^{(1)} \Lambda_\epsilon^{(1)} + V_\epsilon^{(2)} \Lambda_\epsilon^{(0)} \\

&\dots \\

&\text{order } \epsilon^n:
L_0 V_\epsilon^{(n)} + L_1 V_\epsilon^{(n-1)}
&&= \sum_{k=0}^n V_\epsilon^{(k)} \Lambda_\epsilon^{(n-k)} \\
\end{aligned}
```

The same procedure can be applied to the equation $`V_\epsilon^T V_\epsilon = I`$ to obtain equations for the coefficients $`V_\epsilon^{(n)}`$.

```math
\begin{aligned}
&\text{order } \epsilon^0:
I = V_\epsilon^{(0)T} V_\epsilon^{(0)} \\
&\text{order } \epsilon^1:
0 = V_\epsilon^{(0)T} V_\epsilon^{(1)} + V_\epsilon^{(1)T} V_\epsilon^{(0)} \\
&\dots \\
&\text{order } \epsilon^n:
0 = \sum_{k=0}^n V_\epsilon^{(k)T} V_\epsilon^{(n-k)} \\
\end{aligned}
```

## Order 0

At order $\epsilon^0$, the equations simplify to:

```math
\begin{aligned}
&L_0 V_\epsilon^{(0)} = V_\epsilon^{(0)} \Lambda_\epsilon^{(0)} \\
&I = V_\epsilon^{(0)T} V_\epsilon^{(0)}
\end{aligned}
```

the solutions are the eigenvalues and eigenvectors of $`L_0`$:

```math
\begin{aligned}
&\Lambda_\epsilon^{(0)} = \Lambda_0 \\
&V_\epsilon^{(0)} = V_0
\end{aligned}
```

The eigenvalues and eigenvectors of $`L_\epsilon`$ are obviously perturbations of the eigenvalues and eigenvectors of $`L_0`$.

## Order 1

At order $\epsilon^1$, the equations become:

```math
\begin{aligned}
&L_0 V_\epsilon^{(1)} + L_1 V_0 = V_0 \Lambda_\epsilon^{(1)} + V_\epsilon^{(1)} \Lambda_0 \\
&0 = V_0^T V_\epsilon^{(1)} + V_\epsilon^{(1)T} V_0
\end{aligned}
```

the second equation implies that $`V_0^T V_\epsilon^{(1)}`$ is skew-symmetric. It is real and therefore has zero diagonal elements.

we now wish to isolate $`\Lambda_\epsilon^{(1)}`$ :

```math
\begin{aligned}
\Lambda_\epsilon^{(1)}
&= V_0^T L_0 V_\epsilon^{(1)} + V_0^T L_1 V_0 - V_0^T V_\epsilon^{(1)} \Lambda_0 \\
&= \Lambda_0 V_0^T V_\epsilon^{(1)} + V_0^T L_1 V_0 - V_0^T V_\epsilon^{(1)} \Lambda_0 \\
\end{aligned}
```

Since $`\Lambda_1`$ is diagonal, we only need to consider the diagonal elements of the above equation:

```math
\begin{aligned}
\lambda_{\epsilon, i}^{(1)}
&= \lambda_{0, i} \cancel{(V_0^T V_\epsilon^{(1)})_{ii}} + (V_0^T L_1 V_0)_{ii} - \cancel{(V_0^T V_\epsilon^{(1)})_{ii}} \lambda_{0, i} \\
&= (V_0^T L_1 V_0)_{ii} \\
\end{aligned}
```

We have thus found the first order correction to the eigenvalues of $`L_\epsilon`$:

```math
\Lambda_\epsilon^{(1)} = \text{diag}(V_0^T L_1 V_0)
```

## Ressources

[A Tutorial on Matrix Perturbation Theory
(using compact matrix notation),
Bassam Bamieh](https://arxiv.org/pdf/2002.05001)