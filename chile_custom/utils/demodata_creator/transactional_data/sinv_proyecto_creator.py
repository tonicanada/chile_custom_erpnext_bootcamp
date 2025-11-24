import random
import math
from datetime import timedelta
import frappe
from frappe.utils import getdate, add_months

from chile_custom.utils.demodata_creator.transactional_data.project_utils import get_project_info


# =====================================================================================
#   RESOLVER ITEM CODE (busca Item.name usando item_name)
# =====================================================================================

def resolve_item_code(item_label: str):
    """
    Devuelve el Item.name correspondiente a item_name = item_label.
    No crea nada. Solo busca.
    """

    # Primero exact match por item_name
    code = frappe.db.get_value("Item", {"item_name": item_label}, "name")
    if code:
        return code

    # Si no, buscar parecido
    code = frappe.db.get_value(
        "Item",
        {"item_name": ["like", f"%{item_label}%"]},
        "name"
    )
    if code:
        return code

    # No se encontró → error explícito
    raise Exception(f"❌ Item '{item_label}' no existe como item_name en la tabla Item.")



# =====================================================================================
#   FUNCIÓN PRINCIPAL
# =====================================================================================

def crear_facturas_venta_proyecto(
    project_name: str,
    presupuesto_total: float,
    porcentaje_anticipo: float = 0.1,
    currency: str = "CLP",
    seed: int | None = 42,
):
    """
    Crea facturas de venta realistas para un proyecto, con distribución Gaussiana.

    - Se obtiene inicio/fin/cost_center del proyecto (get_project_info)
    - Se emite una SINV de Anticipo
    - El resto se reparte mensualmente con distribución normal (curva suave)
    """

    if seed is not None:
        random.seed(seed)

    # ---------------------------
    # 1) Obtener info del Proyecto
    # ---------------------------
    proj, fecha_inicio, fecha_fin, cost_center, customer = get_project_info(project_name)
    company = proj.company

    invoices = []

    # -------------------------------------
    # 2) Calcular montos
    # -------------------------------------
    anticipo_monto = round(presupuesto_total * porcentaje_anticipo)
    monto_restante = presupuesto_total - anticipo_monto

    # -------------------------------
    # 3) Crear factura de ANTICIPO
    # -------------------------------
    fecha_anticipo = fecha_inicio - timedelta(days=random.randint(0, 3))

    sinv_anticipo = _crear_sinv(
        fecha=fecha_anticipo,
        item="Anticipo",
        amount=anticipo_monto,
        project_name=project_name,
        company=company,
        cost_center=cost_center,
        customer=customer,
        currency=currency,
    )
    invoices.append(sinv_anticipo)

    # ----------------------------------------------------
    # 4) Distribuir el monto restante (DISTRIBUCIÓN NORMAL)
    # ----------------------------------------------------

    # Lista de meses (último día del mes)
    meses = []
    fecha_cursor = fecha_inicio

    while fecha_cursor <= fecha_fin:
        last_day = getdate(f"{fecha_cursor.year}-{fecha_cursor.month}-28") + timedelta(days=4)
        last_day = last_day.replace(day=1) - timedelta(days=1)
        meses.append(last_day)
        fecha_cursor = add_months(fecha_cursor, 1)

    n = len(meses)
    if n <= 0:
        raise Exception("El proyecto no tiene rango válido de meses.")

    # ----------------------------------------------------------------------------
    # DISTRIBUCIÓN GAUSSIANA — Realista, suave, con pico hacia la mitad del proyecto
    # ----------------------------------------------------------------------------

    center = (n - 1) / 2         # centro de la curva
    sigma = n / 5                # desviación estándar → da forma agradable

    gaussian_weights = []
    for i in range(n):
        x = i
        weight = math.exp(-0.5 * ((x - center) / sigma) ** 2)
        gaussian_weights.append(weight)

    # Añadir ruido natural ±10%
    gaussian_weights = [
        w * random.uniform(0.9, 1.1)
        for w in gaussian_weights
    ]

    # Normalizar a 1
    total_weight = sum(gaussian_weights)
    gaussian_weights = [w / total_weight for w in gaussian_weights]

    # Aplicar la distribución
    montos_mes = [round(w * monto_restante) for w in gaussian_weights]

    # Ajuste exacto final
    diferencia = monto_restante - sum(montos_mes)
    if diferencia != 0:
        montos_mes[-1] += diferencia

    # ------------------------------------------------
    # 5) Crear las facturas mensuales del proyecto
    # ------------------------------------------------
    for fecha_factura, monto in zip(meses, montos_mes):

        item = "Estado de Pago"
        if random.random() < 0.15:
            item = "Estado de Pago Adicionales"

        sinv = _crear_sinv(
            fecha=fecha_factura,
            item=item,
            amount=monto,
            project_name=project_name,
            company=company,
            cost_center=cost_center,
            customer=customer,
            currency=currency,
        )
        invoices.append(sinv)

    return invoices



# =====================================================================================
#   CREACIÓN DE SALES INVOICE
# =====================================================================================

def _crear_sinv(
    fecha,
    item,
    amount,
    project_name,
    company,
    cost_center,
    customer,
    currency,
):
    sinv = frappe.get_doc({
        "doctype": "Sales Invoice",
        "company": company,
        "customer": customer,
        "set_posting_time": 1,
        "posting_date": fecha,
        "due_date": fecha + timedelta(days=30),
        "currency": currency,
        "project": project_name,
        "cost_center": cost_center,
        "items": [
            {
                "item_code": resolve_item_code(item),
                "qty": 1,
                "rate": amount,
                "income_account": frappe.db.get_value("Company", company, "default_income_account"),
                "cost_center": cost_center,
                "project": project_name
            }
        ],
    })

    # -----------------------------
    # APLICAR IVA DÉBITO
    # -----------------------------
    sinv.taxes = []

    # Obtener plantilla default de ventas por empresa
    tax_template_name = frappe.db.get_value(
        "Sales Taxes and Charges Template",
        {"is_default": 1, "company": company},
        "name",
    )

    if tax_template_name:
        template = frappe.get_doc("Sales Taxes and Charges Template", tax_template_name)

        if not template.taxes:
            print(f"⚠️ La plantilla de impuestos '{tax_template_name}' no tiene filas.")
        else:
            for t in template.taxes:
                row = t.as_dict().copy()
                for key in ("name", "parent", "parenttype", "parentfield", "idx", "doctype"):
                    row.pop(key, None)
                sinv.append("taxes", row)

    # evitar TDS
    for it in sinv.items:
        it.apply_tds = 0

    # cálculos
    sinv.set_taxes_and_charges()
    sinv.calculate_taxes_and_totals()

    sinv.insert(ignore_permissions=True)
    sinv.submit()

    return sinv.name




facturas = crear_facturas_venta_proyecto(
    project_name="CHC",                # ID del proyecto (Project.name)
    presupuesto_total=1_000_000_000,   # Presupuesto total del proyecto (1000 millones)
    porcentaje_anticipo=0.20,          # 20% de anticipo
    currency="CLP"                     # Moneda
)