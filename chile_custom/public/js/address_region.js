frappe.ui.form.on("Address", {
    comuna(frm) {
        if (!frm.doc.comuna) return;

        frappe.call({
            method: "chile_custom.api.get_region_from_comuna",
            args: { comuna: frm.doc.comuna },
            callback(r) {
                if (r.message) {
                    frm.set_value("region", r.message.region);
                    frm.set_value("region_numero", r.message.numero);
                }
            }
        });
    }
});
