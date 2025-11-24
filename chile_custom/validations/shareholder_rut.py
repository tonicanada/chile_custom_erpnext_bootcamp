# File: chile_custom/validations/shareholder_rut.py
# ---------------------------------------------------------
# Validación del campo RUT en el DocType Shareholder.
# Usa la misma función normalize_rut utilizada para validar tax_id.
# ---------------------------------------------------------

import frappe
from chile_custom.utils.rut import normalize_rut

def validate_shareholder_rut(doc, method):
    """Valida y normaliza el campo 'rut' del Shareholder."""

    # Si no existe el campo rut o está vacío → no validar
    if not hasattr(doc, "rut"):
        return

    if not doc.rut:
        return

    try:
        # Normalizar RUT usando la misma función que employee / tax_id
        doc.rut = normalize_rut(doc.rut)
    except Exception as e:
        frappe.throw(str(e))
