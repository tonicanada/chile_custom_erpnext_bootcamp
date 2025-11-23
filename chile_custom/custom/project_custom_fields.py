import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from chile_custom.constants.regiones import regiones


def create_project_custom_fields():

    # =============================
    # Generar lista de comunas
    # =============================
    comunas = sorted({c for r in regiones for c in r["comunas"]})
    comunas_options = "\n".join(comunas)

    # =============================
    # Campos a crear en Project
    # =============================
    fields = [

        # -----------------------------------------
        # 1) Prefijo del proyecto (obligatorio)
        # -----------------------------------------
        {
            "fieldname": "project_prefix",
            "label": "Project Prefix",
            "fieldtype": "Data",
            "unique": 1,
            "reqd": 1,
            "insert_after": "project_name",
        },

        # -----------------------------------------
        # 2) Latitud
        # -----------------------------------------
        {
            "fieldname": "project_latitude",
            "label": "Latitude",
            "fieldtype": "Float",
            "precision": 9,      # permite -22.815345
            "insert_after": "project_prefix",
        },

        # -----------------------------------------
        # 3) Longitud
        # -----------------------------------------
        {
            "fieldname": "project_longitude",
            "label": "Longitude",
            "fieldtype": "Float",
            "precision": 9,
            "insert_after": "project_latitude",
        },

        # -----------------------------------------
        # 4) URL Google Maps (calculada)
        # -----------------------------------------
        {
            "fieldname": "project_maps_url",
            "label": "Google Maps URL",
            "fieldtype": "Data",
            "read_only": 1,
            "insert_after": "project_longitude",
            "description": "Se construye automaticamente a partir de latitud y longitud",
        },

        # -----------------------------------------
        # 5) Pais
        # -----------------------------------------
        {
            "fieldname": "project_country",
            "label": "Country",
            "fieldtype": "Link",
            "options": "Country",
            "insert_after": "project_maps_url",
        },

        # -----------------------------------------
        # 6) Comuna (solo Chile)
        # -----------------------------------------
        {
            "fieldname": "project_comuna",
            "label": "Comuna",
            "fieldtype": "Select",
            "options": comunas_options,
            "insert_after": "project_country",
            "depends_on": "eval:doc.project_country=='Chile'",
        },

        # -----------------------------------------
        # 7) Region (solo Chile, read-only)
        # -----------------------------------------
        {
            "fieldname": "project_region",
            "label": "Region",
            "fieldtype": "Data",
            "read_only": 1,
            "insert_after": "project_comuna",
            "depends_on": "eval:doc.project_country=='Chile'",
        },

        # -----------------------------------------
        # 8) Direccion completa
        # -----------------------------------------
        {
            "fieldname": "project_address",
            "label": "Project Address",
            "fieldtype": "Small Text",
            "insert_after": "project_region",
        },
    ]

    # =============================
    # Creación / Actualización
    # =============================
    for df in fields:
        existing = frappe.db.exists(
            "Custom Field",
            {"dt": "Project", "fieldname": df["fieldname"]},
        )

        if existing:
            cf = frappe.get_doc("Custom Field", existing)
            cf.update(df)
            cf.save()
        else:
            create_custom_field("Project", df, ignore_validate=True)

    frappe.clear_cache(doctype="Project")
