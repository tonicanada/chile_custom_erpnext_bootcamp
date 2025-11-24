import frappe

def crear_centros_costos_por_proyecto(company: str):
    """
    Crea automáticamente centros de costos hijos para cada proyecto de una compañía.
    
    Pasos:
    1) Elimina todos los centros de costo hijos del centro de costo raíz cuyo nombre = company.
    2) Recorre todos los Project y crea un centro de costo hijo para cada uno:
        - cost_center_number = project.abbr  (o project.project_name si no existe abbr)
        - cost_center_name   = project.project_name
    3) Crea también un centro de costo fijo:
        - cost_center_number = 'OFI'
        - cost_center_name   = 'Oficina'
    
    Parámetros:
        company (str): Nombre de la empresa (Company.name) que tiene un Cost Center raíz.
    """

    if not company:
        frappe.throw("Debes pasar el nombre de la Company.")

    # ---------------------------------------------------------
    # 1) Obtener centro de costo raíz de la empresa
    # ---------------------------------------------------------
    cc_root = frappe.get_value("Cost Center", {"company": company, "is_group": 1}, "name")
    if not cc_root:
        frappe.throw(f"No existe un Cost Center raíz para la empresa: {company}")

    print(f"Centro de costo raíz encontrado: {cc_root}")

    # ---------------------------------------------------------
    # 2) Eliminar todos los hijos del CC raíz
    # ---------------------------------------------------------
    hijos = frappe.get_all("Cost Center", filters={"parent_cost_center": cc_root}, fields=["name"])
    print(f"Eliminando {len(hijos)} centros de costo existentes…")

    for h in hijos:
        frappe.delete_doc("Cost Center", h["name"], force=1, ignore_permissions=True)

    # ---------------------------------------------------------
    # 3) Obtener proyectos
    # ---------------------------------------------------------
    proyectos = frappe.get_all("Project", fields=["name", "project_name", "project_prefix"])

    print(f"Se crearán centros de costo para {len(proyectos)} proyectos…")

    for p in proyectos:
        prefix = p.get("project_prefix") or p.get("name")[:6].upper()  # fallback por si no hay abbr
        cc_number = prefix

        nuevo_cc = frappe.get_doc({
            "doctype": "Cost Center",
            "company": company,
            "parent_cost_center": cc_root,
            "is_group": 0,
            "cost_center_number": cc_number,
            "cost_center_name": p["project_name"],
        })

        nuevo_cc.insert(ignore_permissions=True)
        print(f" → Creado CC: {cc_number} – {p['project_name']}")

    # ---------------------------------------------------------
    # 4) Crear "Oficina"
    # ---------------------------------------------------------
    cc_oficina = frappe.get_doc({
        "doctype": "Cost Center",
        "company": company,
        "parent_cost_center": cc_root,
        "is_group": 0,
        "cost_center_number": "OFI",
        "cost_center_name": "Oficina",
    })

    cc_oficina.insert(ignore_permissions=True)
    print(" → Creado CC: OFI – Oficina")

    frappe.db.commit()
    print("Proceso completado correctamente.")

