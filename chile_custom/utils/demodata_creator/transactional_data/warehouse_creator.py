import frappe

def crear_bodegas_por_proyecto(stock_account):
    """
    Crea automáticamente un Warehouse por cada Project existente.

    Además:
    - Elimina todos los warehouses hijos del grupo 'Bodegas Obras' si existen.
    - Asigna la cuenta contable de stock a cada warehouse creado.
    - Completa el custom field 'project' en Warehouse con el nombre del Proyecto.

    Ejecución:
        bench --site site1.bootcamp console
        from chile_custom.utils.warehouse_generator import crear_bodegas_por_proyecto
        crear_bodegas_por_proyecto("01.01.20.01 - Existencias - CH")
    """

    frappe.flags.in_test = False

    group_name = "Bodegas Obras - CH"

    # ==========================================================
    # 1) CREAR U OBTENER EL WAREHOUSE GROUP PADRE
    # ==========================================================
    parent_wh = frappe.db.exists("Warehouse", group_name)

    if not parent_wh:
        print("Creando Warehouse Group padre 'Bodegas Obras'…")
        parent_doc = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": group_name,
            "is_group": 1,
            "parent_warehouse": None
        })
        parent_doc.insert(ignore_permissions=True)
        parent_wh = parent_doc.name
    else:
        print(f"Warehouse Group padre ya existe: {parent_wh}")

    # ==========================================================
    # 2) ELIMINAR TODOS LOS HIJOS DEL GRUPO PADRE
    # ==========================================================
    print("Eliminando hijos existentes del grupo 'Bodegas Obras'…")

    children = frappe.get_all(
        "Warehouse",
        filters={"parent_warehouse": parent_wh},
        fields=["name", "is_group"]
    )

    # Borrar primero los warehouses que NO son grupo
    for wh in children:
        if not wh["is_group"]:
            print(f"  - Eliminando warehouse (no group): {wh['name']}")
            frappe.delete_doc("Warehouse", wh["name"], ignore_permissions=True, force=True)

    # Luego borrar los grupos (si existieran)
    for wh in children:
        if wh["is_group"]:
            print(f"  - Eliminando sub-group: {wh['name']}")
            frappe.delete_doc("Warehouse", wh["name"], ignore_permissions=True, force=True)

    print("Hijos eliminados correctamente.\n")

    # ==========================================================
    # 3) OBTENER PROYECTOS
    # ==========================================================
    proyectos = frappe.get_all("Project", fields=["name", "project_name"])

    if not proyectos:
        print("No hay proyectos en el sistema. Nada que hacer.")
        return

    print(f"Encontrados {len(proyectos)} proyectos…")

    # ==========================================================
    # 4) CREAR WAREHOUSES POR PROYECTO
    # ==========================================================
    creados = 0

    for proj in proyectos:
        wh_name = proj["project_name"]   # nombre visible (warehouse_name)
        project_id = proj["name"]        # ID real (para el campo custom)

        print(f"Creando Warehouse para proyecto: {wh_name}")

        wh_doc = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": wh_name,
            "is_group": 0,
            "parent_warehouse": parent_wh,
            "account": stock_account,
            "project": project_id        # ← CUANDO EL CUSTOM FIELD SE LLAMA 'project'
        })

        wh_doc.insert(ignore_permissions=True)
        creados += 1

    print("----------------------------------------")
    print(f"Warehouses creados: {creados}")
    print("----------------------------------------")
    print("Proceso completado correctamente.")
