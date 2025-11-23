# archivo sugerido: chile_custom/utils/employee_demo_creator.py

# Ejemplo
# def create_demo_employees_for_constructora(
#     company: str,
#     total_active: int = 500,
#     total_left: int = 100,
#     email_domain: str = "horizonte.cl",
#     department_suffix: str = " - CH",
#     seed: int | None = 42,
# ):


import random
import unicodedata
from datetime import date, timedelta

import frappe
from faker import Faker
from frappe.utils import getdate, today

# -------------------------
# CONFIGURACIÓN GENERAL
# -------------------------

DEPARTMENTS = [
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

# Designations tal cual los pasaste
ALL_DESIGNATIONS = [
    # CORPORATIVAS / ADMIN
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

    # COMERCIALES
    "Representante de Servicio al Cliente",
    "Representante de Ventas",

    # TECNOLOGÍA
    "Diseñador",
    "Ingeniero",
    "Desarrollador de Software",

    # OBRA (CONSTRUCCIÓN)
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

    # OFICINA TÉCNICA
    "Jefe de Oficina Técnica",
    "Profesional de Oficina Técnica",
    "Control de Documentos",
    "Dibujante Técnico",
    "Topógrafo",

    # CALIDAD / SEGURIDAD / MEDIOAMBIENTE
    "Supervisor de Calidad",
    "Inspector de Calidad",
    "Prevencionista de Riesgos",
    "Asistente de Prevención",
    "Encargado de Medio Ambiente",

    # LOGÍSTICA - BODEGA - MAQUINARIA
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



EMPLOYMENT_TYPES_PRIORITY = [
    "Contrato Indefinido",
    "Contrato a Plazo Fijo",
    "Trabajo por Faena",
    "Tiempo Completo",
    "Part-Time",
    "Jornada Excepcional",
    "Honorarios",
    "Práctica Profesional",
    "Aprendiz",
    "Subcontrato",
]

# Designations de “oficina / administración”
ADMIN_DESIGNATIONS = {
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
    "Diseñador",
    "Ingeniero",
    "Desarrollador de Software",
    "Jefe de Oficina Técnica",
    "Profesional de Oficina Técnica",
    "Control de Documentos",
    "Dibujante Técnico",
    "Topógrafo",
    "Supervisor de Calidad",
    "Inspector de Calidad",
    "Prevencionista de Riesgos",
    "Asistente de Prevención",
    "Encargado de Medio Ambiente",
    "Encargado de Activos",
}

# Designations claramente de “obrero / terreno”
OBRERO_DESIGNATIONS = {
    "Administrador de Obra",  # admin de obra, pero lo tratamos como “obra” para sueldos
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
    "Bodeguero",
    "Ayudante de Bodega",
    "Operador de Maquinaria Pesada",
    "Operador de Retroexcavadora",
    "Operador de Excavadora",
    "Operador de Grúa Horquilla",
    "Chofer",
    "Chofer Camión Pluma",
}

# Designations “comerciales”
COMERCIAL_DESIGNATIONS = {
    "Representante de Servicio al Cliente",
    "Representante de Ventas",
}

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
MARITAL_STATUSES = ["Single", "Married", "Divorced", "Widowed"]

COMPANY_START_DATE = date(2013, 1, 1)

try:
    from chile_custom.constants.regiones import regiones
except Exception:
    regiones = {}

fake = Faker("es_CL")


# -------------------------
# UTILIDADES
# -------------------------

def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(ch for ch in value if ch in allowed)


def generate_rut(existing_ruts: set, min_num=60000000, max_num=99999999) -> str:
    """Genera un RUT chileno válido con DV, en un rango alto para reducir
    probabilidad de chocar con personas reales.
    """
    while True:
        base = random.randint(min_num, max_num)
        dv = calculate_rut_dv(base)
        rut = f"{base}-{dv}"
        if rut not in existing_ruts:
            existing_ruts.add(rut)
            return rut


def calculate_rut_dv(number: int) -> str:
    """Cálculo estándar módulo 11 para DV de RUT."""
    s = 0
    multiplier = 2
    for d in reversed(str(number)):
        s += int(d) * multiplier
        multiplier += 1
        if multiplier > 7:
            multiplier = 2
    remainder = 11 - (s % 11)
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def generate_gender() -> str:
    # 65% male, 35% female
    return "Male" if random.random() < 0.65 else "Female"


def generate_birth_date() -> date:
    """Genera una fecha de nacimiento para que la mayoría tenga entre 30 y 40 años."""
    today_date = getdate(today())
    # edad ~ N(35, 7), recortada entre 20 y 60
    age = int(random.gauss(35, 7))
    age = max(20, min(60, age))
    year = today_date.year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # para evitar problemas
    return date(year, month, day)


def generate_join_date_group(birth_date: date, group: str) -> date:
    """group: 'gt7', '3to7', 'lt3' años de antigüedad."""
    today_date = getdate(today())
    min_date = COMPANY_START_DATE

    seven_years_ago = today_date - timedelta(days=7 * 365)
    three_years_ago = today_date - timedelta(days=3 * 365)

    if group == "gt7":
        start = min_date
        end = seven_years_ago
    elif group == "3to7":
        start = seven_years_ago
        end = three_years_ago
    else:  # "lt3"
        start = three_years_ago
        end = today_date

    # no antes de los 18 años
    adult_date = birth_date + timedelta(days=18 * 365)
    if adult_date > start:
        start = adult_date

    if start > end:
        # fallback: justo después de ser mayor de edad
        return adult_date

    delta_days = (end - start).days
    offset = random.randint(0, max(delta_days, 0))
    return start + timedelta(days=offset)


def generate_mobile() -> str:
    number = "9" + "".join(str(random.randint(0, 9)) for _ in range(8))
    return f"+56{number}"


def pick_department_and_designation() -> tuple[str, str]:
    dept = random.choice(DEPARTMENTS)

    # 1) Selección básica según departamento (como ya tienes)
    if dept == "Contabilidad":
        posibles = ["Contador", "Analista", "Asistente Administrativo"]
    elif dept == "Recursos Humanos":
        posibles = ["Gerente de Recursos Humanos", "Analista", "Asistente Administrativo"]
    elif dept == "Gerencia":
        posibles = [
            "Director Ejecutivo (CEO)",
            "Director General",
            "Director Financiero (CFO)",
            "Director de Operaciones (COO)",
            "Presidente",
            "Gerente",
            "Gerente de Proyecto",
        ]
    elif dept == "Oficina Técnica":
        posibles = [
            "Jefe de Oficina Técnica",
            "Profesional de Oficina Técnica",
            "Dibujante Técnico",
            "Topógrafo",
            "Control de Documentos",
        ]
    elif dept == "Obras":
        posibles = list(OBRERO_DESIGNATIONS)
    elif dept in {"Logística", "Maquinaria", "Despacho"}:
        posibles = [
            "Bodeguero",
            "Ayudante de Bodega",
            "Operador de Maquinaria Pesada",
            "Operador de Retroexcavadora",
            "Operador de Excavadora",
            "Operador de Grúa Horquilla",
            "Chofer",
            "Chofer Camión Pluma",
        ]
    else:
        posibles = ALL_DESIGNATIONS

    # 2) Excluir designaciones que no pueden ir en ese departamento
    if dept in DESIGNATION_EXCLUSIONS:
        excl = DESIGNATION_EXCLUSIONS[dept]
        posibles = [d for d in posibles if d not in excl]

    designation = random.choice(posibles)
    return dept, designation



def classify_employee(department: str, designation: str) -> str:
    """Devuelve 'admin' o 'obra' para decidir employment_type, sueldo, etc."""
    if designation in OBRERO_DESIGNATIONS or department in {"Obras", "Maquinaria", "Logística", "Producción"}:
        return "obra"
    return "admin"


def choose_employment_type(category: str) -> str:
    """Respeta aprox 30% indefinido, 40% plazo fijo, 20% faena en global."""
    # categorías simplificadas por tipo de trabajo
    if category == "admin":
        # más indefinido en administración
        choices = [
            "Contrato Indefinido",
            "Contrato a Plazo Fijo",
            "Tiempo Completo",
            "Honorarios",
            "Práctica Profesional",
        ]
        weights = [0.6, 0.2, 0.1, 0.05, 0.05]
    else:  # obra
        choices = [
            "Contrato a Plazo Fijo",
            "Trabajo por Faena",
            "Contrato Indefinido",
            "Subcontrato",
            "Jornada Excepcional",
        ]
        weights = [0.5, 0.3, 0.1, 0.05, 0.05]

    return random.choices(choices, weights=weights, k=1)[0]


def generate_ctc(category: str, designation: str) -> float:
    """Sueldo bruto mensual aproximado en CLP (muy aproximado)."""
    # directores / alta gerencia
    if designation in {"Director Ejecutivo (CEO)", "Presidente"}:
        return random.randint(7000000, 10000000)
    if designation in {"Director Financiero (CFO)", "Director de Operaciones (COO)", "Director General"}:
        return random.randint(5000000, 7000000)
    if designation.startswith("Gerente"):
        return random.randint(2500000, 4500000)
    if designation in {"Jefe de Obra", "Administrador de Obra", "Jefe de Oficina Técnica"}:
        return random.randint(2500000, 4000000)
    if designation in {"Ingeniero", "Profesional de Oficina Técnica", "Topógrafo"}:
        return random.randint(1800000, 2800000)

    if category == "admin":
        return random.randint(900000, 1800000)

    # obreros
    if designation in {"Capataz", "Maestro Primera"}:
        return random.randint(900000, 1300000)
    if designation in {
        "Maestro Segunda",
        "Albañil",
        "Carpintero",
        "Enfierrador",
        "Electricista",
        "Gasfiter",
        "Soldador",
        "Yesero",
        "Pavimentador",
        "Instalador de Cerámica",
        "Instalador Sanitario",
        "Instalador Eléctrico",
    }:
        return random.randint(750000, 1100000)

    # ayudantes, bodegas, choferes
    return random.randint(650000, 950000)


def generate_company_email(first_name: str, last_name: str, domain: str, used_emails: set) -> str:
    # last_name incluye los dos apellidos, tomamos el primero
    parts = last_name.split()
    first_surname = parts[0] if parts else last_name
    base = slugify(first_name[0] + first_surname)
    email = f"{base}@{domain}"
    counter = 2
    while email in used_emails:
        email = f"{base}{counter}@{domain}"
        counter += 1
    used_emails.add(email)
    return email


def generate_personal_email(first_name: str, last_name: str) -> str:
    providers = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]
    provider = random.choice(providers)
    base = slugify(first_name + "." + last_name.replace(" ", ""))
    base = base or "usuario"
    if random.random() < 0.5:
        base = f"{base}{random.randint(1, 99)}"
    return f"{base}@{provider}"


def random_region_and_city() -> tuple[str, str]:
    """
    Devuelve (city, region), compatible con estructuras como:

    regiones = [
        {
            "region": "II Región de Antofagasta",
            "numero": "II",
            "comunas": ["Antofagasta", "Calama", ...]
        },
        ...
    ]
    """

    # Caso: lista de dicts con clave 'region' y 'comunas'
    if isinstance(regiones, list) and regiones and isinstance(regiones[0], dict):
        entry = random.choice(regiones)
        region_name = entry.get("region") or "Región sin nombre"

        comunas = entry.get("comunas") or []
        if comunas:
            comuna = random.choice(comunas)
        else:
            comuna = region_name

        return comuna, region_name

    # Caso: dict clásico {"Región": ["comunas"]}
    if isinstance(regiones, dict) and regiones:
        region_name = random.choice(list(regiones.keys()))
        comunas = regiones.get(region_name) or []
        if comunas:
            return random.choice(comunas), region_name
        return region_name, region_name

    # Fallback si regiones viene vacío
    regiones_demo = {
        "Región Metropolitana": ["Santiago", "Ñuñoa", "Providencia"],
        "Biobío": ["Concepción", "Talcahuano"],
    }

    region_name = random.choice(list(regiones_demo.keys()))
    comuna = random.choice(regiones_demo[region_name])
    return comuna, region_name



def add_education_rows(employee, category: str, birth_date: date, join_date: date):
    """Rellena tabla hija 'education' (Employee Education) con niveles válidos para ERPNext."""
    
    # 1) Opciones según tipo de empleado
    if category == "admin":
        qual_options = [
            ("Universidad de Chile", "Ingeniería Civil", "Graduate"),
            ("Universidad de Santiago", "Ingeniería en Construcción", "Graduate"),
            ("Universidad Católica", "Ingeniería Comercial", "Graduate"),
            ("IP Duoc UC", "Técnico en Construcción", "Under Graduate"),
            ("IP Santo Tomás", "Técnico en Administración", "Under Graduate"),
        ]
    else:
        qual_options = [
            ("Liceo Politécnico", "Enseñanza Media Completa", "Under Graduate"),
            ("Liceo Industrial", "Técnico en Construcción", "Under Graduate"),
        ]

    school, qualification, level = random.choice(qual_options)

    # 2) año de egreso lógico
    year_min = birth_date.year + 18
    year_max = min(join_date.year - 1, birth_date.year + 25)
    if year_max < year_min:
        year_max = year_min
    year_of_passing = random.randint(year_min, year_max)

    # 3) Insertar fila hija
    employee.append(
        "education",
        {
            "school_university": school,
            "qualification": qualification,
            "level": level,  # <-- ahora compatible con ERPNext
            "year_of_passing": year_of_passing,
            "grade": random.choice(["", "5.5", "6.0", "6.5", "7.0"]),
            "subjects": "Construcción, Matemáticas, Gestión",
        },
    )


def add_external_experience_rows(employee, join_date: date, category: str):
    """Rellena 'external_work_history' para algunos empleados."""
    # doctype child típico: Employee External Work History
    # campos comunes: company_name, designation, from_date, to_date, total_experience, contact
    num_jobs = 0
    years_before = (join_date - COMPANY_START_DATE).days / 365.0
    if years_before > 10:
        num_jobs = random.choice([1, 2])
    elif years_before > 3:
        num_jobs = random.choice([0, 1])
    else:
        num_jobs = 0

    if num_jobs == 0:
        return

    current_start = join_date - timedelta(days=int(years_before * 365))
    for _ in range(num_jobs):
        job_length_years = random.uniform(1, 4)
        from_date = current_start
        to_date = from_date + timedelta(days=int(job_length_years * 365))
        if to_date >= join_date:
            to_date = join_date - timedelta(days=30)

        company_name = random.choice(
            ["Constructora Andina", "Obras del Norte", "Inmobiliaria Pacífico", "Servicios Industriales Sur"]
        )
        if category == "admin":
            designation = random.choice(
                ["Analista", "Asistente Administrativo", "Contador", "Ingeniero"]
            )
        else:
            designation = random.choice(
                ["Albañil", "Maestro Primera", "Capataz", "Ayudante"]
            )

        employee.append(
            "external_work_history",
            {
                "company_name": company_name,
                "designation": designation,
                "from_date": from_date,
                "to_date": to_date,
                "total_experience": round(job_length_years, 1),
                "contact": fake.phone_number(),
            },
        )
        current_start = to_date


def add_internal_history_for_cfo(employee, join_date: date, department_suffix: str):
    """Historia interna para el CFO: Jefe de Oficina Técnica -> CFO."""
    from1 = COMPANY_START_DATE
    to1 = date(2018, 12, 31)
    if to1 > join_date:
        to1 = join_date

    employee.append(
        "internal_work_history",
        {
            "from_date": from1,
            "to_date": to1,
            "designation": "Jefe de Oficina Técnica",
            "department": f"Oficina Técnica{department_suffix}",
        },
    )

    from2 = date(2019, 1, 1)
    employee.append(
        "internal_work_history",
        {
            "from_date": from2,
            "to_date": None,
            "designation": "Director Financiero (CFO)",
            "department": f"Gerencia{department_suffix}",
        },
    )



def add_simple_internal_history(employee, join_date: date, designation_old: str, designation_new: str, department: str):
    """Historia simple: un cambio de cargo."""
    mid_date = join_date + timedelta(days=4 * 365)
    if mid_date > getdate(today()):
        mid_date = join_date + timedelta(days=2 * 365)

    employee.append(
        "internal_work_history",
        {
            "from_date": join_date,
            "to_date": mid_date,
            "designation": designation_old,
            "department": department,
        },
    )
    employee.append(
        "internal_work_history",
        {
            "from_date": mid_date,
            "to_date": None,
            "designation": designation_new,
            "department": department,
        },
    )


def set_exit_fields(employee, join_date: date):
    """Completa campos de salida asegurando que relieving_date > join_date."""
    today_date = getdate(today())

    # la salida NO puede ser antes del ingreso + 1 día
    min_leave_date = join_date + timedelta(days=1)

    # si han pasado más de 6 meses, permitimos dejar después de 6 meses
    six_months_after = join_date + timedelta(days=180)
    if six_months_after < today_date:
        min_leave_date = six_months_after

    # la salida no puede ser en el futuro
    max_leave_date = today_date - timedelta(days=1)

    # si por algún motivo el rango queda invertido, corregimos
    if min_leave_date > max_leave_date:
        # significa que el empleado entró demasiado reciente
        # forzamos una salida lógica = ingreso + 1 día
        leave_date = join_date + timedelta(days=1)
    else:
        # elegimos una fecha aleatoria válida
        delta_days = (max_leave_date - min_leave_date).days
        leave_date = min_leave_date + timedelta(days=random.randint(0, delta_days))

    # resignation date: algunos días antes del leave_date
    resignation_date = leave_date - timedelta(days=random.randint(10, 45))
    if resignation_date < join_date:
        resignation_date = join_date

    reasons = [
        "Renuncia voluntaria por mejor oferta laboral",
        "Fin de contrato a plazo fijo",
        "Desvinculación por desempeño",
        "Reducción de personal por reestructuración",
    ]
    feedbacks = [
        "Buen desempeño general, recomendable.",
        "Desempeño correcto, sin observaciones relevantes.",
        "Adecuado en su rol, con oportunidades de mejora.",
        "Relación cordial, se mantiene buena referencia.",
    ]

    employee.status = "Left"
    employee.relieving_date = leave_date
    employee.resignation_letter_date = resignation_date
    employee.reason_for_leaving = random.choice(reasons)
    employee.feedback = random.choice(feedbacks)



def create_address_for_employee(employee, city: str, region: str):
    """Crea un Address y lo asigna como current_address."""
    # address_title = employee.employee_name
    # address_doc = frappe.get_doc(
    #     {
    #         "doctype": "Address",
    #         "address_title": address_title,
    #         "address_type": "Current",
    #         "address_line1": f"Calle {fake.street_name()} {random.randint(10, 999)}",
    #         "city": city,
    #         "state": region,
    #         "country": "Chile",
    #         "pincode": str(random.randint(1000000, 9999999)),
    #     }
    # )
    # address_doc.insert(ignore_permissions=True)
    # employee.current_address = address_doc.name
    
    # Por ahora no creamos direcciones
    pass


GERENTES_POR_DEPARTAMENTO = {}

DESIGNATION_EXCLUSIONS = {
    "Legal": OBRERO_DESIGNATIONS,
    "Marketing": OBRERO_DESIGNATIONS,
    "Contabilidad": {
        "Maestro Primera", "Albañil", "Ayudante", "Chofer", "Soldador", "Carpintero"
    },
    "Ventas": OBRERO_DESIGNATIONS,
    "Servicio al Cliente": OBRERO_DESIGNATIONS,
}


# -------------------------
# FUNCIÓN PRINCIPAL
# -------------------------

def create_demo_employees_for_constructora(
    company: str,
    total_active: int = 500,
    total_left: int = 100,
    email_domain: str = "horizonte.cl",
    department_suffix: str = " - CH",
    seed: int | None = 42,
):
    """
    Crea empleados demo para una constructora chilena.

    Ejemplo desde la consola bench:

        bench --site site1.bootcamp console

        from chile_custom.utils.employee_demo_creator import create_demo_employees_for_constructora
        create_demo_employees_for_constructora("Constructora Horizonte SpA")

    Args:
        company: Nombre de la Company en ERPNext.
        total_active: Número aproximado de empleados activos a crear (además de los 10 iniciales).
        total_left: Número de empleados con estado "Left" a crear.
        email_domain: Dominio para los correos corporativos (ej. horizonte.cl).
        seed: Semilla para tener datos reproducibles.
    """
    if seed is not None:
        random.seed(seed)
        fake.seed_instance(seed)

    if not frappe.db.exists("Company", company):
        frappe.throw(f"No existe la Company '{company}'")

    # cache de ruts ya existentes
    existing_ruts = set()
    try:
        existing = frappe.get_all("Employee", fields=["name", "rut"])
        for row in existing:
            if row.get("rut"):
                existing_ruts.add(row["rut"])
    except Exception:
        # si no existe campo rut, seguimos igual
        existing_ruts = set()

    # cache correos corporativos para evitar duplicados
    used_company_emails = set(
        row["company_email"]
        for row in frappe.get_all("Employee", fields=["company_email"])
        if row.get("company_email")
    )

    # employment types disponibles
    employment_types = {
        et["name"]
        for et in frappe.get_all("Employment Type", fields=["name"])
    }
    for et in EMPLOYMENT_TYPES_PRIORITY:
        if et not in employment_types:
            frappe.throw(f"Falta el Employment Type '{et}'. Créalo antes de ejecutar el script.")

    # Branch no tiene campo company en ERPNext. Tomamos todas.
    branches = [b["name"] for b in frappe.get_all("Branch", fields=["name"])]

    # Si no hay Branch creados, usamos None como valor por defecto.
    if not branches:
        branches = [None]
        created = []

    # -------------------------
    # 1) CEO, CFO y 8 obreros iniciales (2013-01-01)
    # -------------------------

    # CEO
    first_name = fake.first_name()
    last_name_1 = fake.last_name()
    last_name_2 = fake.last_name()
    last_name = f"{last_name_1} {last_name_2}"
    gender = generate_gender()
    birth_date = generate_birth_date()
    join_date = COMPANY_START_DATE
    rut = generate_rut(existing_ruts)

    dept_ceo = f"Gerencia{department_suffix}"
    print(dept_ceo)
    branch_ceo = branches[0]
    category_ceo = "admin"
    employment_type_ceo = "Contrato Indefinido"

    city, region = random_region_and_city()

    ceo = frappe.get_doc(
        {
            "doctype": "Employee",
            "company": company,
            "first_name": first_name,
            "last_name": last_name,
            "employee_name": f"{first_name} {last_name}",
            "gender": gender,
            "status": "Active",
            "date_of_birth": birth_date,
            "date_of_joining": join_date,
            "department": dept_ceo,
            "designation": "Director Ejecutivo (CEO)",
            "branch": branch_ceo,
            "employment_type": employment_type_ceo,
            "marital_status": random.choice(MARITAL_STATUSES),
            "blood_group": random.choice(BLOOD_GROUPS),
            "cell_number": generate_mobile(),
            "rut": rut,
        }
    )

    # emails CEO
    company_email = generate_company_email(first_name, last_name, email_domain, used_company_emails)
    personal_email = generate_personal_email(first_name, last_name)
    ceo.company_email = company_email
    ceo.personal_email = personal_email
    ceo.prefered_contact_email = "Company Email"
    ceo.prefered_email = company_email

    # emergencia
    ceo.emergency_contact = fake.name()
    ceo.emergency_phone_number = generate_mobile()
    ceo.emergency_contact_relation = random.choice(["Cónyuge", "Hermano", "Padre", "Madre"])

    # educación y experiencia
    add_education_rows(ceo, category_ceo, birth_date, join_date)
    add_external_experience_rows(ceo, join_date, category_ceo)

    # address
    create_address_for_employee(ceo, city, region)

    ceo.ctc = generate_ctc(category_ceo, ceo.designation)

    ceo.insert(ignore_permissions=True)
    created.append(ceo.name)

    # CFO con historia interna
    first_name = fake.first_name()
    last_name_1 = fake.last_name()
    last_name_2 = fake.last_name()
    last_name = f"{last_name_1} {last_name_2}"
    gender = generate_gender()
    birth_date = generate_birth_date()
    join_date = COMPANY_START_DATE  # mismo inicio que CEO
    rut = generate_rut(existing_ruts)

    dept_cfo = f"Gerencia{department_suffix}"
    branch_cfo = branches[0]
    category_cfo = "admin"
    employment_type_cfo = "Contrato Indefinido"

    city, region = random_region_and_city()

    cfo = frappe.get_doc(
        {
            "doctype": "Employee",
            "company": company,
            "first_name": first_name,
            "last_name": last_name,
            "employee_name": f"{first_name} {last_name}",
            "gender": gender,
            "status": "Active",
            "date_of_birth": birth_date,
            "date_of_joining": join_date,
            "department": dept_cfo,
            "designation": "Director Financiero (CFO)",
            "branch": branch_cfo,
            "employment_type": employment_type_cfo,
            "marital_status": random.choice(MARITAL_STATUSES),
            "blood_group": random.choice(BLOOD_GROUPS),
            "cell_number": generate_mobile(),
            "rut": rut,
        }
    )

    company_email = generate_company_email(first_name, last_name, email_domain, used_company_emails)
    personal_email = generate_personal_email(first_name, last_name)
    cfo.company_email = company_email
    cfo.personal_email = personal_email
    cfo.prefered_contact_email = "Company Email"
    cfo.prefered_email = company_email

    cfo.emergency_contact = fake.name()
    cfo.emergency_phone_number = generate_mobile()
    cfo.emergency_contact_relation = random.choice(["Cónyuge", "Hermano", "Padre", "Madre"])

    add_education_rows(cfo, category_cfo, birth_date, join_date)
    add_external_experience_rows(cfo, join_date, category_cfo)
    add_internal_history_for_cfo(cfo, join_date, department_suffix)

    create_address_for_employee(cfo, city, region)
    cfo.ctc = generate_ctc(category_cfo, cfo.designation)

    cfo.insert(ignore_permissions=True)
    created.append(cfo.name)

    # 8 obreros iniciales
    for _ in range(8):
        first_name = fake.first_name()
        last_name_1 = fake.last_name()
        last_name_2 = fake.last_name()
        last_name = f"{last_name_1} {last_name_2}"
        gender = generate_gender()
        birth_date = generate_birth_date()
        join_date = COMPANY_START_DATE
        rut = generate_rut(existing_ruts)

        dept = "Obras"
        designation = random.choice([
            "Albañil",
            "Maestro Primera",
            "Maestro Segunda",
            "Ayudante",
            "Carpintero",
            "Enfierrador",
        ])
        category = "obra"
        employment_type = "Contrato a Plazo Fijo"

        city, region = random_region_and_city()

        emp = frappe.get_doc(
            {
                "doctype": "Employee",
                "company": company,
                "first_name": first_name,
                "last_name": last_name,
                "employee_name": f"{first_name} {last_name}",
                "gender": gender,
                "status": "Active",
                "date_of_birth": birth_date,
                "date_of_joining": join_date,
                "department": dept,
                "designation": designation,
                "branch": random.choice(branches),
                "employment_type": employment_type,
                "marital_status": random.choice(MARITAL_STATUSES),
                "blood_group": random.choice(BLOOD_GROUPS),
                "cell_number": generate_mobile(),
                "salary_currency": "CLP",
                "salary_mode": "Bank",
                "rut": rut,
            }
        )

        personal_email = generate_personal_email(first_name, last_name)
        emp.personal_email = personal_email
        emp.prefered_contact_email = "Personal Email"
        emp.prefered_email = personal_email

        emp.emergency_contact = fake.name()
        emp.emergency_phone_number = generate_mobile()
        emp.emergency_contact_relation = random.choice(["Cónyuge", "Hermano", "Padre", "Madre"])

        add_education_rows(emp, category, birth_date, join_date)
        add_external_experience_rows(emp, join_date, category)
        create_address_for_employee(emp, city, region)
        emp.ctc = generate_ctc(category, emp.designation)

        emp.insert(ignore_permissions=True)
        created.append(emp.name)

    # -------------------------
    # 2) Resto de empleados ACTIVOS
    # -------------------------
    remaining_active = max(total_active - 10, 0)

    # distribución de antigüedad
    num_gt7 = int(remaining_active * 0.30)
    num_3to7 = int(remaining_active * 0.30)
    num_lt3 = remaining_active - num_gt7 - num_3to7

    tenure_groups = ["gt7"] * num_gt7 + ["3to7"] * num_3to7 + ["lt3"] * num_lt3
    random.shuffle(tenure_groups)

    for group in tenure_groups:
        first_name = fake.first_name()
        last_name_1 = fake.last_name()
        last_name_2 = fake.last_name()
        last_name = f"{last_name_1} {last_name_2}"
        gender = generate_gender()
        birth_date = generate_birth_date()

        join_date = generate_join_date_group(birth_date, group)
        rut = generate_rut(existing_ruts)

        dept, designation = pick_department_and_designation()
        # No permitir más de 1 gerente por departamento
        if "Gerente" in designation:
            if GERENTES_POR_DEPARTAMENTO.get(dept, False):
                # reasignar una designación NO gerente
                no_manager_designations = [d for d in ALL_DESIGNATIONS if "Gerente" not in d]
                designation = random.choice(no_manager_designations)
            else:
                GERENTES_POR_DEPARTAMENTO[dept] = True
        
        dept = f"{dept}{department_suffix}"
        category = classify_employee(dept, designation)
        employment_type = choose_employment_type(category)

        branch = random.choice(branches)
        city, region = random_region_and_city()

        emp = frappe.get_doc(
            {
                "doctype": "Employee",
                "company": company,
                "first_name": first_name,
                "last_name": last_name,
                "employee_name": f"{first_name} {last_name}",
                "gender": gender,
                "status": "Active",
                "date_of_birth": birth_date,
                "date_of_joining": join_date,
                "department": dept,
                "designation": designation,
                "branch": branch,
                "employment_type": employment_type,
                "marital_status": random.choice(MARITAL_STATUSES),
                "blood_group": random.choice(BLOOD_GROUPS),
                "cell_number": generate_mobile(),
                "salary_currency": "CLP",
                "salary_mode": "Bank",
                "rut": rut,
            }
        )

        # emails
        is_admin_like = (category == "admin") or designation in {
            "Administrador de Obra",
            "Residente de Obra",
            "Jefe de Obra",
            "Profesional de Oficina Técnica",
            "Control de Documentos",
            "Dibujante Técnico",
            "Topógrafo",
        }

        personal_email = generate_personal_email(first_name, last_name)
        if is_admin_like:
            company_email = generate_company_email(first_name, last_name, email_domain, used_company_emails)
            emp.company_email = company_email
            emp.personal_email = personal_email
            emp.prefered_contact_email = "Company Email"
            emp.prefered_email = company_email
        else:
            emp.personal_email = personal_email
            emp.prefered_contact_email = "Personal Email"
            emp.prefered_email = personal_email

        # emergencia
        emp.emergency_contact = fake.name()
        emp.emergency_phone_number = generate_mobile()
        emp.emergency_contact_relation = random.choice(["Cónyuge", "Hermano", "Padre", "Madre"])

        # educación y experiencia
        add_education_rows(emp, category, birth_date, join_date)
        add_external_experience_rows(emp, join_date, category)

        # address
        create_address_for_employee(emp, city, region)
        emp.ctc = generate_ctc(category, emp.designation)

        emp.insert(ignore_permissions=True)
        created.append(emp.name)

    # -------------------------
    # 3) Empleados que han dejado la empresa
    # -------------------------

    for _ in range(total_left):
        first_name = fake.first_name()
        last_name_1 = fake.last_name()
        last_name_2 = fake.last_name()
        last_name = f"{last_name_1} {last_name_2}"
        gender = generate_gender()
        birth_date = generate_birth_date()

        # para que tenga sentido, forzamos antigüedad >1 año
        join_group = random.choice(["gt7", "3to7", "lt3"])
        join_date = generate_join_date_group(birth_date, join_group)
        rut = generate_rut(existing_ruts)

        dept, designation = pick_department_and_designation()
        # No permitir más de 1 gerente por departamento
        if "Gerente" in designation:
            if GERENTES_POR_DEPARTAMENTO.get(dept, False):
                # reasignar una designación NO gerente
                no_manager_designations = [d for d in ALL_DESIGNATIONS if "Gerente" not in d]
                designation = random.choice(no_manager_designations)
            else:
                GERENTES_POR_DEPARTAMENTO[dept] = True
        
        dept = f"{dept}{department_suffix}"
        category = classify_employee(dept, designation)
        employment_type = choose_employment_type(category)

        branch = random.choice(branches)
        city, region = random_region_and_city()

        emp = frappe.get_doc(
            {
                "doctype": "Employee",
                "company": company,
                "first_name": first_name,
                "last_name": last_name,
                "employee_name": f"{first_name} {last_name}",
                "gender": gender,
                "status": "Active",  # lo cambiamos luego a Left
                "date_of_birth": birth_date,
                "date_of_joining": join_date,
                "department": dept,
                "designation": designation,
                "branch": branch,
                "employment_type": employment_type,
                "marital_status": random.choice(MARITAL_STATUSES),
                "blood_group": random.choice(BLOOD_GROUPS),
                "cell_number": generate_mobile(),
                "salary_currency": "CLP",
                "salary_mode": "Bank",
                "rut": rut,
            }
        )

        is_admin_like = (category == "admin") or designation in {
            "Administrador de Obra",
            "Residente de Obra",
            "Jefe de Obra",
            "Profesional de Oficina Técnica",
            "Control de Documentos",
            "Dibujante Técnico",
            "Topógrafo",
        }

        personal_email = generate_personal_email(first_name, last_name)
        if is_admin_like:
            company_email = generate_company_email(first_name, last_name, email_domain, used_company_emails)
            emp.company_email = company_email
            emp.personal_email = personal_email
            emp.prefered_contact_email = "Company Email"
            emp.prefered_email = company_email
        else:
            emp.personal_email = personal_email
            emp.prefered_contact_email = "Personal Email"
            emp.prefered_email = personal_email

        emp.emergency_contact = fake.name()
        emp.emergency_phone_number = generate_mobile()
        emp.emergency_contact_relation = random.choice(["Cónyuge", "Hermano", "Padre", "Madre"])

        add_education_rows(emp, category, birth_date, join_date)
        add_external_experience_rows(emp, join_date, category)
        create_address_for_employee(emp, city, region)
        emp.ctc = generate_ctc(category, emp.designation)

        # marcar salida
        set_exit_fields(emp, join_date)

        emp.insert(ignore_permissions=True)
        created.append(emp.name)

    frappe.db.commit()
    print(f"✅ Empleados demo creados: {len(created)} registros.")
    return created
