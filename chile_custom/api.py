import frappe
from chile_custom.constants.regiones import regiones

@frappe.whitelist()
def get_region_from_comuna(comuna):
    for r in regiones:
        if comuna in r["comunas"]:
            return {
                "region": r["region"],
                "numero": r["numero"]
            }
    return {}
