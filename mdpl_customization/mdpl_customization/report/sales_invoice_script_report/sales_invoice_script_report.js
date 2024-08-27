frappe.query_reports["sales invoice script report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.now_date(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.now_date(),
            "reqd": 1
        },
        {   
            "fieldname": "itm_group",
            "label": "Item Group",
            "fieldtype": "MultiSelectList",
            "options": "Item Group",
            "get_data": function(txt) {
                return frappe.db.get_link_options("Item Group", txt);
            }
        },
        
        {
            "fieldname": "customer",
            "label": "Customer",
            "fieldtype": "MultiSelectList",
            "options": "Customer",
            "get_data": function(txt) {
                return frappe.db.get_link_options("Customer", txt);
            }
        },
         {
    "fieldname": "parent_item_group",
    "label": "Parent Item Group",
    "fieldtype": "MultiSelectList",
    "options": "Item Group",
    "get_data": function(txt) {
        return frappe.db.get_list('Item Group', {
            fields: ["name"],
            filters: {
                is_group: 1
            }
        }).then(data => {
            return data.map(d => ({ value: d.name, label: d.name }));
        });
    }
}


    ]
};

