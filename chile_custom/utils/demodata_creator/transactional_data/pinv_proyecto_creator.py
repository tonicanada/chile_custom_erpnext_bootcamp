import random
from datetime import date, timedelta

import frappe
from frappe.utils import getdate
from chile_custom.utils.demodata_creator.transactional_data.project_utils import get_project_info


# -------------------------------------------------
# CONFIGURACIÓN OPCIONAL POR GRUPOS
# (ajusta estos nombres a tus item_group / supplier_group
# o déjalos vacíos para usar filtros genéricos)
# -------------------------------------------------

# Para materiales de obra (stock)
ITEM_GROUPS_MATERIAL = [
    # "Materiales de Obra",
    # "Materiales de Construcción",
]

SUPPLIER_GROUPS_MATERIAL = [
    # "Proveedores Materiales",
]

# Para subcontratos / servicios de obra (no stock)
ITEM_GROUPS_SUBCONTRATO = [
    # "Subcontratos",
    # "Servicios de Obra",
]

SUPPLIER_GROUPS_SUBCONTRATO = [
    # "Subcontratistas",
]


# -------------------------------------------------
# HELPERS GENERALES
# -------------------------------------------------


def _get_warehouses_for_project(company: str, project_name: str):
    """Devuelve bodegas asociadas al proyecto o, si no hay, todas las de la empresa."""
    wh = frappe.get_all(
        "Warehouse",
        filters={"project": project_name},
        pluck="name",
    )
    if wh:
        return wh

    wh = frappe.get_all(
        "Warehouse",
        filters={"company": company},
        pluck="name",
    )
    return wh


def _get_items_by_groups(item_groups: list[str] | None, is_stock: bool | None):
    """
    Devuelve item_code filtrando por:
    - ítems habilitados
    - ítems de compra
    - que NO sean activos fijos
    - stock / no stock (según parámetro)
    - item_group (si se especifica)
    """
    filters = {
        "disabled": 0,
        "is_purchase_item": 1,
        "is_fixed_asset": 0,       # <-- EXCLUYE ACTIVOS FIJOS
    }

    if item_groups:
        filters["item_group"] = ["in", item_groups]

    if is_stock is not None:
        filters["is_stock_item"] = 1 if is_stock else 0

    items = frappe.get_all("Item", filters=filters, pluck="name")
    return items



def _get_suppliers_by_groups(supplier_groups: list[str] | None):
    """Devuelve proveedores filtrando por supplier_group (si se da)."""
    filters = {}
    if supplier_groups:
        filters["supplier_group"] = ["in", supplier_groups]

    suppliers = frappe.get_all("Supplier", filters=filters, pluck="name")
    return suppliers


def _random_dates_normal(start: date, end: date, n: int, pre_start_days: int = 15):
    """
    Genera n fechas entre (start - pre_start_days) y end,
    con distribución aproximadamente normal (más concentradas en el centro).
    """
    real_start = start - timedelta(days=pre_start_days)
    real_end = end
    span_days = (real_end - real_start).days
    if span_days <= 0:
        span_days = 1

    xs = []
    for _ in range(n):
        # gauss centrado en 0.5, sigma 0.2, recortado a [0,1]
        v = random.gauss(0.5, 0.2)
        v = max(0.0, min(1.0, v))
        xs.append(v)

    xs.sort()
    dates = [real_start + timedelta(days=int(x * span_days)) for x in xs]
    return dates


def _split_budget(total: float, n: int):
    """Reparte un presupuesto total en n partes aleatorias que suman ~total."""
    if n <= 0:
        return []

    raw = [random.random() for _ in range(n)]
    s = sum(raw)
    if s == 0:
        weights = [1 / n] * n
    else:
        weights = [r / s for r in raw]

    amounts = [total * w for w in weights]
    # redondeo a miles para que quede más bonito, ajustando la diferencia
    rounded = [round(a, -3) for a in amounts]
    diff = total - sum(rounded)
    if rounded:
        rounded[0] += diff

    return rounded


def _get_standard_rate(item_code: str) -> float:
    rate = frappe.db.get_value("Item", item_code, "standard_rate")
    if rate and rate > 0:
        return float(rate)
    return float(random.randint(10_000, 800_000))


