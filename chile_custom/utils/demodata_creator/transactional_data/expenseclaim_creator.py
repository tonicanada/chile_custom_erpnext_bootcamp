import frappe
import random
from datetime import timedelta

from frappe.utils import getdate
from chile_custom.utils.demodata_creator.transactional_data.project_utils import get_project_info


def get_tipos_comprobante():
    """
    Obtiene las opciones del Custom Field tipo_comprobante_tributario.
    """
    field = frappe.db.get_value(
        "Custom Field",
        {"dt": "Expense Claim Detail", "fieldname": "tipo_comprobante_tributario"},
        "options",
    )
    if not field:
        raise Exception("❌ No existe el custom field tipo_comprobante_tributario.")

    return [opt.strip() for opt in field.split("\n") if opt.strip()]


def crear_expense_claims_para_proyecto(project_name: str, company: str, cantidad: int = 10):
    """
    Crea Expense Claims con líneas aleatorias dentro del rango del proyecto.
    """

    print(f"\n=== Creando Expense Claims para {project_name} ({company}) ===")

    # ──────────────────────────────────────────
    # INFO DEL PROYECTO
    # ──────────────────────────────────────────
    proj, start, end, cost_center, customer = get_project_info(project_name)

    if proj.company != company:
        raise Exception(
            f"❌ El proyecto {project_name} pertenece a '{proj.company}', no a '{company}'."
        )

    # ──────────────────────────────────────────
    # DATOS DINÁMICOS
    # ──────────────────────────────────────────
    empleados = frappe.get_all("Employee", filters={"company": company}, pluck="name")
    suppliers = frappe.get_all("Supplier", pluck="name")
    tipos_gasto = frappe.get_all("Expense Claim Type", pluck="name")
    tipos_comprobante = get_tipos_comprobante()

    if not empleados:
        raise Exception(f"❌ No hay empleados asociados a la empresa {company}.")
    if not suppliers:
        raise Exception("❌ No existen proveedores.")
    if not tipos_gasto:
        raise Exception("❌ No existen Expense Claim Type.")
    if not tipos_comprobante:
        raise Exception("❌ El custom field tipo_comprobante_tributario no tiene opciones.")

    created = []
    rango_dias = (end - start).days

    # ──────────────────────────────────────────
    # CREACIÓN DE EXPENSE CLAIMS
    # ──────────────────────────────────────────
    for _ in range(cantidad):

        # Fecha aleatoria dentro del rango del proyecto
        fecha = start + timedelta(days=random.randint(0, max(0, rango_dias)))

        empleado = random.choice(empleados)
        emp_doc = frappe.get_doc("Employee", empleado)
        department = emp_doc.department or None

        # Parent
        claim = frappe.get_doc({
            "doctype": "Expense Claim",
            "company": company,
            "posting_date": fecha,
            "approval_status": "Approved",
            "employee": empleado,
            "project": proj.name,
            "department": department,
            "cost_center": cost_center,   # <- asignado, pero ERPNext lo pisará en validate()
        })

        # Crear entre 1 y 4 líneas
        lineas = random.randint(1, 4)

        for _ in range(lineas):
            amount = random.randint(3000, 20000)

            claim.append("expenses", {
                "expense_type": random.choice(tipos_gasto),
                "description": "Gasto generado automáticamente",
                "amount": amount,
                "project": proj.name,
                "cost_center": cost_center,
                "tipo_comprobante_tributario": random.choice(tipos_comprobante),
                "numero_documento": random.randint(1000, 999999),
                "proveedor": random.choice(suppliers),
            })

        # Inserción → ERPNext pisa cost center y sanctioned_amount
        claim.insert(ignore_permissions=True)

        # ──────────────────────────────────────────
        # FIX 1: Forzar cost center del parent
        # ──────────────────────────────────────────
        claim.db_set("cost_center", cost_center)

        # ──────────────────────────────────────────
        # FIX 2: Igualar expense_date al posting_date
        # ──────────────────────────────────────────
        for row in claim.expenses:
            row.db_set("expense_date", claim.posting_date)

        # ──────────────────────────────────────────
        # FIX 3: sanctioned_amount = amount
        # ──────────────────────────────────────────
        for row in claim.expenses:
            row.db_set("sanctioned_amount", row.amount)

        # Submit sin riesgos (ya no sobrescribe nada)
        claim.submit()

        print(f"   ✔ Creado: {claim.name}")
        created.append(claim.name)

    frappe.db.commit()

    print(f"\n🎉 {len(created)} Expense Claims creados exitosamente para {project_name}\n")
    return created



# crear_expense_claims_para_proyecto(
#     project_name="PROJ-0003",
#     company="Constructora Horizonte SpA",
#     cantidad=20
# )