"""
================================================================================
DEMO PROJECT GENERATOR – Chile Custom
================================================================================

Este script crea una DEMO realista de proyectos para el Bootcamp de ERPNext.

FUNCIONALIDADES PRINCIPALES
---------------------------
1. Elimina TODOS los "Project Type" existentes y los reemplaza por:
   - Edificación
   - Plantas Fotovoltaicas
   - Centrales hidráulicas
   - Minería
   - Arriendo de Maquinaria

2. Genera una cantidad N de proyectos con:
   - Nombre coherente según el tipo de proyecto
   - Prefijo único (PFMO, PFMO2, etc.)
   - País = Chile
   - Comuna, Región y Número de Región obtenidas desde regiones.py
   - Latitud y Longitud aleatorias pero dentro del rango geográfico chileno
   - Dirección ficticia usando Faker
   - URL Google Maps basada en lat/lon
   - Fechas esperadas (inicio y fin) desde el presente (18-11-2025) hacia adelante
   - Notas HTML generadas según tipo de proyecto

REQUISITOS
----------
- Tener definidos los Custom Fields:
    project_country, project_comuna, project_region,
    project_prefix, project_latitude, project_longitude,
    project_maps_url, project_address

CÓMO EJECUTAR
-------------
Desde bench console:

    bench --site site1.bootcamp console
    >>> from chile_custom.demo.create_demo_projects import create_demo_projects
    >>> create_demo_projects()

NOTA
----
Este script es solo para poblar una DEMO.
No usar en producción.

================================================================================
"""

import random
import frappe
from faker import Faker
from datetime import datetime, timedelta
from chile_custom.constants.regiones import regiones


fake = Faker("es_CL")

# =============================================================================
# UTILIDADES
# =============================================================================

def get_random_region_and_comuna():
    """Escoge una región y comuna aleatorias desde regiones.py."""
    r = random.choice(regiones)
    comuna = random.choice(r["comunas"])
    return r["region"], r["numero"], comuna


def generate_random_lat_long():
    """Genera lat/long realistas para Chile."""
    lat = random.uniform(-18.5, -54.0)
    lon = random.uniform(-66.0, -75.0)
    return round(lat, 6), round(lon, 6)


def project_prefix_from_name(name):
    """Genera abreviatura: Planta Fotovoltaica Molinos -> PFMO."""
    return "".join(w[0].upper() for w in name.split() if w)


def get_existing_prefixes():
    """Obtiene todos los prefijos de proyectos existentes en ERP."""
    rows = frappe.get_all("Project", fields=["project_prefix"])
    return {r["project_prefix"] for r in rows if r["project_prefix"]}


def ensure_unique_prefix(prefix, used_prefixes):
    """
    Asegura que el prefijo no esté repetido.
    Si existe PFMO -> PFMO2 -> PFMO3
    """
    original = prefix
    counter = 1
    while prefix in used_prefixes:
        counter += 1
        prefix = f"{original}{counter}"
    used_prefixes.add(prefix)
    return prefix


def generate_project_notes(project_type, comuna):
    """Genera HTML contextual para el campo Notes según tipo de proyecto."""
    if project_type == "Plantas Fotovoltaicas":
        mw = random.randint(30, 250)
        return f"""
        <h3>Proyecto Fotovoltaico</h3>
        <p>La planta tendrá una capacidad instalada de <strong>{mw} MW</strong>, ubicada en {comuna}.</p>
        <p>Integrará energía renovable al sistema eléctrico nacional.</p>
        """

    if project_type == "Edificación":
        m2 = random.randint(4000, 60000)
        return f"""
        <h3>Proyecto de Edificación</h3>
        <p>Edificio de <strong>{m2:,} m²</strong> útiles en la comuna de {comuna}.</p>
        <p>Incluye áreas técnicas, estacionamientos y certificación LEED.</p>
        """

    if project_type == "Centrales hidráulicas":
        mw = random.randint(10, 300)
        return f"""
        <h3>Central Hidroeléctrica</h3>
        <p>Producción estimada de <strong>{mw} MW</strong>.</p>
        <p>Incluye obras civiles, bocatomas, túneles y casa de máquinas.</p>
        """

    if project_type == "Minería":
        tons = random.randint(20000, 300000)
        return f"""
        <h3>Proyecto Minero</h3>
        <p>Extracción estimada de <strong>{tons:,} ton/mes</strong>.</p>
        <p>Incluye caminos de acceso, plataformas y sistemas de procesamiento.</p>
        """

    if project_type == "Arriendo de Maquinaria":
        return f"""
        <h3>Servicio de Arriendo de Maquinaria</h3>
        <p>Base en la comuna de {comuna}, con flota de maquinaria pesada.</p>
        <p>Incluye grúas, retroexcavadoras y equipos especializados.</p>
        """

    return "<p>Proyecto sin notas específicas.</p>"


