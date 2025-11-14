import re
import frappe


def normalize_rut(rut: str) -> str:
    """
    Limpia, normaliza y valida un RUT chileno.
    Devuelve SIEMPRE el formato: XXXXXXXX-DV (sin puntos, guion obligatorio)
    Ej: "12.345.678-k" -> "12345678-K"
    """

    if not rut:
        return ""

    rut = rut.strip().upper()

    # 1. quitar puntos
    rut = rut.replace(".", "")

    # 2. Si NO tiene guion, intentar reconstruirlo
    if "-" not in rut:
        # último carácter → DV
        rut = rut[:-1] + "-" + rut[-1:]

    # Validar formato básico
    if not re.match(r"^\d+-[\dK]$", rut):
        raise frappe.ValidationError("Formato de RUT inválido. Use: 12345678-K")

    cuerpo, dv = rut.split("-")

    if not cuerpo.isdigit():
        raise frappe.ValidationError("RUT inválido: el cuerpo debe ser numérico.")

    # Validar DV
    if calculate_dv(cuerpo) != dv:
        raise frappe.ValidationError(f"RUT inválido: el dígito verificador no coincide ({rut})")

    # 3. Devolver en formato estándar
    return f"{cuerpo}-{dv}"


def calculate_dv(cuerpo: str) -> str:
    """
    Calcula el dígito verificador con el algoritmo OFICIAL del SII (2-7).
    """

    suma = 0
    factor = 2

    for c in reversed(cuerpo):
        suma += int(c) * factor
        factor = 2 if factor == 7 else factor + 1

    resto = suma % 11
    dv = 11 - resto

    if dv == 11:
        return "0"
    if dv == 10:
        return "K"
    return str(dv)
