import frappe
import random
from faker import Faker
import unicodedata
import re

fake = Faker("es_CL")

ROLES_POSIBLES = [
    "Contabilidad",
    "Compras",
    "Administración",
    "Operaciones",
    "Gerencia",
]

# ================================================================
# UTILIDADES
# ================================================================

def telefono_chileno():
    """Genera un número móvil chileno válido: +569XXXXXXXX"""
    return f"+569{random.randint(10000000, 99999999)}"


def limpiar(texto):
    """Normaliza texto: sin acentos, sin caracteres especiales, minúsculas."""
    if not texto:
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode(
        'ascii', 'ignore'
    ).decode('ascii')
    texto = re.sub(r'[^a-zA-Z0-9 ]', '', texto)
    return texto.lower().strip()


def dominio_desde_nombre(nombre_entidad):
    """Genera un dominio plausible a partir del Supplier/Customer."""
    base = limpiar(nombre_entidad)
    partes = base.split()

    if len(partes) == 1:
        raiz = partes[0]
    elif len(partes) == 2:
        raiz = partes[1]
    else:
        comunes = {"spa", "ltda", "sa", "eirl", "limitada", "constructora", "empresa", "servicios"}
        filtrado = [p for p in partes if p not in comunes]
        if len(filtrado) == 0:
            raiz = partes[-1]
        elif len(filtrado) == 1:
            raiz = filtrado[0]
        else:
            raiz = filtrado[-2] + filtrado[-1]

    return raiz + random.choice([".cl", ".com"])


# ================================================================
# FUNCIÓN PRINCIPAL — CREA CONTACTOS PARA SUPPLIER O CUSTOMER
# ================================================================
"""
crear_contactos_entidad(tipo)

Crea contactos para:
    - Proveedores  (tipo="supplier")
    - Clientes     (tipo="customer")

Características:
- Genera entre 1 y 3 contactos por entidad
- Asegura al menos 1 Billing Contact
- Teléfonos chilenos correctos: +569XXXXXXXX
- Emails coherentes formados por:
      nombre.apellido@dominio_generado.cl
- Rol aleatorio del listado ROLES_POSIBLES
- Evita consultas a Gravatar
- Inserta contactos con ignore_permissions=True
"""

def crear_contactos_entidad(tipo="supplier"):
    tipo = tipo.lower()

    if tipo not in ["supplier", "customer"]:
        frappe.throw("Tipo debe ser 'supplier' o 'customer'.")

    doctype = "Supplier" if tipo == "supplier" else "Customer"
    fieldname = "supplier_name" if tipo == "supplier" else "customer_name"

    entidades = frappe.get_all(doctype, fields=["name", fieldname])

    if not entidades:
        frappe.msgprint(f"No hay registros en {doctype}.")
        return

    total_contactos = 0
    total_entidades = len(entidades)

    print(f"Creando contactos para {total_entidades} {tipo}s...")

    for idx, entidad in enumerate(entidades, start=1):

        print(f"\rEntidad {idx}/{total_entidades} – Contactos creados: {total_contactos}", end="")

        cantidad = random.choice([1, 1, 2, 3])
        indice_billing = random.randint(0, cantidad - 1)

        nombre_entidad = entidad[fieldname]
        dominio = dominio_desde_nombre(nombre_entidad)

        for i in range(cantidad):

            first = fake.first_name()
            last = fake.last_name() + " " + fake.last_name()
            rol = random.choice(ROLES_POSIBLES)
            telefono = telefono_chileno()

            # Construcción del email
            local = f"{limpiar(first)}.{limpiar(last)}".replace(" ", "")
            if not local or local == ".":
                local = f"contacto{random.randint(1000,9999)}"

            email = f"{local}@{dominio}"

            # Evitar duplicados
            sec = 1
            while frappe.db.exists("Contact", {"email_id": email}):
                email = f"{local}{sec}@{dominio}"
                sec += 1

            billing = 1 if i == indice_billing else 0

            contacto = frappe.get_doc({
                "doctype": "Contact",
                "first_name": first,
                "last_name": last,
                "gender": random.choice(["Male", "Female"]),
                "status": "Passive",

                # Evita llamadas a Gravatar
                "image": None,

                "email_ids": [{"email_id": email, "is_primary": 1}],
                "phone_nos": [{"phone": telefono, "is_primary_phone": 1}],

                # User ID
                "user_id": email,

                "is_primary_contact": 0,
                "is_billing_contact": billing,

                "department": rol,

                "links": [{
                    "link_doctype": doctype,
                    "link_name": entidad.name
                }]
            })

            contacto.insert(ignore_permissions=True)
            total_contactos += 1

    print("")  # salto de línea
    frappe.msgprint(f"Contactos creados: {total_contactos}")


# ================================================================
# OPCIONAL: CORREGIR TELÉFONOS EXISTENTES
# ================================================================
def actualizar_telefonos_chilenos():
    contactos = frappe.get_all("Contact", fields=["name"])
    total = len(contactos)
    print(f"Corrigiendo teléfonos para {total} contactos...")

    for idx, c in enumerate(contactos, start=1):
        contact = frappe.get_doc("Contact", c.name)

        if not contact.phone_nos:
            contact.append("phone_nos", {
                "phone": telefono_chileno(),
                "is_primary_phone": 1
            })
        else:
            actualizado = False

            for phone in contact.phone_nos:
                if phone.is_primary_phone:
                    phone.phone = telefono_chileno()
                    actualizado = True
                    break

            if not actualizado:
                contact.phone_nos[0].phone = telefono_chileno()
                contact.phone_nos[0].is_primary_phone = 1

        contact.save(ignore_permissions=True)
        print(f"\rActualizados {idx}/{total}", end="")

    print("\n¡Listo!")


# ================================================================
# OPCIONAL: CORREGIR EMAILS EXISTENTES
# ================================================================
def actualizar_emails_contactos():
    contactos = frappe.get_all("Contact", fields=["name"])
    total = len(contactos)

    print(f"Corrigiendo emails para {total} contactos...")

    for idx, c in enumerate(contactos, start=1):
        contact = frappe.get_doc("Contact", c.name)

        # Obtener Supplier o Customer asociado
        enlaces = [l for l in contact.links if l.link_doctype in ("Supplier", "Customer")]
        if not enlaces:
            continue

        doctype = enlaces[0].link_doctype
        nombre = frappe.db.get_value(doctype, enlaces[0].link_name,
                                     "supplier_name" if doctype == "Supplier" else "customer_name")

        dominio = dominio_desde_nombre(nombre)

        first = limpiar(contact.first_name)
        last = limpiar(contact.last_name)
        local = f"{first}.{last}".replace(" ", "") or f"contacto{idx}"
        email = f"{local}@{dominio}"

        sec = 1
        while frappe.db.exists("Contact", {"email_id": email}):
            email = f"{local}{sec}@{dominio}"
            sec += 1

        if not contact.email_ids:
            contact.append("email_ids", {"email_id": email, "is_primary": 1})
        else:
            contact.email_ids[0].email_id = email
            contact.email_id = email

        contact.save(ignore_permissions=True)
        print(f"\rActualizados {idx}/{total}", end="")

    print("\n¡Listo! Emails corregidos.")