# =============================================================================
# SCRIPT PRINCIPAL
# =============================================================================

def create_demo_projects():

    # ----------------------------------------------
    # 1) Eliminar y recrear Project Types
    # ----------------------------------------------
    frappe.db.delete("Project Type")

    project_types = [
        "Edificación",
        "Plantas Fotovoltaicas",
        "Centrales hidráulicas",
        "Minería",
        "Arriendo de Maquinaria",
    ]

    for t in project_types:
        d = frappe.new_doc("Project Type")
        d.project_type = t
        d.insert()

    print("✔ Project Types creados.")

    # ----------------------------------------------
    # 2) Obtener prefijos existentes en BD
    # ----------------------------------------------
    used_prefixes = get_existing_prefixes()

    # ----------------------------------------------
    # 3) Crear proyectos demo
    # ----------------------------------------------
    N = 15  # cantidad de proyectos demo

    today = datetime(2025, 11, 18)

    for i in range(N):
        project_type = random.choice(project_types)

        # Nombre del proyecto
        city = fake.city()
        if project_type == "Plantas Fotovoltaicas":
            name = f"Planta Fotovoltaica {city}"
        elif project_type == "Edificación":
            name = f"Edificio {fake.last_name()} Center"
        elif project_type == "Centrales hidráulicas":
            name = f"Central Hidroeléctrica {city}"
        elif project_type == "Minería":
            name = f"Proyecto Minero {city}"
        else:
            name = f"Arriendo Maquinaria {city}"

        # Ubicación
        region, region_num, comuna = get_random_region_and_comuna()
        lat, lon = generate_random_lat_long()
        direccion = fake.address().replace("\n", ", ")

        # Fechas
        start = today + timedelta(days=random.randint(5, 60))
        end = start + timedelta(days=random.randint(120, 720))

        # Prefijo único
        prefix_base = project_prefix_from_name(name)
        prefix = ensure_unique_prefix(prefix_base, used_prefixes)

        # Notas HTML
        notes = generate_project_notes(project_type, comuna)

        # Crear Project
        p = frappe.new_doc("Project")
        p.project_name = name
        p.project_type = project_type
        p.project_country = "Chile"
        p.project_comuna = comuna
        p.project_region = region
        p.project_prefix = prefix
        p.project_latitude = lat
        p.project_longitude = lon
        p.project_maps_url = f"https://www.google.com/maps?q={lat},{lon}"
        p.project_address = direccion
        p.expected_start_date = start
        p.expected_end_date = end
        p.notes = notes

        p.insert()
        p.save()

        print(f"✔ Proyecto creado: {name} ({prefix}) — {comuna}, {region}")

    frappe.db.commit()
    print("\n🎉 DEMO completa: proyectos creados exitosamente.\n")
    
    
    
# (lat_min, lat_max, lon_min, lon_max)
regiones_bbox = {
    "XV Región de Arica y Parinacota": (-19.0, -17.4, -70.5, -69.0),
    "I Región de Tarapacá": (-21.0, -19.0, -70.3, -68.5),
    "II Región de Antofagasta": (-25.5, -21.0, -70.0, -66.5),
    "III Región de Atacama": (-29.5, -25.5, -71.0, -69.0),
    "IV Región de Coquimbo": (-32.3, -29.5, -71.8, -70.2),
    "V Región de Valparaíso": (-33.1, -32.0, -72.1, -70.5),
    "XIII Región Metropolitana de Santiago": (-34.3, -32.8, -71.3, -70.3),
    "VI Región del Libertador General Bernardo O’Higgins": (-35.2, -33.8, -71.8, -70.5),
    "VII Región del Maule": (-36.4, -34.9, -72.3, -70.3),
    "XVI Región de Ñuble": (-37.3, -36.0, -72.3, -71.2),
    "VIII Región del Biobío": (-38.6, -36.8, -73.3, -71.1),
    "IX Región de La Araucanía": (-39.5, -37.8, -73.5, -71.3),
    "XIV Región de Los Ríos": (-40.5, -39.5, -73.7, -71.7),
    "X Región de Los Lagos": (-43.0, -40.0, -74.3, -72.0),
    "XI Región Aysén del General Carlos Ibáñez del Campo": (-47.1, -43.0, -75.0, -72.0),
    "XII Región de Magallanes y Antártica Chilena": (-55.0, -47.1, -75.0, -67.0),
}


