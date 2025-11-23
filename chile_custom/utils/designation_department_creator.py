# File: chile_custom/scripts/demo_hr.py
# -----------------------------------------------------------------------------
# Script para poblar datos demo de Departments y Designations para una
# empresa constructora en Chile.
#
# - Elimina todos los departamentos hijos de "All Departments".
# - Crea una lista de departamentos en español.
# - Elimina todas las designaciones existentes.
# - Inserta una lista amplia de cargos administrativos, técnicos y de obra.
#
# Ejecución desde consola:
# bench --site [sitio] execute chile_custom.scripts.demo_hr.seed_departments_and_designations
#
# Autor: Antonio Cañada Momblant
# Proyecto: Bootcamp ERPNext 2025
# -----------------------------------------------------------------------------

import frappe


# ------------------------------------------------------------------------
# LISTA DE DEPARTAMENTOS (adaptados a una constructora en Chile)
# ------------------------------------------------------------------------
DEPARTAMENTOS = [
    "Contabilidad",
    "Servicio al Cliente",
    "Despacho",
    "Recursos Humanos",
    "Legal",
    "Gerencia",
    "Marketing",
    "Operaciones",
    "Producción",
    "Compras",
    "Gestión de Calidad",
    "Investigación y Desarrollo",
    "Ventas",
    "Oficina Técnica",
    "Obras",
    "Logística",
    "Maquinaria",
    "Prevención de Riesgos",
]

# ------------------------------------------------------------------------
# LISTA COMPLETA DE DESIGNACIONES (administrativas + obra)
# ------------------------------------------------------------------------
DESIGNATIONS = [

    # ---------------------------
    # CORPORATIVAS / ADMIN
    # ---------------------------
    "Contador",
    "Asistente Administrativo",
    "Oficial Administrativo",
    "Analista",
    "Asociado",
    "Analista de Negocios",
    "Gerente de Desarrollo de Negocios",
    "Consultor",
    "Director Ejecutivo (CEO)",
    "Director Financiero (CFO)",
    "Director de Operaciones (COO)",
    "Director de Tecnología (CTO)",
    "Asistente Ejecutivo",
    "Gerente de Finanzas",
    "Gerente de Recursos Humanos",
    "Jefe de Marketing y Ventas",
    "Gerente",
    "Director General",
    "Gerente de Marketing",
    "Especialista en Marketing",
    "Presidente",
    "Gerente de Producto",
    "Gerente de Proyecto",
    "Investigador",
    "Secretaria",
    "Vicepresidente",

    # ---------------------------
    # COMERCIALES
    # ---------------------------
    "Representante de Servicio al Cliente",
    "Representante de Ventas",

    # ---------------------------
    # TECNOLOGÍA
    # ---------------------------
    "Diseñador",
    "Ingeniero",
    "Desarrollador de Software",

    # ---------------------------
    # OBRA (CONSTRUCCIÓN)
    # ---------------------------
    "Administrador de Obra",
    "Jefe de Obra",
    "Residente de Obra",
    "Supervisor de Obra",
    "Capataz",
    "Maestro Primera",
    "Maestro Segunda",
    "Ayudante",
    "Trazador",
    "Albañil",
    "Carpintero",
    "Enfierrador",
    "Gasfiter",
    "Electricista",
    "Soldador",
    "Pintor",
    "Yesero",
    "Pavimentador",
    "Instalador de Cerámica",
    "Instalador Sanitario",
    "Instalador Eléctrico",

    # ---------------------------
    # OFICINA TÉCNICA
    # ---------------------------
    "Jefe de Oficina Técnica",
    "Profesional de Oficina Técnica",
    "Control de Documentos",
    "Dibujante Técnico",
    "Topógrafo",

    # ---------------------------
    # CALIDAD / SEGURIDAD / MEDIOAMBIENTE
    # ---------------------------
    "Supervisor de Calidad",
    "Inspector de Calidad",
    "Prevencionista de Riesgos",
    "Asistente de Prevención",
    "Encargado de Medio Ambiente",

    # ---------------------------
    # LOGÍSTICA - BODEGA - MAQUINARIA
    # ---------------------------
    "Bodeguero",
    "Ayudante de Bodega",
    "Encargado de Activos",
    "Operador de Maquinaria Pesada",
    "Operador de Retroexcavadora",
    "Operador de Excavadora",
    "Operador de Grúa Horquilla",
    "Chofer",
    "Chofer Camión Pluma",
]


# -----------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -----------------------------------------------------------------------------
def seed_departments_and_designations():
    """
    Crea datos de prueba para departamentos y designaciones en ERPNext,
    específico para una constructora en Chile.

    - Borra todos los Department que sean hijos de "All Departments".
    - Inserta nuevos departamentos.
    - Borra todas las Designations existentes.
    - Inserta nuevas designaciones.

    Ejecutar con:
        bench --site [site] execute chile_custom.scripts.demo_hr.seed_departments_and_designations
    """

    # -------------------------------------------------------------------------
    # 1. OBTENER EL ROOT "All Departments"
    # -------------------------------------------------------------------------
    root = frappe.db.get_value(
        "Department",
        {"is_group": 1, "lft": 1},
        "name"
    )

    if not root:
        frappe.throw("No se encontró el departamento raíz (All Departments).")

    # -------------------------------------------------------------------------
    # 2. ELIMINAR SOLO LOS HIJOS DEL ROOT
    # -------------------------------------------------------------------------
    child_departments = frappe.get_all(
        "Department",
        filters={"parent_department": root},
        pluck="name"
    )

    for dept in child_departments:
        frappe.delete_doc("Department", dept, force=1)

    frappe.db.commit()

    # -------------------------------------------------------------------------
    # 3. CREAR NUEVOS DEPARTAMENTOS (todos bajo el root)
    # -------------------------------------------------------------------------
    for d in DEPARTAMENTOS:
        frappe.get_doc({
            "doctype": "Department",
            "department_name": d,
            "parent_department": root,
            "is_group": 0
        }).insert()

    frappe.db.commit()

    # -------------------------------------------------------------------------
    # 4. ELIMINAR TODAS LAS DESIGNACIONES
    # -------------------------------------------------------------------------
    existing_designations = frappe.get_all("Designation", pluck="name")

    for des in existing_designations:
        frappe.delete_doc("Designation", des, force=1)

    frappe.db.commit()

    # -------------------------------------------------------------------------
    # 5. CREAR NUEVAS DESIGNACIONES
    # -------------------------------------------------------------------------
    for d in DESIGNATIONS:
        frappe.get_doc({
            "doctype": "Designation",
            "designation_name": d
        }).insert()

    frappe.db.commit()

    return "Departamentos y designaciones creados exitosamente 🎉"
