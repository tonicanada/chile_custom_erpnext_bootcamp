from frappe.custom.doctype.custom_field.custom_field import create_custom_field
import frappe

def create_campos_comprobante_tributario():
    """
    Crea en Expense Claim Detail:
    - tipo_comprobante_tributario (Select)
    - numero_documento (Int)
    - proveedor (Link a Supplier)
    """

    # ----------------------------
    # 1) Campo tipo_comprobante_tributario
    # ----------------------------
    options = [
        "Factura",
        "Factura Exenta",
        "Boleta",
        "Boleta Exenta",
        "Nota de Crédito",
        "Nota de Débito",
        "Vale",
        "Recibo",
        "Voucher Tarjeta",
        "Comprobante Transferencia",
        "Extraviado",
    ]

    field_tipo = {
        "fieldname": "tipo_comprobante_tributario",
        "label": "Tipo de Comprobante Tributario",
        "fieldtype": "Select",
        "options": "\n".join(options),
        "insert_after": "expense_type",
        "allow_on_submit": 1,
    }

    if not frappe.db.exists("Custom Field",
            {"dt": "Expense Claim Detail", "fieldname": "tipo_comprobante_tributario"}):
        create_custom_field("Expense Claim Detail", field_tipo)
        print("✅ Creado: tipo_comprobante_tributario")
    else:
        print("ℹ️ Ya existe: tipo_comprobante_tributario")

    # ----------------------------
    # 2) Campo numero_documento (Int)
    # ----------------------------
    field_numero = {
        "fieldname": "numero_documento",
        "label": "Número de Documento",
        "fieldtype": "Int",
        "insert_after": "tipo_comprobante_tributario",
        "allow_on_submit": 1,
        "description": "Número del documento tributario asociado",
    }

    if not frappe.db.exists("Custom Field",
            {"dt": "Expense Claim Detail", "fieldname": "numero_documento"}):
        create_custom_field("Expense Claim Detail", field_numero)
        print("✅ Creado: numero_documento")
    else:
        print("ℹ️ Ya existe: numero_documento")

    # ----------------------------
    # 3) Campo proveedor (Link a Supplier)
    # ----------------------------
    field_proveedor = {
        "fieldname": "proveedor",
        "label": "Proveedor",
        "fieldtype": "Link",
        "options": "Supplier",
        "insert_after": "numero_documento",
        "allow_on_submit": 1,
        "description": "Proveedor asociado al gasto",
    }

    if not frappe.db.exists("Custom Field",
            {"dt": "Expense Claim Detail", "fieldname": "proveedor"}):
        create_custom_field("Expense Claim Detail", field_proveedor)
        print("✅ Creado: proveedor")
    else:
        print("ℹ️ Ya existe: proveedor")


# Para ejecutarlo desde bench:
# bench --site site1.bootcamp execute chile_custom.scripts.expense_claim_fields.create_campos_comprobante_tributario
