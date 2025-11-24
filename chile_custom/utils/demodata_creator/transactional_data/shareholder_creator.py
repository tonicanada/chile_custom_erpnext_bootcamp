import frappe

def crear_shareholders_demo():
    """
    Crea 5 shareholders con RUTs válidos,
    mezclando Persona Natural y Persona Jurídica.
    """

    shareholders = [
        {
            "title": "Juan Pérez Soto",
            "rut": "12345678-5",     # ✔️ válido
            "tipo_accionista": "Persona Natural"
        },
        {
            "title": "María González Torres",
            "rut": "9876543-3",      # ✔️ válido
            "tipo_accionista": "Persona Natural"
        },
        {
            "title": "Inversiones Andes SpA",
            "rut": "76543210-3",     # ✔️ válido
            "tipo_accionista": "Persona Jurídica"
        },
        {
            "title": "Constructora Los Robles Ltda",
            "rut": "77321890-0",     # ✔️ válido
            "tipo_accionista": "Persona Jurídica"
        },
        {
            "title": "Desarrollos Patagónicos S.A.",
            "rut": "78901234-2",     # ✔️ válido
            "tipo_accionista": "Persona Jurídica"
        },
    ]


    creados = []
    existentes = []

    for sh in shareholders:
        if frappe.db.exists("Shareholder", sh["title"]):
            existentes.append(sh["title"])
            continue

        doc = frappe.get_doc({
            "doctype": "Shareholder",
            "title": sh["title"],
            "rut": sh["rut"],
            "tipo_accionista": sh["tipo_accionista"]
        })

        doc.insert(ignore_permissions=True)
        doc.save()
        creados.append(sh["title"])

    frappe.db.commit()

    return {
        "creados": creados,
        "existentes": existentes
    }