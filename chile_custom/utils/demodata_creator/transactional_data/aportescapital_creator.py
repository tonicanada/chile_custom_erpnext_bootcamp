import frappe
from datetime import datetime

def crear_aportes_capital(empresa, cuenta_banco, aportes, fecha):
    """
    Crea Payment Entries correctos para aportes de capital.
    Asiento generado:
        Dr Banco
            Cr Capital Social
    Incluye Party Type = Shareholder para que ERPNext valide.
    """

    creados = []

    # Centro de costo por si es obligatorio
    cost_center = "OFI - Oficina - CH"

    # Cuenta Capital Social
    cuenta_capital = "03.01 - Capital Social - CH"

    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    fecha_str = fecha_dt.strftime("%Y%m%d")

    for idx, (title, monto) in enumerate(aportes, start=1):

        # Obtener el shareholder por título
        shareholder = frappe.db.get_value(
            "Shareholder",
            {"title": title, "company": empresa},
            "name"
        )
        if not shareholder:
            print(f"❌ Shareholder no encontrado: {title}")
            continue

        nombre_pe = f"CAP-{fecha_str}-{idx:03d}"

        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "name": nombre_pe,

            "payment_type": "Receive",
            "company": empresa,
            "posting_date": fecha,

            # 🔥 ERPNext lo exige
            "party_type": "Shareholder",
            "party": shareholder,

            # 🔥 Sobreescribimos la lógica interna de Proveedores
            "paid_from": cuenta_capital,        # HABER
            "paid_to": cuenta_banco,            # DEBE

            # Montos
            "paid_amount": monto,
            "received_amount": monto,

            # Obligatorios para pagos bancarios
            "reference_no": f"Aporte-{idx}",
            "reference_date": fecha,

            # Cost center por obligación
            "cost_center": cost_center,
        })

        pe.insert(ignore_permissions=True)
        pe.submit()

        print(f"✅ Payment Entry creado: {nombre_pe} → {title}: {monto}")
        creados.append(nombre_pe)

    frappe.db.commit()
    return creados







# # EJECUTAR
# empresa = "Constructora Horizonte SpA"
# cuenta_banco = "01.01.01.02 - Banco Santander - CH"
# fecha = "2024-01-10"

# aportes = [
#     ("Juan Pérez Soto", 50000000),
#     ("María González Torres", 20000000),
#     ("Inversiones Andes SpA", 25000000),
#     ("Constructora Los Robles Ltda", 30000000),
#     ("Desarrollos Patagónicos S.A.", 25000000),
# ]

# crear_aportes_capital(empresa, cuenta_banco, aportes, fecha)