# -------------------------------------------------
# CREACIÓN DE PINV POR TIPO
# -------------------------------------------------

def _crear_pinv_material_obra(
    company: str,
    project_name: str,
    posting_date: date,
    monto_aprox: float,
    cost_center: str,
    warehouses: list[str],
    items_material: list[str],
    suppliers_material: list[str],
) -> str | None:
    """Crea una Purchase Invoice de materiales (stock) para un proyecto."""

    if not items_material or not suppliers_material or not warehouses:
        print("⚠️ Config/materiales/bodegas incompletos para material_obra, saltando...")
        return None

    supplier = random.choice(suppliers_material)
    warehouse = random.choice(warehouses)

    # número de líneas
    num_items = random.randint(1, 4)
    item_codes = random.choices(items_material, k=num_items)

    remaining = max(monto_aprox, 50_000)
    items = []
    
    # plantilla de impuestos POR EMPRESA
    tax_template_name = frappe.db.get_value(
        "Purchase Taxes and Charges Template",
        {"is_default": 1, "company": company},
        "name",
    )

    for idx, code in enumerate(item_codes, start=1):
        rate = _get_standard_rate(code)
        if idx == num_items:
            # última línea: que consuma lo que queda aproximadamente
            qty = max(1, int(remaining / rate))
        else:
            max_qty = max(1, int(remaining / (rate * 2)))  # para no comernos todo de golpe
            qty = random.randint(1, max_qty)
            remaining -= qty * rate

        items.append({
            "item_code": code,
            "qty": qty,
            "rate": rate,
            "uom": frappe.db.get_value("Item", code, "stock_uom") or "Nos",
            "warehouse": warehouse,
            "project": project_name,
            "cost_center": cost_center,
        })
        
    bill_no = str(random.randint(10_000, 99_999_999))
    pinv = frappe.get_doc({
        "doctype": "Purchase Invoice",
        "set_posting_time": 1,
        "update_stock": 1,
        "taxes_and_charges": tax_template_name,
        "company": company,
        "posting_date": posting_date,
        "bill_date": posting_date,
        "due_date": posting_date + timedelta(days=30),
        "supplier": supplier,
        "conversion_rate": 1.0,
        "bill_no": bill_no,
        "currency": frappe.db.get_value("Company", company, "default_currency") or "CLP",
        "items": items,
    })
    
    # --- APLICAR PLANTILLA DE IMPUESTOS MANUALMENTE ---
    pinv.taxes = []

    if tax_template_name:
        template = frappe.get_doc("Purchase Taxes and Charges Template", tax_template_name)

        if not template.taxes:
            print(f"⚠️ La plantilla de impuestos '{tax_template_name}' no tiene filas de impuestos.")
        else:
            for t in template.taxes:
                # copiamos los campos relevantes desde la plantilla
                tax_row = t.as_dict().copy()
                # limpiamos metadatos que no deben ir en la nueva fila
                for key in ("name", "parent", "parenttype", "parentfield", "idx", "doctype"):
                    tax_row.pop(key, None)

                pinv.append("taxes", tax_row)

    # por si acaso, aseguramos que ningún item tenga apply_tds = 1
    for it in pinv.items:
        it.apply_tds = 0    
    
    pinv.set_taxes_and_charges()    
    pinv.calculate_taxes_and_totals()
    pinv.insert(ignore_permissions=True)
    pinv.submit()
    print(f"✅ PINV materiales obra creada: {pinv.name} (Proyecto: {project_name})")
    return pinv.name


