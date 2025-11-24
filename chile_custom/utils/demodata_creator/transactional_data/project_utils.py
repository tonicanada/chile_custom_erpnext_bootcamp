# project_utils.py

import frappe
from frappe.utils import getdate
from datetime import timedelta
import random
from datetime import date, timedelta


import frappe
from frappe.utils import getdate
from datetime import timedelta

def get_project_info(project_name: str):
    """
    Devuelve:
      - doc del proyecto
      - fecha inicio
      - fecha fin
      - cost center
      - customer asociado (si existe), si no: None
    """

    proj = frappe.get_doc("Project", project_name)

    # -----------------------------
    # FECHAS DEL PROYECTO
    # -----------------------------
    start = (
        proj.expected_start_date
        or proj.actual_start_date
        or proj.get("start_date")
        or getdate(proj.creation)
    )

    end = (
        proj.expected_end_date
        or proj.completion_date
        or (getdate(start) + timedelta(days=180))
    )

    start = getdate(start)
    end = getdate(end)

    if end <= start:
        end = start + timedelta(days=90)

    # -----------------------------
    # COST CENTER
    # -----------------------------
    cost_center = proj.get("cost_center") or frappe.db.get_value(
        "Company", proj.company, "default_cost_center"
    )

    if not cost_center:
        res = frappe.get_all(
            "Cost Center",
            filters={"company": proj.company},
            pluck="name",
            limit_page_length=1,
        )
        if not res:
            raise Exception(f"No se encontró Cost Center para la empresa {proj.company}")
        cost_center = res[0]

    # -----------------------------
    # CUSTOMER DEL PROYECTO
    # -----------------------------
    # Campo estándar en ERPNext desde v14: proj.customer
    customer = proj.get("customer") or None

    return proj, start, end, cost_center, customer




def asignar_cost_center_por_prefijo():
    """
    Recorre todos los proyectos y asigna automáticamente un Cost Center
    basándose en el campo project_prefix del Project.

    Lógica:
    - Toma el project_prefix del proyecto.
    - Busca un Cost Center cuyo nombre comience por ese prefijo.
    - Si encuentra uno, lo asigna al campo `cost_center` del proyecto.
    - No modifica proyectos que ya tienen cost_center asignado.
    """

    proyectos = frappe.get_all(
        "Project",
        fields=["name", "project_name", "project_prefix", "cost_center", "company"]
    )

    if not proyectos:
        print("No se encontraron proyectos.")
        return

    asignados = 0
    saltados = 0
    no_encontrados = []

    for proj in proyectos:
        prefix = proj.get("project_prefix")
        current_cc = proj.get("cost_center")

        # Si ya tiene cost center → saltar
        if current_cc:
            saltados += 1
            continue

        if not prefix:
            no_encontrados.append((proj["name"], "SIN PREFIJO"))
            continue

        # Buscar cost centers cuyo name empiece por el prefijo del proyecto
        posibles_cc = frappe.get_all(
            "Cost Center",
            filters={"company": proj["company"], "name": ["like", f"{prefix}%"]},
            pluck="name"
        )

        if not posibles_cc:
            no_encontrados.append((proj["name"], prefix))
            continue

        cc = posibles_cc[0]

        # Asignar cost center al proyecto
        doc = frappe.get_doc("Project", proj["name"])
        doc.cost_center = cc
        doc.save(ignore_permissions=True)

        asignados += 1
        print(f"✔ Proyecto '{proj['project_name']}' → Cost Center asignado: {cc}")

    # ---------------------------
    #   RESUMEN
    # ---------------------------
    print("\n---------------------------------------")
    print(f"Proyectos revisados: {len(proyectos)}")
    print(f"Cost centers asignados: {asignados}")
    print(f"Saltados (ya tenían cost center): {saltados}")
    print(f"Sin coincidencias: {len(no_encontrados)}")

    if no_encontrados:
        print("\nProyectos sin cost center encontrado:")
        for name, pref in no_encontrados:
            print(f"  - {name} (prefijo: {pref})")



