# Réponse d'un système linéaire stationaire à un bruit blanc

## Modèle

Considérons le système dynamique avec une perturbation stochastique $`\xi(t)`$ :

```math
\dot{x}(t) = A x(t) + \xi(t)
```

avec $`\xi(t)`$ un bruit blanc stationnaire caractérisé par :

```math
\mathbb{E}[\xi(t)] = 0, \qquad \mathbb{E}[\xi(t)\xi(t')^T] = Q \delta(t-t')
```

## Réponse du système

entre les temps $`t`$ et $`t+dt`$ :

```math
\begin{aligned}
x(t+dt)
&= e^{A dt} x(t) + \int_0^{dt} e^{A \tau} \xi(t+dt-\tau) d\tau \\
&= [I + A dt + o(dt)] x(t) + \int_0^{dt} [I + o(1)] \xi(t+dt-\tau) d\tau \\
&= [I + A dt] x(t) + \underbrace{\int_t^{t+dt} \xi(s) ds}_{= \int_0^{dt} \xi(s) ds = \Xi(dt)} + o(dt)\\
\end{aligned}
```

Etudions $`\Xi(dt) = \int_0^{dt} \xi(s) ds`$, il s'agit d'une variable aléatoire gaussienne :

* de moyenne nulle : $`\mathbb{E}[\Xi(dt)] = \int_0^{dt} \mathbb{E}[\xi(s)] ds = 0`$,

* de variance $`\mathbb{E}[\Xi(dt)\Xi(dt)^T] = \int_0^{dt} \int_0^{dt} \mathbb{E}[\xi(s)\xi(s')^T] ds ds' = \int_0^{dt} \int_0^{dt} Q \delta(s-s') ds ds' = Q dt`$.

### Calcul de $`\mathbb{E}[x]`$

```math
\begin{aligned}
&\mathbb{E}[x(t+dt)]= [I + A dt] \mathbb{E}[x(t)] + \cancel{\mathbb{E}[\Xi(dt)]} + o(dt) \\ \\
&\frac{d\mathbb{E}[x]}{dt} = A \mathbb{E}[x(t)] \\
\end{aligned}
```

Si le système est stable, $`\mathbb{E}[x(t)] \to 0`$.

### Calcul de $`\mathbb{E}[x x^T]`$

posons $`P(t) = \mathbb{E}[x(t)x(t)^T]`$, on a :

```math
\begin{aligned}
&P(t+dt) &&= &&\mathbb{E}[x(t+dt)x(t+dt)^T] \\
& &&= &&\mathbb{E}[((I + A dt) x(t) + \Xi(dt))((I + A dt) x(t) + \Xi(dt))^T] + o(dt) \\
& &&= &&\mathbb{E}[((I + A dt) x(t) x(t)^T (I + A^T dt)] \\
& && &&+ \mathbb{E}[\Xi(dt) \Xi(dt)^T] \\
& && &&+ \cancel{\mathbb{E}[(I + A dt) x(t) \Xi(dt)^T]} + \cancel{\mathbb{E}[\Xi(dt) x(t)^T (I + A^T dt)]} \\
& && &&+ o(dt) \\
& &&= &&(I + A dt) P(t) (I + A^T dt) + Q dt + o(dt) \\
& &&= &&P(t) + (A P(t) + P(t) A^T + Q) dt + o(dt)
\end{aligned}
```

qui donne l'équation différentielle :

```math
\frac{dP}{dt} = A P(t) + P(t) A^T + Q
```

Si l'équation différentielle est stable, $`P(t) \to P`$ solution de l'équation de Lyapunov :

```math
A P + P A^T + Q = 0
```

Comme $`Q \succeq 0`$, ll'existence d'une solution $`P \succeq 0`$ équivaut à la stabilité de $`A`$ (Critère de Liapounov).


## Cas de deux systèmes excités par le même bruit blanc

On considère deux systèmes linéaires stables excités par des bruits blancs gaussiens, potentiellement corrélés :

```math
\begin{aligned}
\dot{x}(t) &= A x(t) + \xi_x(t) \\
\dot{y}(t) &= B y(t) + \xi_y(t)
\end{aligned}
```

avec $`\mathbb{E}[\xi_x \xi_y^T] = Q_{xy}`$

On peut reformuler le système sous la forme d'un système unique :

```math
\begin{aligned}
\begin{bmatrix}
\dot{x}(t) \\
\dot{y}(t)
\end{bmatrix}
&=
\begin{bmatrix}
A & 0 \\
0 & B
\end{bmatrix}
\begin{bmatrix}
x(t) \\
y(t)
\end{bmatrix}
+
\begin{bmatrix}
I \\
I
\end{bmatrix}
\xi(t)
\end{aligned}
```

et obtenir l'équation de Lyapunov pour la matrice de covariance se présente alors sous la forme :

```math
\mathbb{E}[
\begin{bmatrix}
x(t) \\
y(t)
\end{bmatrix}
\begin{bmatrix}
x(t) & y(t)
\end{bmatrix}
] =
\begin{bmatrix}
P_{xx} & P_{xy} \\
P_{yx} & P_{yy}
\end{bmatrix}
```

et l'équation de Lyapunov est :

```math
\begin{bmatrix}
A & 0 \\
0 & B
\end{bmatrix}
\begin{bmatrix}
P_{xx} & P_{xy} \\
P_{yx} & P_{yy}
\end{bmatrix}
+
\begin{bmatrix}
P_{xx} & P_{xy} \\
P_{yx} & P_{yy}
\end{bmatrix}
\begin{bmatrix}
A^T & 0 \\
0 & B^T
\end{bmatrix}
+
\begin{bmatrix}
Q_{xx} & Q_{xy} \\
Q_{yx} & Q_{yy}
\end{bmatrix}
=0
```

c'est-à-dire :

```math
\begin{cases}
A P_{xx} + P_{xx} A^T + Q_{xx} = 0 \\
B P_{yy} + P_{yy} B^T + Q_{yy} = 0 \\
A P_{xy} + P_{xy} B^T + Q_{xy} = 0 \\
B P_{yx} + P_{yx} A^T + Q_{yx} = 0
\end{cases}
```

donc la covariance croisée $`P_{xy}`$ est solution de l'équation de Lyapunov :

```math
A P_{xy} + P_{xy} B^T + Q_{xy} = 0
```