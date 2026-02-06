from typing import List, Tuple

def regresion_lineal(valores: List[float]) -> Tuple[float, float]:
    """
    Retorna (pendiente, R²) usando datos reales.
    x = orden temporal de llegada
    """
    n = len(valores)
    if n < 3:
        return 0.0, 0.0

    x = list(range(n))
    y = valores

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    den = sum((x[i] - mean_x) ** 2 for i in range(n))

    if den == 0:
        return 0.0, 0.0

    m = num / den
    b = mean_y - m * mean_x

    ss_tot = sum((yi - mean_y) ** 2 for yi in y)
    ss_res = sum((y[i] - (m * x[i] + b)) ** 2 for i in range(n))

    r2 = 1 - (ss_res / ss_tot) if ss_tot else 0.0

    return round(m, 4), round(r2, 4)
