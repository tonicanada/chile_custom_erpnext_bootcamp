import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from chile_custom.constants.regiones import regiones

def create_address_custom_fields():
    # Construir lista completa de comunas (sin duplicados, ordenadas)
    comunas = sorted({c for r in regiones for c in r["comunas"]})
    comunas_options = "\n".join(comunas)

    fields = [
        {
            "fieldname": "comuna",
            "label": "Comuna",
            "fieldtype": "Select",
            "options": comunas_options,
            "insert_after": "state",
            "depends_on": "eval:doc.country=='Chile'",
        },
        {
            "fieldname": "region",
            "label": "Región",
            "fieldtype": "Data",
            "read_only": 1,
            "insert_after": "comuna",
            "depends_on": "eval:doc.country=='Chile'",
        },
        {
            "fieldname": "region_numero",
            "label": "Código Región",
            "fieldtype": "Data",
            "read_only": 1,
            "insert_after": "region",
            "depends_on": "eval:doc.country=='Chile'",
        },
    ]

    for df in fields:
        # ¿Ya existe el Custom Field?
        existing_name = frappe.db.exists(
            "Custom Field",
            {"dt": "Address", "fieldname": df["fieldname"]}
        )

        if existing_name:
            # Actualizarlo
            cf = frappe.get_doc("Custom Field", existing_name)
            cf.update(df)
            cf.save()
        else:
            # Crearlo
            create_custom_field("Address", df, ignore_validate=True)

    frappe.clear_cache(doctype="Address")
