frappe.ui.form.on('Project', {

    project_comuna(frm) {
        if (!frm.doc.project_comuna) return;

        frappe.call({
            method: "chile_custom.api.get_region_from_comuna",
            args: {
                comuna: frm.doc.project_comuna
            },
            callback(r) {
                if (r.message) {
                    frm.set_value("project_region", r.message.region);
                    // Si tienes este campo:
                    // frm.set_value("project_region_numero", r.message.numero);
                }
            }
        });
    }

});
