import frappe
from chile_custom.utils.rut import normalize_rut

def validate_tax_id(doc, method):
    """Valida y normaliza tax_id en cualquier DocType."""

    if not hasattr(doc, "tax_id"):
        return

    if not doc.tax_id:
        return

    try:
        doc.tax_id = normalize_rut(doc.tax_id)
    except Exception as e:
        frappe.throw(str(e))
