import frappe

def reset_expense_claim_types(company: str, default_account: str = None):
    """
    Borra todos los Expense Claim Type y crea nuevos.
    Inserta correctamente filas en la tabla hija 'accounts'.
    """

    print("\n=== Reset de Expense Claim Types ===")

    # Validar cuenta contable
    if default_account:
        existe = frappe.db.exists("Account", {"name": default_account, "company": company})
        if not existe:
            raise Exception(f"❌ La cuenta '{default_account}' no existe en la empresa '{company}'.")

    # ------------------------------------------------
    # BORRAR EXISTENTES
    # ------------------------------------------------
    existing = frappe.get_all("Expense Claim Type", pluck="name")

    for e in existing:
        try:
            frappe.delete_doc("Expense Claim Type", e, force=True, ignore_permissions=True)
            print(f"🗑 Eliminado: {e}")
        except Exception as err:
            print(f"⚠️ No se pudo eliminar {e}: {err}")

    frappe.db.commit()

    # ------------------------------------------------
    # NUEVOS TIPOS
    # ------------------------------------------------
    nuevos_tipos = [
        "Viaje",
        "Alojamiento",
        "Comida",
        "Transporte",
        "Combustible",
        "Peajes",
        "Estacionamiento",
        "Materiales Menores",
        "Herramientas Menores",
        "Telefonía / Internet",
        "Gastos de Representación",
        "Movilización",
        "Suministros de Oficina",
        "Arriendo Equipos",
        "Otros",
    ]

    for tipo in nuevos_tipos:
        # Crear documento vacio
        doc = frappe.get_doc({
            "doctype": "Expense Claim Type",
            "expense_type": tipo,
            "description": f"Tipo de gasto: {tipo}",
        })

        doc.insert(ignore_permissions=True)

        # ---------------------------------------------------
        # 🔥 Crear manualmente fila en tabla hija
        #    (ESTA ES LA CLAVE)
        # ---------------------------------------------------
        if default_account:
            frappe.get_doc({
                "doctype": "Expense Claim Account",
                "parent": doc.name,
                "parenttype": "Expense Claim Type",
                "parentfield": "accounts",
                "company": company,
                "default_account": default_account,
            }).insert(ignore_permissions=True)

        print(f"✔ Creado: {tipo}")

    frappe.db.commit()

    print("\n🎉 Reset de Expense Claim Types completado correctamente.\n")