def _crear_pinv_subcontrato_obra(
    company: str,
    project_name: str,
    posting_date: date,
    monto_aprox: float,
    cost_center: str,
    items_subcontrato: list[str],
    suppliers_subcontrato: list[str],
) -> str | None:
    """Crea una Purchase Invoice de subcontrato (no stock) para un proyecto."""

    if not items_subcontrato or not suppliers_subcontrato:
        print("⚠️ Config/subcontratos incompletos para subcontrato_obra, saltando...")
        return None

    supplier = random.choice(suppliers_subcontrato)

    num_items = random.randint(1, 3)
    item_codes = random.choices(items_subcontrato, k=num_items)

    remaining = max(monto_aprox, 100_000)
    items = []
    
        
    # plantilla de impuestos POR EMPRESA
    tax_template_name = frappe.db.get_value(
        "Purchase Taxes and Charges Template",
        {"is_default": 1, "company": company},
        "name",
    )
    
    for idx, code in enumerate(item_codes, start=1):
        rate = _get_standard_rate(code)
        if idx == num_items:
            qty = max(1, int(remaining / rate))
        else:
            max_qty = max(1, int(remaining / (rate * 2)))
            qty = random.randint(1, max_qty)
            remaining -= qty * rate

        items.append({
            "item_code": code,
            "qty": qty,
            "rate": rate,
            "uom": frappe.db.get_value("Item", code, "stock_uom") or "Nos",
            "project": project_name,
            "cost_center": cost_center,
            # sin warehouse → servicio / no stock
        })

    bill_no = str(random.randint(10_000, 99_999_999))
    pinv = frappe.get_doc({
        "doctype": "Purchase Invoice",
        "set_posting_time": 1,
        "company": company,                 
        "posting_date": posting_date,       
        "taxes_and_charges": tax_template_name,
        "bill_date": posting_date,
        "due_date": posting_date + timedelta(days=30),
        "bill_no": bill_no,
        "supplier": supplier,
        "conversion_rate": 1.0,
        "currency": frappe.db.get_value("Company", company, "default_currency") or "CLP",
        "items": items,
    })
    
    # --- APLICAR PLANTILLA DE IMPUESTOS MANUALMENTE ---
    pinv.taxes = []

    if tax_template_name:
        template = frappe.get_doc("Purchase Taxes and Charges Template", tax_template_name)

        if not template.taxes:
            print(f"⚠️ La plantilla de impuestos '{tax_template_name}' no tiene filas de impuestos.")
        else:
            for t in template.taxes:
                # copiamos los campos relevantes desde la plantilla
                tax_row = t.as_dict().copy()
                # limpiamos metadatos que no deben ir en la nueva fila
                for key in ("name", "parent", "parenttype", "parentfield", "idx", "doctype"):
                    tax_row.pop(key, None)

                pinv.append("taxes", tax_row)

    # por si acaso, aseguramos que ningún item tenga apply_tds = 1
    for it in pinv.items:
        it.apply_tds = 0    
    
    pinv.set_taxes_and_charges() 
    pinv.calculate_taxes_and_totals()
    pinv.insert(ignore_permissions=True)
    pinv.submit()
    print(f"✅ PINV subcontrato obra creada: {pinv.name} (Proyecto: {project_name})")
    return pinv.name


# -------------------------------------------------
# FUNCIÓN PRINCIPAL POR PROYECTO
# -------------------------------------------------

