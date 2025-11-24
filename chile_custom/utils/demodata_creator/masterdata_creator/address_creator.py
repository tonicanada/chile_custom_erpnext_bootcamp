import frappe
import random
from faker import Faker

# Importa las regiones desde tu app chile_custom
from chile_custom.constants.regiones import regiones as REGIONES_CHILE

fake = Faker("es_CL")


def _get_random_region():
    """
    Devuelve una tupla (region, numero_region, comuna) tomada aleatoriamente
    desde la lista oficial de regiones de Chile.
    """
    reg = random.choice(REGIONES_CHILE)
    return reg["region"], reg["numero"], random.choice(reg["comunas"])


def crear_direcciones_entidad_chile(entidad: str):
    """
    Crea direcciones demo para Supplier o Customer en ERPNext.

    Parámetros
    ----------
    entidad : str
        Debe ser exactamente uno de los siguientes valores:
        - "supplier"
        - "customer"

        En minúsculas. Si se pasa otro valor, la función lanza un error.

    Descripción
    -----------
    Esta función genera entre 1 y 3 direcciones para cada Supplier o Customer
    del sistema. Garantiza que cada entidad tenga al menos una dirección de tipo
    "Billing". Si solo se genera una dirección, será obligatoriamente Billing.

    Para cada dirección se genera:
        - Dirección (calle + número)
        - Región y comuna válidas según REGIONES_CHILE
        - Teléfono de Chile utilizando Faker
        - Pincode
        - Tipo de dirección: Billing / Shipping / Personal

    Las direcciones quedan vinculadas correctamente a Supplier o Customer
    mediante la tabla hija Address Link.

    Ejemplos de uso
    ---------------
    >>> crear_direcciones_entidad_chile("supplier")
    >>> crear_direcciones_entidad_chile("customer")
    """

    # ======== Validación del argumento ========
    if entidad not in ["supplier", "customer"]:
        frappe.throw("El argumento debe ser 'supplier' o 'customer' (en minúsculas).")

    # Determinar campos dependiendo de la entidad
    doctype = "Supplier" if entidad == "supplier" else "Customer"
    nombre_campo = "supplier_name" if entidad == "supplier" else "customer_name"

    registros = frappe.get_all(doctype, fields=["name", nombre_campo])

    if not registros:
        frappe.msgprint(f"No hay registros en {doctype}.")
        return

    total = 0

    for reg in registros:

        # Cantidad de direcciones a crear
        cantidad = random.choice([1, 1, 2, 3])

        # Lista final de tipos para garantizar al menos una Billing
        if cantidad == 1:
            tipos = ["Billing"]
        else:
            tipos = ["Billing"] + random.choices(
                ["Shipping", "Personal"],
                k=cantidad - 1
            )
            random.shuffle(tipos)

        # Crear cada dirección
        for address_type in tipos:

            region, region_numero, comuna = _get_random_region()

            calle = fake.street_name()
            numero = fake.building_number()
            pincode = fake.postcode()
            telefono = fake.phone_number()

            address = frappe.get_doc({
                "doctype": "Address",
                "address_title": reg[nombre_campo],
                "address_type": address_type,
                "address_line1": f"{calle} {numero}",
                "city": comuna,
                "state": region,
                "country": "Chile",
                "pincode": pincode,
                "phone": telefono,

                # Campos personalizados de Chile
                "comuna": comuna,
                "region": region,
                "region_numero": region_numero,

                # Enlace a entidad
                "links": [{
                    "link_doctype": doctype,
                    "link_name": reg.name
                }]
            })

            address.insert(ignore_permissions=True)
            total += 1

    frappe.msgprint(f"Direcciones creadas para {doctype}: {total}")
