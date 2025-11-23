# File: chile_custom/validations/employee_rut.py
# ---------------------------------------------------------
# Validación del campo RUT en el DocType Employee.
# Usa la misma función normalize_rut utilizada para validar tax_id.
# ---------------------------------------------------------

import frappe
from chile_custom.utils.rut import normalize_rut


def validate_employee_rut(doc, method):
    """Valida y normaliza el campo 'rut' del Employee."""

    # Si no existe el campo rut o está vacío → no validar
    if not hasattr(doc, "rut"):
        return

    if not doc.rut:
        return

    try:
        # Normalizar RUT usando la misma función que tax_id
        doc.rut = normalize_rut(doc.rut)
    except Exception as e:
        frappe.throw(str(e))
