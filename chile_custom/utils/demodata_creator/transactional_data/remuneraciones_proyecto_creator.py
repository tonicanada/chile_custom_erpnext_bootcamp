import frappe
from datetime import date
import calendar
import random

from chile_custom.utils.demodata_creator.transactional_data.project_utils import get_project_info


def _split_budget_uniform(total: float, months: int, perturbation: float = 0.20):
    """
    Distribución uniforme con perturbaciones.
    - Cada mes parte con total/months
    - Se le agrega una variación aleatoria: +/-perturbation (20% por defecto)
    - Se normaliza la suma total
    - Se redondea a miles

    Ej: perturbation=0.20 → cada mes puede variar entre 80% y 120% del valor base.
    """

    if months <= 0:
        return []

    base = total / months

    # generar variaciones
    raw = []
    for _ in range(months):
        factor = 1 + random.uniform(-perturbation, perturbation)
        raw.append(base * factor)

    # normalizar para que sumen total
    s = sum(raw)
    normalized = [v * (total / s) for v in raw]

    # redondeo "bonito"
    rounded = [round(a, -3) for a in normalized]
    diff = total - sum(rounded)
    if rounded:
        rounded[0] += diff

    return rounded


def _month_range(start: date, end: date):
    months = []
    y, m = start.year, start.month
    while True:
        months.append((y, m))
        if (y == end.year and m == end.month):
            break
        m += 1
        if m > 12:
            m = 1
            y += 1
    return months


def crear_remuneraciones_para_proyecto(
    company: str,
    project_name: str,
    presupuesto_total: float,
    cuenta_gasto_rem: str,
    cuenta_sueldos_por_pagar: str = "02.01.03.01 - Sueldos por Pagar - CH",
    seed: int | None = 42,
    perturbation: float = 0.20,
):
    """
    Crea Journal Entries mensuales para remuneraciones asociadas a un proyecto.

    - Distribución uniforme con perturbación (pequeña variación mes a mes).
    - Dr Gasto remuneraciones (CC proyecto)
    - Cr Sueldos por pagar
    - Fecha = último día de cada mes del proyecto.
    """

    if seed is not None:
        random.seed(seed)

    proj, start, end, cost_center, customer = get_project_info(project_name)
    meses = _month_range(start, end)
    n_meses = len(meses)

    if n_meses <= 0:
        print("⚠️ Proyecto sin meses válidos en el rango.")
        return []

    # --- Distribución uniforme perturbada ---
    montos = _split_budget_uniform(
        presupuesto_total,
        n_meses,
        perturbation=perturbation
    )

    creados = []

    for idx, (y, m) in enumerate(meses):
        last_day = calendar.monthrange(y, m)[1]
        fecha = date(y, m, last_day)
        monto = montos[idx]

        je = frappe.get_doc({
            "doctype": "Journal Entry",
            "company": company,
            "posting_date": fecha,
            "voucher_type": "Journal Entry",
            "user_remark": f"Remuneraciones proyecto {project_name} ({calendar.month_name[m]})",
            "accounts": [
                {
                    "account": cuenta_gasto_rem,
                    "debit_in_account_currency": monto,
                    "cost_center": cost_center,
                    "project": project_name,
                },
                {
                    "account": cuenta_sueldos_por_pagar,
                    "credit_in_account_currency": monto,
                    "cost_center": cost_center,
                    "project": project_name,
                },
            ]
        })

        je.insert(ignore_permissions=True)
        je.submit()

        creados.append(je.name)
        print(f"🧾 JE remuneraciones creado: {je.name} ({fecha}) por {monto:,.0f} CLP")

    frappe.db.commit()

    print(
        f"🎯 Remuneraciones generadas para {project_name}: {len(creados)} meses "
        f"(presupuesto: {presupuesto_total:,.0f} CLP)"
    )

    return creados



# crear_remuneraciones_para_proyecto(
#     company="Constructora Horizonte SpA",
#     project_name="PROJ-0003",
#     presupuesto_total=120_000_000,   # 120 millones en remuneraciones
#     cuenta_gasto_rem="5.01.10.01 - Remuneraciones Obra - CH",
# )
