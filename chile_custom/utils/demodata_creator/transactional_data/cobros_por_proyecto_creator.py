import frappe
from datetime import timedelta
import random


def crear_cobros_para_proyecto(
    company: str,
    project_name: str,
    cuenta_banco: str,
    seed: int | None = 42,
    porcentaje_30_dias: float = 0.7,
    porcentaje_contado: float = 0.2,
    porcentaje_60_dias: float = 0.1,
    porcentaje_sin_cobrar: float = 0.10,  # <= NUEVO: % de SINV sin cobrar
):
    """
    Crea Payment Entries tipo 'Receive' para SINV asociadas a un proyecto,
    usando el proyecto definido en los ÍTEMS (NO en el parent). Deja un %
    de facturas sin cobrar (las últimas temporalmente).

    LÓGICA:
    - 70% cobranza a 30 días
    - 20% al contado
    - 10% a 60 días
    - Outstanding real siempre correcto
    """

    if seed is not None:
        random.seed(seed)

    # -------------------------------------------------
    # 1. Obtener SINV submitted
    # -------------------------------------------------
    sinv_all = frappe.get_all(
        "Sales Invoice",
        filters={"docstatus": 1},
        fields=["name", "customer", "posting_date", "grand_total"],
        order_by="posting_date asc"
    )

    sinv = []

    # -------------------------------------------------
    # 2. Filtrar por proyecto desde los ítems
    # -------------------------------------------------
    for inv in sinv_all:
        items = frappe.get_all(
            "Sales Invoice Item",
            filters={"parent": inv.name},
            fields=["project"]
        )

        if not items:
            continue

        project_item = next((it.project for it in items if it.project), None)

        if project_item == project_name:
            sinv.append(inv)

    if not sinv:
        print(f"⚠️ No se encontraron SINV para proyecto '{project_name}' usando ítems.")
        return []

    # -------------------------------------------------
    # 3. Sin cobrar (las últimas)
    # -------------------------------------------------
    n_total = len(sinv)
    n_sin_cobrar = int(n_total * porcentaje_sin_cobrar)

    if n_sin_cobrar > 0:
        sinv_sin_cobrar = sinv[-n_sin_cobrar:]
        sinv_a_cobrar = sinv[:-n_sin_cobrar]
        print(f"🔕 {len(sinv_sin_cobrar)} SINV quedarán SIN COBRAR")
    else:
        sinv_sin_cobrar = []
        sinv_a_cobrar = sinv

    # Normalizar porcentajes
    total_p = porcentaje_30_dias + porcentaje_contado + porcentaje_60_dias
    p30 = porcentaje_30_dias / total_p
    p0  = porcentaje_contado   / total_p
    p60 = porcentaje_60_dias  / total_p

    creados = []

    # -------------------------------------------------
    # 4. Crear Payment Entries de cobro
    # -------------------------------------------------
    for inv in sinv_a_cobrar:

        # outstanding real
        outstanding = frappe.db.get_value(
            "Sales Invoice",
            inv.name,
            "outstanding_amount"
        )

        if not outstanding or outstanding <= 0:
            print(f"⚠️ SINV {inv.name} ya está cobrada, saltando…")
            continue

        # condición de cobro
        r = random.random()
        if r < p30:
            dias = 30
        elif r < p30 + p0:
            dias = 0
        else:
            dias = 60

        posting_date = inv.posting_date + timedelta(days=dias)

        # cuenta por cobrar desde Company
        cuenta_por_cobrar = frappe.db.get_value(
            "Company", company, "default_receivable_account"
        )

        if not cuenta_por_cobrar:
            raise Exception(
                f"La compañía {company} no tiene configurada default_receivable_account."
            )

        # -------------------------------------------------
        # Crear Payment Entry (Receive)
        # -------------------------------------------------
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "company": company,
            "posting_date": posting_date,
            "paid_to": cuenta_banco,   # entra el dinero al banco
            "paid_from": cuenta_por_cobrar,  # sale de cuentas por cobrar
            "party_type": "Customer",
            "party": inv.customer,
            "paid_amount": outstanding,
            "received_amount": outstanding,
            "reference_no": inv.name,
            "reference_date": inv.posting_date,
            "remarks": f"Cobro automático SINV {inv.name} (proyecto {project_name})",
            "references": [{
                "reference_doctype": "Sales Invoice",
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
        print(f"💰 Payment Entry creado: {pe.name} — SINV {inv.name} — cobro {dias} días")

    frappe.db.commit()

    print(f"\n🏁 COBROS PARA PROYECTO {project_name}: {len(creados)} Payment Entries creados.")
    print(f"🔕 SINV sin cobrar: {len(sinv_sin_cobrar)}")
    return creados



# crear_cobros_para_proyecto(
#     "Constructora Horizonte SpA",
#     "PROJ-0029",
#     "01.01.01.06 - Banco BCI - CH",
#     porcentaje_sin_cobrar=0.10   # 20% sin cobrar
# )
