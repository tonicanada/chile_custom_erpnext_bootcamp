import frappe

def crear_bodegas_por_proyecto(stock_account):
    """
    Crea automáticamente un Warehouse por cada Project existente.

    Pasos:
    1) Asegura que exista un Warehouse Group padre llamado 'Bodegas Obras'.
    2) Recorre todos los Project del ERPNext.
    3) Para cada Project:
        - Crea un Warehouse con el mismo nombre del Project (si no existe).
        - Asigna la cuenta de stock recibida como argumento.
        - Lo ubica bajo el Warehouse Group 'Bodegas Obras'.

    Cómo ejecutarlo desde consola:
        bench --site site1.bootcamp console

        from chile_custom.utils.warehouse_generator import crear_bodegas_por_proyecto
        crear_bodegas_por_proyecto("01.01.20.01 - Existencias - CH")

    Args:
        stock_account (str): Nombre completo de la cuenta contable de stock
                             que se asociará a todos los warehouses creados.
    """

    frappe.flags.in_test = False  # asegurar comportamiento normal

    # ==========================================================
    # 1) CREAR / OBTENER WAREHOUSE GROUP PADRE
    # ==========================================================
    group_name = "Bodegas Obras"

    # Buscar si existe
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
    # 2) OBTENER PROYECTOS
    # ==========================================================
    proyectos = frappe.get_all("Project", fields=["name", "project_name"])

    if not proyectos:
        print("No hay proyectos en el sistema. Nada que hacer.")
        return

    print(f"Encontrados {len(proyectos)} proyectos…")

    # ==========================================================
    # 3) CREAR WAREHOUSES POR PROYECTO
    # ==========================================================
    creados = 0
    ya_existian = 0

    for proj in proyectos:
        wh_name = proj["project_name"]

        if frappe.db.exists("Warehouse", wh_name):
            ya_existian += 1
            continue

        print(f"Creando Warehouse para proyecto: {wh_name}")

        wh_doc = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": wh_name,
            "is_group": 0,
            "parent_warehouse": parent_wh,
            "account": stock_account   # asignar la cuenta de stock
        })

        wh_doc.insert(ignore_permissions=True)
        creados += 1

    print("----------------------------------------")
    print(f"Warehouses creados: {creados}")
    print(f"Ya existían: {ya_existian}")
    print("----------------------------------------")
    print("Proceso completado correctamente.")
