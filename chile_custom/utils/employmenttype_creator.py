import frappe

def reset_employment_types_chile():
    """
    Elimina todos los Employment Type actuales y crea un set nuevo para una
    constructora chilena.

    Se adapta automáticamente al campo correcto usado en autoname, leyendo el
    meta del DocType Employment Type.
    """

    # 1) Employment Types que quieres para la constructora
    nuevos_tipos = [
        "Tiempo Completo",
        "Part-Time",
        "Jornada Excepcional",
        "Contrato a Plazo Fijo",
        "Contrato Indefinido",
        "Honorarios",
        "Práctica Profesional",
        "Aprendiz",
        "Trabajo por Faena",
        "Subcontrato",
    ]

    # 2) Averiguar cómo se llama el campo que usa autoname
    meta = frappe.get_meta("Employment Type")
    autoname = (meta.autoname or "").strip()

    fieldname_for_name = None

    # Caso típico: autoname = "field:employment_type" o similar
    if autoname.startswith("field:"):
        fieldname_for_name = autoname.split("field:", 1)[1].strip()

    # Si por alguna razón no hay autoname tipo field:, intentamos adivinar
    if not fieldname_for_name:
        # candidatos habituales
        candidates = ["employment_type", "employee_type", "employment_type_name"]
        for c in candidates:
            if meta.get_field(c):
                fieldname_for_name = c
                break

    # Si aún no lo tenemos, buscamos un campo obligatorio tipo Data con label relacionada
    if not fieldname_for_name:
        for df in meta.fields:
            if (
                df.reqd
                and df.fieldtype in ("Data", "Small Text")
                and df.label
                and "Employment" in df.label
            ):
                fieldname_for_name = df.fieldname
                break

    if not fieldname_for_name:
        # Si llegamos aquí es que el DocType está muy custom; mejor avisar.
        raise Exception(
            "No se pudo determinar el campo usado para autoname en 'Employment Type'. "
            "Revisa el DocType y ajusta el script."
        )

    print(f"🔍 Usando el campo '{fieldname_for_name}' para crear Employment Types.")

    # 3) Eliminar existentes
    print("🧹 Eliminando Employment Types existentes...")
    existentes = frappe.get_all("Employment Type", pluck="name")
    for et in existentes:
        frappe.delete_doc("Employment Type", et, force=1)
    frappe.db.commit()

    # 4) Crear nuevos usando el campo correcto
    print("🛠️ Creando nuevos Employment Types...")

    for tipo in nuevos_tipos:
        values = {
            "doctype": "Employment Type",
            fieldname_for_name: tipo,
        }

        doc = frappe.get_doc(values)
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
    print("✅ Employment Types creados correctamente para constructora chilena.")
