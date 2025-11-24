import frappe

def create_bankaccount_types_es():
    """
    Crea Bank Account Types con nombres en español.
    El DocType solo tiene un campo obligatorio: account_type.
    """
    tipos = [
        "Cuenta Corriente",
        "Cuenta Vista",
        "Cuenta de Ahorro",
        "Tarjeta de Crédito",
        "Depósito a Plazo",
    ]

    creados = []
    existentes = []

    for label in tipos:
        # Usamos el mismo nombre como ID del documento
        internal_name = label

        if frappe.db.exists("Bank Account Type", internal_name):
            existentes.append(internal_name)
            continue

        doc = frappe.get_doc({
            "doctype": "Bank Account Type",
            "name": internal_name,       # Esto será el ID y también la etiqueta visible
            "account_type": label        # ÚNICO CAMPO OBLIGATORIO
        })

        doc.insert(ignore_permissions=True)
        creados.append(internal_name)

    frappe.db.commit()

    frappe.msgprint(
        f"🎉 Bank Account Types creados: {creados}<br>"
        f"📌 Ya existentes: {existentes}"
    )

    return {"creados": creados, "existentes": existentes}
