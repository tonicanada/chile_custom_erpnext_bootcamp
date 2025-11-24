import frappe
from datetime import date, timedelta
import random


def pagar_sueldos_por_proyecto(
    company: str,
    project_name: str,
    cuenta_sueldos_por_pagar: str,
    cuenta_banco: str,
    seed: int | None = 42,
):
    """
    Genera Payment Entries para pagar sueldos de un proyecto.

    Lógica:
    - Cada mes tiene un saldo en la cuenta Sueldos por Pagar, causado por JE mensuales.
    - La función detecta el saldo mes a mes en el libro mayor.
    - Crea un Payment Entry por mes.
    - Fecha del pago:
        - 70%: primeros 5 días del mes siguiente
        - 20%: el mismo día de fin de mes
        - 10%: 1–3 días antes del fin de mes (pago adelantado)
    """

    if seed is not None:
        random.seed(seed)

    # -------------------------------------------------------
    # 1) Obtener el rango de fechas del proyecto
    # -------------------------------------------------------
    proj = frappe.get_doc("Project", project_name)
    start = proj.expected_start_date or proj.start_date
    end = proj.expected_end_date or proj.end_date

    if not start or not end:
        raise Exception(f"El proyecto {project_name} no tiene fechas definidas.")

    start = start.replace(day=1)  # desde inicio de mes
    end = end.replace(day=28)     # evitar problemas con meses irregulares

    # -------------------------------------------------------
    # 2) Obtener movimientos por mes
    # -------------------------------------------------------
    ledger = frappe.get_all(
        "GL Entry",
        filters={
            "company": company,
            "account": cuenta_sueldos_por_pagar,
            "project": project_name,
        },
        fields=["posting_date", "debit", "credit"],
        order_by="posting_date asc"
    )

    if not ledger:
        print(f"⚠️ No hay movimientos de sueldos por pagar para {project_name}")
        return []

    # Agrupar por (año, mes)
    meses = {}

    for row in ledger:
        y = row.posting_date.year
        m = row.posting_date.month
        key = (y, m)
        if key not in meses:
            meses[key] = {"debit": 0, "credit": 0}
        meses[key]["debit"] += row.debit
        meses[key]["credit"] += row.credit

    creados = []

    # -------------------------------------------------------
    # 3) Procesar cada mes y generar Payment Entry
    # -------------------------------------------------------
    for (y, m), movs in meses.items():
        saldo_mes = movs["credit"] - movs["debit"]

        if saldo_mes <= 0:
            continue  # nada que pagar

        # fechas relevantes
        mes_ini = date(y, m, 1)
        mes_fin = date(y, m, 28)  # simplificación segura

        # -------------------------------------------------------
        # Elegir día de pago
        # -------------------------------------------------------
        r = random.random()
        if r < 0.70:
            # primeros 5 días del mes siguiente
            pay_date = (mes_fin + timedelta(days=3)).replace(day=random.randint(1,5))
        elif r < 0.90:
            # mismo día fin de mes
            pay_date = mes_fin
        else:
            # 1–3 días antes del fin de mes
            pay_date = mes_fin - timedelta(days=random.randint(1, 3))

        # Recuperar la cuenta por pagar real (puede ser la misma o distinta)
        cuenta_por_pagar = cuenta_sueldos_por_pagar

        # -------------------------------------------------------
        # Crear Payment Entry
        # -------------------------------------------------------
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Internal Transfer",     # <-- CLAVE
            "company": company,
            "posting_date": pay_date,

            # DINERO SALE DEL BANCO
            "paid_from": cuenta_banco,
            "paid_from_account_currency": frappe.db.get_value("Account", cuenta_banco, "account_currency"),

            # DINERO ENTRA A SUELDOS POR PAGAR (reduciendo el pasivo)
            "paid_to": cuenta_por_pagar,
            "paid_to_account_currency": frappe.db.get_value("Account", cuenta_por_pagar, "account_currency"),

            "paid_amount": saldo_mes,
            "received_amount": saldo_mes,
            "remarks": f"Pago de sueldos proyecto {project_name} — {y}-{m:02d}",
            "reference_no": f"SUELDO-{project_name}-{y}{m:02d}",
            "reference_date": pay_date,
        })

        pe.insert(ignore_permissions=True)
        pe.submit()

        creados.append(pe.name)
        print(f"💸 Pago de sueldos creado: {pe.name} — mes {y}-{m:02d} — {saldo_mes:,.0f} CLP")

    frappe.db.commit()

    print(f"\n🏁 PAGOS DE SUELDOS para proyecto {project_name}: {len(creados)} Payment Entries creados.")
    return creados



# pagar_sueldos_por_proyecto(
#     company="Constructora Horizonte SpA",
#     project_name="PROJ-0029",
#     cuenta_sueldos_por_pagar="02.01.03.01 - Sueldos por Pagar - CH",
#     cuenta_banco="01.01.01.06 - Banco BCI - CH",
# )
