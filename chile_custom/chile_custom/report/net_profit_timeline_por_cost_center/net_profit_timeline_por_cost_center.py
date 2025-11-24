import frappe
from frappe.utils import flt
from datetime import timedelta


def execute(filters=None):
    if not filters:
        filters = {}

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw("Debe seleccionar From Date y To Date")

    # ------------------------------------------------------------
    # 1. Traer GL Entries
    # ------------------------------------------------------------
    rows = frappe.db.sql(
        """
        SELECT 
            gle.posting_date AS day,
            gle.cost_center,
            SUM(gle.credit - gle.debit) AS net_profit
        FROM `tabGL Entry` gle
        INNER JOIN `tabAccount` acc
            ON gle.account = acc.name
        WHERE
            gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
            AND acc.root_type IN ('Income', 'Expense')
            AND gle.cost_center IS NOT NULL
        GROUP BY gle.posting_date, gle.cost_center
        ORDER BY gle.posting_date
        """,
        {"from_date": from_date, "to_date": to_date},
        as_dict=True,
    )

    if not rows:
        return [], []

    # ------------------------------------------------------------
    # 2. Agrupar por cost center y calcular acumulado
    # ------------------------------------------------------------
    data_by_cc = {}
    for r in rows:
        cc = r.cost_center
        data_by_cc.setdefault(cc, [])
        data_by_cc[cc].append((r.day, flt(r.net_profit)))

    # Calcular acumulado por centro de costo
    for cc, values in data_by_cc.items():
        total = 0
        acumulated = []
        for d, np in values:
            total += np
            acumulated.append((d, total))
        data_by_cc[cc] = dict(acumulated)

    # ------------------------------------------------------------
    # 3. Crear lista COMPLETA de fechas (sin saltos)
    # ------------------------------------------------------------
    start = frappe.utils.getdate(from_date)
    end = frappe.utils.getdate(to_date)

    all_dates = []
    current = start
    while current <= end:
        all_dates.append(current)
        current += timedelta(days=1)

    # ------------------------------------------------------------
    # 4. Construir columnas
    # ------------------------------------------------------------
    columns = [{"label": "Fecha", "fieldname": "day", "fieldtype": "Date"}]

    for cc in data_by_cc:
        columns.append({
            "label": cc,
            "fieldname": cc.replace(" ", "_").lower(),
            "fieldtype": "Float"
        })

    # ------------------------------------------------------------
    # 5. Construir filas con FORWARD FILL
    # ------------------------------------------------------------
    data = []
    for d in all_dates:
        row = {"day": d}
        for cc in data_by_cc:
            cc_field = cc.replace(" ", "_").lower()
            valores = data_by_cc[cc]

            if d in valores:
                row[cc_field] = valores[d]
            else:
                # obtener último valor previo: forward fill
                prev_dates = [x for x in valores.keys() if x < d]
                if prev_dates:
                    last_date = max(prev_dates)
                    row[cc_field] = valores[last_date]
                else:
                    row[cc_field] = 0

        data.append(row)

    return columns, data
