import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def create_employee_rut_field():
    """
    Crea (o actualiza) un campo 'rut' en el DocType Employee.

    Para ejecutarlo:
        bench --site [site] execute chile_custom.scripts.employee_rut_custom_field.create_employee_rut_field
    """

    field = {
        "fieldname": "rut",
        "label": "RUT",
        "fieldtype": "Data",
        "insert_after": "employee_name",   # puedes cambiarlo
        "reqd": 0,
        "unique": 0,
        "bold": 1,
        "translatable": 0,
        "description": "RUT chileno del empleado",
    }

    # Verificar si ya existe
    existing = frappe.db.exists(
        "Custom Field",
        {"dt": "Employee", "fieldname": "rut"}
    )

    if existing:
        # Si existe, actualizar
        cf = frappe.get_doc("Custom Field", existing)
        cf.update(field)
        cf.save()
        frappe.msgprint("Campo RUT actualizado en Employee.")
    else:
        # Si no existe, crear
        create_custom_field("Employee", field, ignore_validate=True)
        frappe.msgprint("Campo RUT creado en Employee.")

    frappe.clear_cache(doctype="Employee")
