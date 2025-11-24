import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def create_codigo_sbif_field():
    """
    Crea un Custom Field en el DocType 'Bank' para almacenar el Código SBIF.
    """

    fieldname = "codigo_sbif"

    # Evitar duplicados
    if frappe.db.exists("Custom Field", f"Bank-{fieldname}"):
        frappe.msgprint("ℹ️ El campo 'Código SBIF' ya existe.")
        return

    create_custom_field(
        "Bank",
        {
            "fieldname": fieldname,
            "label": "Código SBIF",
            "fieldtype": "Data",
            "insert_after": "bank_name",   # después de nombre del banco
            "reqd": 0,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "translatable": 0,
            "description": "Código SBIF/CMF del banco (por ejemplo: Santander = 037)"
        }
    )

    frappe.db.commit()
    frappe.msgprint("🎉 Campo 'Código SBIF' creado correctamente en Bank.")
