import frappe
from datetime import timedelta
import random


def crear_pagos_para_proyecto(
    company: str,
    project_name: str,
    cuenta_banco: str,
    seed: int | None = 42,
    porcentaje_30_dias: float = 0.7,
    porcentaje_contado: float = 0.2,
    porcentaje_60_dias: float = 0.1,
    porcentaje_sin_pagar: float = 0.10,   # <= NUEVO: % de facturas que NO se pagarán
):
    """
    Crea Payment Entries para las facturas de compra (PINV) asociadas a un proyecto,
    usando el proyecto definido en los ítems. Permite dejar un % de facturas sin pagar.

    LOGICA:
    - Facturas ordenadas por fecha
    - Las últimas X facturas (según % sin pagar) se dejan sin pago
    - 70% se pagan a 30 días
    - 20% al contado
    - 10% a 60 días
    - Outstanding siempre correcto
    """

    if seed is not None:
        random.seed(seed)

    # -------------------------------------------------
    # 1. Obtener todas las PINV (docstatus=1)
    # -------------------------------------------------
    pinvs_all = frappe.get_all(
        "Purchase Invoice",
        filters={"docstatus": 1},
        fields=["name", "supplier", "posting_date", "bill_no", "grand_total"],
        order_by="posting_date asc"  # <= importante para saber cuáles son las últimas
    )

    pinvs = []

    # -------------------------------------------------
    # 2. Filtrar solo las PINV cuyos ítems coinciden con el proyecto
    # -------------------------------------------------
    for inv in pinvs_all:
        items = frappe.get_all(
            "Purchase Invoice Item",
            filters={"parent": inv.name},
            fields=["project"]
        )

        if not items:
            continue

        # primer project válido que aparezca en los ítems
        project_item = next((it.project for it in items if it.project), None)

        if project_item == project_name:
            pinvs.append(inv)

    if not pinvs:
        print(f"⚠️ No se encontraron PINV para proyecto '{project_name}' usando ítems.")
        return []

    # -------------------------------------------------
    # 3. Calcular cuántas facturas dejar SIN pagar
    # -------------------------------------------------
    n_total = len(pinvs)
    n_sin_pagar = int(n_total * porcentaje_sin_pagar)

    if n_sin_pagar > 0:
        pinvs_sin_pagar = pinvs[-n_sin_pagar:]   # últimas
        pinvs_a_pagar  = pinvs[:-n_sin_pagar]   # todas menos las últimas
        print(f"🔕 {len(pinvs_sin_pagar)} facturas quedarán SIN pagar")
    else:
        pinvs_sin_pagar = []
        pinvs_a_pagar = pinvs

    # Normalizar porcentajes
    total_p = porcentaje_30_dias + porcentaje_contado + porcentaje_60_dias
    p30 = porcentaje_30_dias / total_p
    p0  = porcentaje_contado   / total_p
    p60 = porcentaje_60_dias  / total_p

    creados = []

    # -------------------------------------------------
    # 4. Procesar las PINV que SÍ se pagarán
    # -------------------------------------------------
    for inv in pinvs_a_pagar:

        # outstanding real
        outstanding = frappe.db.get_value(
            "Purchase Invoice",
            inv.name,
            "outstanding_amount"
        )

        if not outstanding or outstanding <= 0:
            print(f"⚠️ PINV {inv.name} ya está pagada, saltando…")
            continue

        # escoger condición de pago
        r = random.random()
        if r < p30:
            dias = 30
        elif r < p30 + p0:
            dias = 0
        else:
            dias = 60

        posting_date = inv.posting_date + timedelta(days=dias)

        # cuenta por pagar desde Company
        cuenta_por_pagar = frappe.db.get_value(
            "Company", company, "default_payable_account"
        )

        if not cuenta_por_pagar:
            raise Exception(
                f"La compañía {company} no tiene configurada default_payable_account."
            )

        # -------------------------------------------------
        # Crear Payment Entry
        # -------------------------------------------------
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "company": company,
            "posting_date": posting_date,
            "paid_from": cuenta_banco,
            "paid_to": cuenta_por_pagar,
            "party_type": "Supplier",
            "party": inv.supplier,
            "paid_amount": outstanding,
            "received_amount": outstanding,
            "reference_no": inv.bill_no or inv.name,
            "reference_date": inv.posting_date,
            "remarks": f"Pago automático factura {inv.name} (proyecto {project_name})",
            "references": [{
                "reference_doctype": "Purchase Invoice",
                "reference_name": inv.name,
                "due_date": inv.posting_date + timedelta(days=dias),
                "total_amount": outstanding,
                "outstanding_amount": outstanding,
                "allocated_amount": outstanding,
            }]
        })

        pe.insert(ignore_permissions=True)
        pe.submit()

        creados.append(pe.name)
        print(f"💸 Payment Entry creado: {pe.name} — PINV {inv.name} — pago {dias} días")

    frappe.db.commit()

    print(f"\n🏁 PAGOS PARA PROYECTO {project_name}: {len(creados)} Payment Entries creados.")
    print(f"🔕 Facturas sin pagar: {len(pinvs_sin_pagar)}")
    return creados