def crear_pinv_para_proyecto(
    company: str,
    project_name: str,
    presupuesto_total: float,
    n_pinv: int = 20,
    porcentaje_material: float = 0.7,
    seed: int | None = 42,
):
    """
    Crea Purchase Invoices demo para un proyecto dado.

    - Usa fechas de inicio/fin del Project para distribuir las facturas en el tiempo.
    - Las compras comienzan hasta 15 días antes de la fecha de inicio.
    - Reparte el presupuesto_total entre n_pinv facturas.
    - Mezcla materiales de obra (stock) y subcontratos (no stock).

    Ejemplo desde bench console:

        from chile_custom.utils.demodata_creator.transactional_data.pinv_proyecto_creator import crear_pinv_para_proyecto

        crear_pinv_para_proyecto(
            "Constructora Horizonte SpA",
            "PROY-0001",
            presupuesto_total=200_000_000,
            n_pinv=30,
            porcentaje_material=0.65,
        )
    """

    if seed is not None:
        random.seed(seed)

    proj, start, end, cost_center, customer = get_project_info(project_name)
    warehouses = _get_warehouses_for_project(company, project_name)

    # Ítems y proveedores
    items_material = _get_items_by_groups(
        ITEM_GROUPS_MATERIAL or None, is_stock=True
    )
    if not items_material:
        # fallback: todos los stock items
        items_material = _get_items_by_groups(None, is_stock=True)

    items_subcontrato = _get_items_by_groups(
        ITEM_GROUPS_SUBCONTRATO or None, is_stock=False
    )
    if not items_subcontrato:
        # fallback: todos los no stock items
        items_subcontrato = _get_items_by_groups(None, is_stock=False)

    suppliers_material = _get_suppliers_by_groups(SUPPLIER_GROUPS_MATERIAL or None)
    if not suppliers_material:
        suppliers_material = frappe.get_all("Supplier", pluck="name")

    suppliers_subcontrato = _get_suppliers_by_groups(SUPPLIER_GROUPS_SUBCONTRATO or None)
    if not suppliers_subcontrato:
        suppliers_subcontrato = frappe.get_all("Supplier", pluck="name")

    if not items_material:
        print("⚠️ No se encontraron ítems de materiales (stock).")
    if not items_subcontrato:
        print("⚠️ No se encontraron ítems de subcontratos (no stock).")
    if not suppliers_material or not suppliers_subcontrato:
        print("⚠️ Revisa que existan proveedores para los grupos configurados.")

    # Fechas y montos por PINV
    fechas = _random_dates_normal(start, end, n_pinv, pre_start_days=15)
    montos = _split_budget(presupuesto_total, n_pinv)

    # --- NUEVO BLOQUE: Garantizar ambos tipos ---

    if n_pinv <= 0:
        print("⚠️ n_pinv debe ser mayor que 0.")
        return []

    # Número de facturas por tipo (forzando mínimo 1 de cada tipo cuando n_pinv > 1)
    n_material = int(round(n_pinv * porcentaje_material))
    if n_pinv > 1:
        if n_material <= 0:
            n_material = 1
        if n_material >= n_pinv:
            n_material = n_pinv - 1
    else:
        # con 1 sola factura no se puede garantizar ambos tipos
        n_material = 1

    n_subcontrato = n_pinv - n_material

    # Lista base (material / subcontrato)
    tipos = ["material"] * n_material + ["subcontrato"] * n_subcontrato

    # Mezcla aleatoria
    random.shuffle(tipos)

    # Asegurar diversidad por tramos del proyecto (inicio / medio / fin)
    tercio = max(1, n_pinv // 3)

    def asegurar_diversidad(segmento):
        sub = [tipos[i] for i in segmento]
        if "material" not in sub:
            tipos[segmento[0]] = "material"
        if "subcontrato" not in sub and n_subcontrato > 0:
            tipos[segmento[-1]] = "subcontrato"

    # Tramos índice → como las fechas están ordenadas, esto equivale a meses iniciales / medios / finales
    asegurar_diversidad(list(range(0, tercio)))
    if 2 * tercio < n_pinv:
        asegurar_diversidad(list(range(tercio, 2 * tercio)))
        asegurar_diversidad(list(range(2 * tercio, n_pinv)))
    else:
        asegurar_diversidad(list(range(tercio, n_pinv)))

    creados = []

    for i in range(n_pinv):
        fecha = fechas[i]
        monto = montos[i]

        tipo = tipos[i]   # 👈 AHORA USAMOS LA LISTA TIPOS, NO random.random()

        if tipo == "material":
            nombre = _crear_pinv_material_obra(
                company,
                project_name,
                fecha,
                monto,
                cost_center,
                warehouses,
                items_material,
                suppliers_material,
            )
        else:
            nombre = _crear_pinv_subcontrato_obra(
                company,
                project_name,
                fecha,
                monto,
                cost_center,
                items_subcontrato,
                suppliers_subcontrato,
            )

        if nombre:
            creados.append(nombre)

    frappe.db.commit()
    print(
        f"🎯 Proyecto {project_name}: PINV creadas = {len(creados)} "
        f"(presupuesto aprox: {presupuesto_total:,.0f} CLP)"
    )
    return creados


# crear_pinv_para_proyecto(
#     "Constructora Horizonte SpA",
#     "EL-NOMBRE-DE-TU-PROYECTO",
#     presupuesto_total=300_000_000,
#     n_pinv=40,
#     porcentaje_material=0.7,
# )