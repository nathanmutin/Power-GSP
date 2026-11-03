import numpy as np
import pandas as pd
from scipy.linalg import expm

from utils.grid import Grid

def step_response(grid: Grid, delta_P: pd.Series, t: np.ndarray) -> [pd.DataFrame, pd.DataFrame]:
    """
    Réponse à un échelon de puissance ΔP appliqué à t = 0, à partir de l'équilibre (δ = δ' = 0).

    Args:
        grid: Réseau électrique (Grid).
        delta_P: Perturbation (MW) par nœud, pd.Series indexée par bus ou tableau dans l'ordre de buses.
            Négative pour une perte de production.
        t (np.ndarray): Instants (s).

    Returns:
        (delta, freq): DataFrames bus x instants : écart d'angle δ (rad)
        et écart de fréquence Δf = δ' / 2π (Hz).
    """
    # inertial and non-inertial buses
    m = grid.M.diagonal()
    g = m > 0
    l = ~g
    
    # Calcul de a^ = V^T M^{-1/2} ΔP
    delta_P_array = grid.to_array(delta_P)
    delta_P_reduced = delta_P_array[g] - grid.L[g,:][:, l] @ grid.lu_L_ll.solve(delta_P_array[l])
    a_hat = grid.eigenvectors.T @ (grid.M.diagonal()[g] ** -0.5 * delta_P_reduced)
    
    # Valeurs pour la soltution analytique
    squared_pulsations = grid.eigenvalues
    pulsations = grid.pulsations
    damping_ratios = grid.damping_ratios
    damped_pulsations = pulsations * np.sqrt(np.abs(1 - damping_ratios**2))
    exponent_decay = -damping_ratios * pulsations
    sin_factors = damped_pulsations / np.sqrt(np.abs(1 - damping_ratios**2))
    
    # Réponse comme somme sur les modes
    delta_hat = np.zeros((len(a_hat), len(t)))
    f_hat = np.zeros((len(a_hat), len(t)))
    
    delta_hat[0] = a_hat[0] * t**2 / 2
    f_hat[0] = a_hat[0] * t
    
    for k in range(1, len(a_hat)):
        # On néglige les modes sur-amortis (ζ > 1) car ils sont très rapides et ne contribuent pas à la réponse.
        if damping_ratios[k] < 1:            
            delta_hat[k] = a_hat[k] / squared_pulsations[k] * (
                1 - np.exp(exponent_decay[k] * t) * (
                    np.cos(damped_pulsations[k] * t)
                    + sin_factors[k] * np.sin(damped_pulsations[k] * t)
                )
            )
            f_hat[k] = a_hat[k] / damped_pulsations[k] * np.exp(exponent_decay[k] * t) * np.sin(damped_pulsations[k] * t)
        else:
            # On ajoute tout de même le valeure en régime permanent pour les modes sur-amortis, mais pas la partie transitoire.
            delta_hat[k] = a_hat[k] / squared_pulsations[k] * np.ones_like(t)
            #f_hat[k] = np.zeros_like(t)
    
    f_hat = f_hat / (2 * np.pi)
    
    delta = grid.modes @ delta_hat
    f = grid.modes @ f_hat
    
    return pd.DataFrame(delta, index=grid.buses.index, columns=t), pd.DataFrame(f, index=grid.buses.index, columns=t)


def step_response_integration(grid: Grid, delta_P: pd.Series, t: np.ndarray) -> [pd.DataFrame, pd.DataFrame]:
    """
    Idem que step_response mais par intégration numérique de l'équation différentielle.
    Pour vérifier l'implémentation analytique (step_response).
    """
    # inertial and non-inertial buses
    m = grid.M.diagonal()
    g = m > 0
    l = ~g
    
    x0 = np.zeros(2 * sum(g))  # [δ_g, δ'_g]
    
    A = np.zeros((2 * sum(g), 2 * sum(g)))
    A[:sum(g), sum(g):] = np.eye(sum(g))
    A[sum(g):, :sum(g)] = -grid.L_reduced / m[g][:, None]
    A[sum(g):, sum(g):] = -grid.D_reduced / m[g][:, None]
    
    b = np.zeros(2 * sum(g))
    b[sum(g):] = (delta_P[g] - grid.L[g,:][:, l] @ grid.lu_L_ll.solve(delta_P[l])) / m[g] 
    
    deltas = np.zeros((len(m), len(t)))
    fs = np.zeros((len(m), len(t)))
    deltas[g, 0] = x0[:sum(g)]
    
    for i in range(len(t) - 1):
        # On connait la solution avec l'exponentielle de matrice
        dt = t[i + 1] - t[i]
        exp_At = expm(A * dt)
        x0 = exp_At @ x0 + np.linalg.solve(A, (exp_At - np.eye(2 * sum(g))) @ b)
        deltas[g, i + 1] = x0[:sum(g)]
        fs[g, i + 1] = x0[sum(g):]
    
    # Prolongation aux nœuds sans inertie par Kron
    deltas[l, :] = grid.l_from_g_values(deltas[g, :])
    fs[l, :] = grid.l_from_g_values(fs[g, :])
    fs = fs / (2 * np.pi)
        
    return pd.DataFrame(deltas, index=grid.buses.index, columns=t), pd.DataFrame(fs, index=grid.buses.index, columns=t)