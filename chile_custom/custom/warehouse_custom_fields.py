import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def create_warehouse_project_field():
    """
    Crea (o actualiza) un campo 'project' en el DocType Warehouse.
    Permite vincular cada bodega a un Proyecto.

    Para ejecutarlo:
        bench --site [site] execute chile_custom.scripts.warehouse_project_custom_field.create_warehouse_project_field
    """

    field = {
        "fieldname": "project",
        "label": "Proyecto",
        "fieldtype": "Link",
        "options": "Project",
        "insert_after": "warehouse_name",  # puedes cambiarlo si quieres otro orden
        "reqd": 0,
        "translatable": 0,
        "description": "Proyecto al cual pertenece esta bodega.",
    }

    # Verificar si ya existe
    existing = frappe.db.exists(
        "Custom Field",
        {"dt": "Warehouse", "fieldname": "project"}
    )

    if existing:
        # Si existe, actualizar los valores
        cf = frappe.get_doc("Custom Field", existing)
        cf.update(field)
        cf.save()
        frappe.msgprint("Campo 'project' actualizado en Warehouse.")
    else:
        # Si no existe, crear
        create_custom_field("Warehouse", field, ignore_validate=True)
        frappe.msgprint("Campo 'project' creado en Warehouse.")

    # Limpiar caché del DocType
    frappe.clear_cache(doctype="Warehouse")
