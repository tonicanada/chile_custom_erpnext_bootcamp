frappe.query_reports["Net Profit Timeline por Cost Center"] = {
    "filters": [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1,
            // Hoy menos 24 meses
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -24)
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1,
            // Fecha actual
            default: frappe.datetime.get_today()
        }
    ]
};