def asignar_cliente_aleatorio_a_proyectos():
    """
    Asigna un cliente aleatorio a cada Project en ERPNext.

    - Toma todos los customers del sistema.
    - Recorre todos los proyectos.
    - Asigna un customer aleatorio en el campo estándar 'customer'.
    
    Cómo ejecutar:
        bench --site site1.bootcamp console

        from chile_custom.utils.project_random_customer import asignar_cliente_aleatorio_a_proyectos
        asignar_cliente_aleatorio_a_proyectos()
    """

    # Obtener todos los clientes
    customers = frappe.get_all("Customer", pluck="name")

    if not customers:
        print("⚠️ No hay clientes creados en el sistema.")
        return

    # Obtener todos los proyectos
    projects = frappe.get_all("Project", pluck="name")

    if not projects:
        print("⚠️ No hay proyectos en el sistema.")
        return

    print(f"🔎 Encontrados {len(projects)} proyectos y {len(customers)} clientes.")

    # Recorremos los proyectos y asignamos un cliente al azar
    for project_name in projects:
        customer = random.choice(customers)

        doc = frappe.get_doc("Project", project_name)
        doc.customer = customer
        doc.save(ignore_permissions=True)

        print(f"✔️ Proyecto {project_name} → Cliente asignado: {customer}")

    frappe.db.commit()
    print("\n🎉 Asignación completada correctamente.")
    
    
    
    
def ajustar_fechas_proyectos():
    """
    Ajusta fechas de proyectos:
    - Nueva fecha de inicio aleatoria entre 01-02-2024 y 30-11-2025.
    - Mantiene duración original.
    - Garantiza que la fecha final no pase de 30-11-2025.
    """

    start_min = date(2024, 2, 1)
    end_max  = date(2025, 11, 30)

    projects = frappe.get_all(
        "Project",
        fields=["name", "expected_start_date", "expected_end_date"]
    )

    count_ok = 0
    skipped = 0

    for p in projects:
        start = p.expected_start_date
        end = p.expected_end_date

        if not start or not end:
            skipped += 1
            continue

        duration = (end - start).days
        if duration < 1:
            skipped += 1
            continue

        # límite máximo para poder ubicar un proyecto sin pasarse
        latest_allowed_start = end_max - timedelta(days=duration)

        # si la duración es demasiado grande para caber en el rango → recortamos duración
        if latest_allowed_start < start_min:
            # duración demasiado grande → ajustamos duración
            duration = (end_max - start_min).days
            latest_allowed_start = end_max - timedelta(days=duration)

        # elegimos nueva fecha de inicio dentro del rango permitido
        delta_days = (latest_allowed_start - start_min).days
        random_offset = random.randint(0, delta_days)
        new_start = start_min + timedelta(days=random_offset)

        # nueva fecha de fin: no puede pasar end_max
        new_end = new_start + timedelta(days=duration)
        if new_end > end_max:
            new_end = end_max

        # Guardar en DB
        frappe.db.set_value("Project", p.name, "expected_start_date", new_start)
        frappe.db.set_value("Project", p.name, "expected_end_date", new_end)

        print(f"📌 {p.name}: {start}–{end} → {new_start}–{new_end}")

        count_ok += 1

    print("------------------------------------------------------")
    print(f"✔ Ajustados correctamente: {count_ok}")
    print(f"⚠ Omitidos: {skipped}")
    print("------------------------------------------------------")
    
    
    
    

import frappe

def fix_project_in_sinv_items(project_name: str | None = None):
    """
    Asigna el proyecto del parent (Sales Invoice.project)
    a todos los ítems de cada Sales Invoice.

    Si project_name se entrega:
        → solo procesa SINV con ese proyecto.

    Si project_name es None:
        → procesa TODAS las SINV que tengan project en el parent.

    Uso:
        fix_project_in_sinv_items("PROJ-0003")
    """

    # -------------------------------------------------
    # Filtrar SINV por proyecto (o todas si no se entrega)
    # -------------------------------------------------
    filters = {"docstatus": 1}
    if project_name:
        filters["project"] = project_name

    sinv_list = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=["name", "project"]
    )

    if not sinv_list:
        print("⚠️ No se encontraron Sales Invoice que procesar.")
        return

    total_actualizados = 0

    # -------------------------------------------------
    # Procesar cada SINV
    # -------------------------------------------------
    for sinv in sinv_list:
        if not sinv.project:
            # SINV sin project → no hacemos nada
            continue

        doc = frappe.get_doc("Sales Invoice", sinv.name)
        updated = False

        for item in doc.items:
            if item.project != sinv.project:
                item.project = sinv.project
                updated = True

        if updated:
            doc.flags.ignore_mandatory = True
            doc.save(ignore_permissions=True)
            total_actualizados += 1
            print(f"🔧 Actualizado {sinv.name}: items ahora tienen project='{sinv.project}'")

    frappe.db.commit()

    print(f"\n🏁 Proceso completado. Facturas actualizadas: {total_actualizados}")
    return total_actualizados
