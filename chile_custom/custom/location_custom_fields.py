import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def create_location_custom_project_field():
    """
    Crea un nuevo Custom Field en Location para enlazar un Proyecto.
    No usa el campo estándar 'project'.
    
    Ejecutar:
        bench --site SITE execute chile_custom.scripts.location_add_custom_project_field.create_location_custom_project_field
    """

    new_fieldname = "linked_project"   # <--- cámbialo si quieres

    # Verificar si ya existe
    existing = frappe.db.exists(
        "Custom Field",
        {"dt": "Location", "fieldname": new_fieldname}
    )

    if existing:
        return f"⚠️ Ya existe un campo '{new_fieldname}' en Location."

    field = {
        "fieldname": new_fieldname,
        "label": "Proyecto",
        "fieldtype": "Link",
        "options": "Project",
        "insert_after": "location_name",
        "reqd": 0,
        "hidden": 0,
        "in_list_view": 1,
        "in_standard_filter": 1,
        "description": "Proyecto asociado a esta Location",
    }

    create_custom_field("Location", field)
    frappe.db.commit()

    return f"✅ Custom Field '{new_fieldname}' creado exitosamente en Location."
