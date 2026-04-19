def formatear_tiempo(minutos_totales):
    """Convierte minutos a formato legible +/- Xh Ym."""
    signo = ""
    if minutos_totales < 0:
        signo = "-"
        minutos_totales = abs(minutos_totales)

    horas = minutos_totales // 60
    minutos = minutos_totales % 60
    return f"{signo}{horas}h {minutos}m"


def calcular_saldo_total(datos):
    """Recorre todo el historial y suma las diferencias."""
    saldo = 0
    for fecha, info in datos.items():
        saldo += info['diferencia']
    return saldo
