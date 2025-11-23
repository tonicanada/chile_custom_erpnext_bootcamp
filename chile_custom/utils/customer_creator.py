# ===========================================================
# SCRIPT PARA DEMO ERPNext — VERSION FUNCIONAL
# ===========================================================
# Llama a:
#
#    generar_demo_clientes(120)
#
# Y el script hará:
# 1) Reset de Industry Type
# 2) Creación de nuevas Industry
# 3) Generación de N clientes (sin duplicados)
#
# Listo para usar en demos del Bootcamp
# ===========================================================

import random
import unicodedata
import frappe

# Probabilidades para tipo de cliente
PROB_COMERCIAL = 0.90
PROB_GOBIERNO  = 0.10

# Rubros para generar nombres
RUBROS_COMERCIALES = [
    "Inmobiliaria", "Constructora", "Energía Solar", "Energía Eólica",
    "Servicios Industriales", "Minería", "Agroindustria",
    "Logística", "Consultora", "Importadora", "Transporte",
    "Soluciones Tecnológicas", "Servicios Ambientales"
]

RUBROS_GOBIERNO = [
    "Municipalidad de", "Ministerio de", "Empresa Nacional de",
    "Corporación Pública", "Servicio Regional de"
]

# Industrias para Industry Type
INDUSTRIAS_COMERCIALES = [
    "Construcción",
    "Inmobiliaria",
    "Energía",
    "Minería",
    "Manufactura",
    "Servicios Industriales",
    "Transporte",
    "Tecnologías de la Información",
    "Logística",
    "Agroindustria"
]

INDUSTRIAS_GOBIERNO = [
    "Administración Pública",
    "Servicios Públicos",
    "Infraestructura",
    "Obras Públicas",
    "Salud Pública",
    "Educación Pública"
]

# Ciudades
CIUDADES = [
    "Santiago", "Valparaíso", "Concepción", "La Serena", "Temuco",
    "Antofagasta", "Iquique", "Rancagua", "Talca", "Arica",
    "Puerto Montt", "Coyhaique"
]

# Dominios fake
DOMINIOS_FAKE = [
    "empresa-demo.cl", "clientefake.cl", "negociosxyz.cl",
    "corp-industrial.cl", "servicioschile.cl"
]


# -----------------------------------------------------------
# UTILIDADES
# -----------------------------------------------------------
def calcular_dv(rut):
    rut = str(rut)
    reversed_digits = map(int, reversed(rut))
    factors = [2,3,4,5,6,7]
    s = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
    dv = 11 - (s % 11)
    if dv == 11: return "0"
    if dv == 10: return "K"
    return str(dv)


def generar_rut_unico(usados):
    while True:
        base = random.randint(90000000, 99999999)
        dv = calcular_dv(base)
        rut = f"{base}-{dv}"
        if rut not in usados:
            usados.add(rut)
            return rut


def normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.replace("ñ","n").replace("Ñ","N")


def generar_nombre_unico(tipo, usados):
    while True:
        if tipo == "Comercial":
            nombre = f"{random.choice(RUBROS_COMERCIALES)} {random.choice(CIUDADES)} SpA"
        else:
            nombre = f"{random.choice(RUBROS_GOBIERNO)} {random.choice(CIUDADES)}"

        if nombre not in usados:
            usados.add(nombre)
            return nombre


# -----------------------------------------------------------
# REINICIAR INDUSTRY TYPE
# -----------------------------------------------------------
def reset_industries():
    print("→ Eliminando Industry Type existentes...")
    existentes = frappe.get_all("Industry Type", pluck="name")

    for ind in existentes:
        try:
            frappe.delete_doc("Industry Type", ind, force=1, ignore_permissions=True)
        except:
            pass

    frappe.db.commit()

    print("→ Creando Industry Type nuevos...")
    todas = INDUSTRIAS_COMERCIALES + INDUSTRIAS_GOBIERNO

    for ind in todas:
        doc = frappe.get_doc({
            "doctype": "Industry Type",
            "industry": ind
        })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()


# -----------------------------------------------------------
# CREAR CLIENTES
# -----------------------------------------------------------
def crear_clientes(n):
    print(f"→ Creando {n} clientes demo...")

    ruts_usados = set()
    nombres_usados = set()
    creados = []

    for _ in range(n):

        tipo = "Comercial" if random.random() < PROB_COMERCIAL else "Gobierno"
        nombre = generar_nombre_unico(tipo, nombres_usados)
        rut = generar_rut_unico(ruts_usados)

        industria = random.choice(INDUSTRIAS_COMERCIALES if tipo=="Comercial" else INDUSTRIAS_GOBIERNO)

        dominio = random.choice(DOMINIOS_FAKE)
        web = f"https://www.{normalizar(nombre.lower().replace(' ', ''))}.{dominio}"

        cust = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": nombre,
            "customer_type": "Company",
            "customer_group": tipo,
            "territory": "Chile",
            "tax_id": rut,
            "website": web,
            "industry": industria
        })
        cust.insert(ignore_permissions=True)
        creados.append(cust.name)

    frappe.db.commit()
    print(f"→ {len(creados)} clientes creados.")
    return creados


# -----------------------------------------------------------
# FUNCIÓN PRINCIPAL QUE LLAMAS DESDE LA CONSOLA
# -----------------------------------------------------------
def generar_demo_clientes(n):
    print("\n=== INICIO GENERACIÓN DEMO ===\n")

    reset_industries()
    clientes = crear_clientes(n)

    print("\n=== FIN DEMO ===")
    return clientes
