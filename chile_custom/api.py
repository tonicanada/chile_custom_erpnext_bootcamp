import frappe
from chile_custom.constants.regiones import regiones

@frappe.whitelist()
def get_region_from_comuna(comuna):
    for r in regiones:
        if comuna in r["comunas"]:
            return {
                "region": r["region"],
                "numero": r["numero"]
            }
    return {}


@frappe.whitelist(allow_guest=True)
def top_proveedores_pinv():
    """
    Devuelve los 10 proveedores con más facturas de compra.
    SQL simple sin parámetros.
    """
    data = frappe.db.sql(
        """
        SELECT
            supplier,
            COUNT(*) as total_facturas,
            SUM(grand_total) as monto_total
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1
        GROUP BY supplier
        ORDER BY total_facturas DESC
        LIMIT 10
        """,
        as_dict=True
    )

    return data


@frappe.whitelist()
def facturas_pinv_por_fecha(fecha_inicio, fecha_fin, supplier=None):
    """
    Consulta SQL avanzada con parámetros.
    Devuelve todas las PINV entre fechas, opcionalmente filtradas por proveedor.
    """

    conditions = """
        posting_date BETWEEN %(start)s AND %(end)s
        AND docstatus = 1
    """

    params = {
        "start": fecha_inicio,
        "end": fecha_fin,
    }

    # Si el usuario envía un supplier opcional
    if supplier:
        conditions += " AND supplier = %(supplier)s"
        params["supplier"] = supplier

    query = f"""
        SELECT
            name,
            supplier,
            posting_date,
            due_date,
            grand_total,
            outstanding_amount
        FROM `tabPurchase Invoice`
        WHERE {conditions}
        ORDER BY posting_date DESC
        LIMIT 500
    """

    results = frappe.db.sql(query, params, as_dict=True)
    return results
