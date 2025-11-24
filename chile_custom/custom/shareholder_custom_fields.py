import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def create_shareholder_custom_fields():
    """
    Crea campos personalizados en el DocType 'Shareholder':
    - RUT
    - Tipo de Accionista (Persona Natural / Persona Jurídica)
    """

    custom_fields = []

    # 1. Campo RUT
    custom_fields.append({
        "fieldname": "rut",
        "label": "RUT",
        "fieldtype": "Data",
        "insert_after": "title",        # ← campo correcto en Shareholder
        "reqd": 0,
        "in_list_view": 1,
        "in_standard_filter": 1,
        "description": "RUT del accionista (Ej: 12.345.678-9)"
    })

    # 2. Campo Tipo de Accionista
    custom_fields.append({
        "fieldname": "tipo_accionista",
        "label": "Tipo de Accionista",
        "fieldtype": "Select",
        "options": "Persona Natural\nPersona Jurídica",
        "insert_after": "rut",
        "reqd": 0,
        "in_list_view": 1,
        "in_standard_filter": 1
    })

    for cf in custom_fields:
        cf_key = f"Shareholder-{cf['fieldname']}"
        if not frappe.db.exists("Custom Field", cf_key):
            create_custom_field("Shareholder", cf)

    frappe.db.commit()
    frappe.msgprint("🎉 Campos personalizados creados en Shareholder.")
