// Copyright (c) 2023, vansh and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Payment Entry Report"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd":1,
            "default":frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd":1,
            "default": frappe.datetime.get_today(),
        }
        // {
        //     "fieldname":"status",
        //     "label":"Status",
        //     "fieldtype":"Link",
        //     "options":"Workflow State"
        // }
	]
};
