def fuzzify_slope(p):
    if abs(p) < 0.01:
        return 0.1
    if abs(p) < 0.03:
        return 0.5
    return 1.0


def fuzzify_r2(r2):
    if r2 < 0.3:
        return 0.2
    if r2 < 0.6:
        return 0.6
    return 1.0


def fuzzify_proximity(valor, minimo, maximo):
    if minimo <= valor <= maximo:
        return 0.2
    if (minimo - 1) <= valor <= (maximo + 1):
        return 0.6
    return 1.0


def evaluar_riesgo_difuso(pendiente, r2, valor_actual, minimo, maximo):
    s = fuzzify_slope(pendiente)
    c = fuzzify_r2(r2)
    p = fuzzify_proximity(valor_actual, minimo, maximo)

    # Inferencia (AND difuso ≈ promedio ponderado)
    riesgo = (0.4 * s) + (0.3 * c) + (0.3 * p)

    if riesgo < 0.35:
        return "bajo", riesgo
    elif riesgo < 0.7:
        return "medio", riesgo
    else:
        return "alto", riesgo
