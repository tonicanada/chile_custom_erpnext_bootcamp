import frappe

def create_locations_from_projects():
    """
    Crea una Location por cada Project activo,
    sin parent_location (campo vacío),
    vinculando el proyecto en el Custom Field 'linked_project'.
    """

    CUSTOM_FIELD = "linked_project"  # Nombre del campo custom

    # Obtener proyectos activos (todos menos Cancelled)
    proyectos = frappe.get_all(
        "Project",
        filters={"status": ["!=", "Cancelled"]},
        fields=["name", "project_name"]
    )

    if not proyectos:
        return "⚠️ No hay proyectos activos."

    creadas = []
    existentes = []

    for proj in proyectos:
        project_id = proj["name"]

        # Verificar si YA existe una Location vinculada al proyecto
        existing_loc = frappe.get_all(
            "Location",
            filters={CUSTOM_FIELD: project_id},
            pluck="name"
        )
        if existing_loc:
            existentes.append(existing_loc[0])
            continue

        # Crear nueva Location SIN parent_location
        nueva = frappe.get_doc({
            "doctype": "Location",
            "location_name": proj["project_name"],
            "parent_location": "",   # 🔥 Esto asegura nivel raíz
            "is_group": 0,
            CUSTOM_FIELD: project_id
        })

        nueva.insert(ignore_permissions=True)
        creadas.append(nueva.name)

    frappe.db.commit()

    return {
        "creadas": creadas,
        "existentes": existentes,
        "summary": f"Locations creadas: {len(creadas)}, ya existentes: {len(existentes)}"
    }