def generate_region_based_lat_long(region):
    """
    Genera lat/long realistas basadas en la región indicada.
    Evita coordenadas en el océano o fuera de Chile.
    """
    if region not in regiones_bbox:
        # fallback general Chile (rango completo)
        lat = random.uniform(-55.0, -17.4)
        lon = random.uniform(-75.0, -66.5)
        return round(lat, 6), round(lon, 6)

    lat_min, lat_max, lon_min, lon_max = regiones_bbox[region]
    lat = random.uniform(lat_min, lat_max)
    lon = random.uniform(lon_min, lon_max)
    return round(lat, 6), round(lon, 6)


# =============================================================
# FUNCIÓN: CORREGIR COORDENADAS DE PROJECT
# =============================================================

def build_google_maps_url(lat, lon):
    return f"https://www.google.com/maps?q={lat},{lon}"



def fix_project_lat_lon():
    """
    Recorre todos los proyectos con país Chile y corrige:
    - región (si está vacía)
    - latitud y longitud (según región real)
    - Google Maps URL
    """

    projects = frappe.get_all(
        "Project",
        fields=["name", "project_country", "project_comuna", "project_region"]
    )

    count = 0

    for p in projects:

        # Solo corregimos proyectos chilenos con comuna válida
        if p.project_country != "Chile" or not p.project_comuna:
            continue

        region = p.project_region

        lat, lon = generate_region_based_lat_long(region)
        maps_url = build_google_maps_url(lat, lon)

        doc = frappe.get_doc("Project", p.name)
        doc.project_region = region
        doc.project_latitude = lat
        doc.project_longitude = lon
        doc.project_maps_url = maps_url
        doc.save()

        count += 1
        print(f"✔ Corregido: {p.name} ({p.project_comuna}) → {lat}, {lon}")

    frappe.db.commit()

    print(f"\n🎉 Corrección completa: {count} proyectos actualizados.\n")
    

# =============================================================
# FUNCIÓN: CORREGIR DIRECCIÓN SEGÚN COMUNA
# =============================================================
    
    
def get_region_by_comuna(comuna):
    """Busca la región según la comuna, usando regiones.py."""
    for r in regiones:
        if comuna in r["comunas"]:
            return r["region"]
    return None


def build_address(comuna, region):
    """
    Construye una dirección realista usando Faker + comuna + región.
    Ejemplo:
        'Calle Los Alerces 2451, Comuna de Buin, Región Metropolitana de Santiago, Chile'
    """
    calle = fake.street_name()
    numero = fake.building_number()
    depto = fake.secondary_address() if fake.boolean(chance_of_getting_true=30) else ""

    direccion = f"{calle} {numero}"
    if depto:
        direccion += f", {depto}"

    direccion += f", Comuna de {comuna}, {region}, Chile"

    return direccion


def fix_project_addresses():
    """
    Recorre todos los proyectos chilenos y les asigna una dirección
    coherente y realista usando Faker, basada en la comuna.
    """

    projects = frappe.get_all(
        "Project",
        fields=["name", "project_country", "project_comuna", "project_region"]
    )

    count = 0

    for p in projects:

        if p.project_country != "Chile":
            continue

        if not p.project_comuna:
            continue

        region = p.project_region or get_region_by_comuna(p.project_comuna)

        direccion = build_address(p.project_comuna, region)

        doc = frappe.get_doc("Project", p.name)
        doc.project_address = direccion
        doc.project_region = region  # por si estaba vacío
        doc.save()

        count += 1
        print(f"✔ Dirección corregida: {p.name} → {direccion}")

    frappe.db.commit()
    print(f"\n🎉 Direcciones corregidas exitosamente: {count} proyectos.\n")