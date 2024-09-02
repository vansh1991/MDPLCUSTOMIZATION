import frappe

def execute(filters=None):
    filters = filters or {}

    # Ensure both dates are selected
    if not filters.get('from_date') or not filters.get('to_date'):
        frappe.msgprint("Please select both From Date and To Date.")
        return [], []

    # Define all static item groups
    all_item_groups = [
        'Airpod 2', 'Airpod 3', 'Airpod Pro', 'Airpod Pro2',
        '11', '12', '13', '14', '14 Plus', '14 Pro', '14 Pro Max',
        '15', '15 Plus', '15 Pro', '15 Pro Max', 'iPad Air 6th gen',
        'iPad Pro 5th gen', 'Ipad 9th gen', 'iPad 10th gen',
        'Ipad Air 5th gen', 'Ipad pro 4th gen', 'iPad Pro 3rd Gen', '(Accessories)',
        'Watch SE 2', 'Watch 8', 'WATCH Ultra', 'Watch 9', 'WATCH Ultra 2',
        'Mac Air M2', 'Mac Air M3'
    ]

    # Initialize selected_item_groups
    selected_item_groups = []

    # Apply parent_item_group logic first
    if filters.get('parent_item_group'):
        if 'Macbook' in filters['parent_item_group']:
            selected_item_groups += ['Mac Air M2', 'Mac Air M3']
        if 'AirPods' in filters['parent_item_group']:
            selected_item_groups += ['Airpod 2', 'Airpod 3', 'Airpod Pro', 'Airpod Pro2']
        if 'iPhone' in filters['parent_item_group']:
            selected_item_groups += ['11', '12', '13', '14', '14 Plus', '14 Pro', '14 Pro Max', '15', '15 Plus', '15 Pro', '15 Pro Max']
        if 'iPad' in filters['parent_item_group']:
            selected_item_groups += ['iPad Air 6th gen', 'iPad Pro 5th gen', 'Ipad 9th gen', 'iPad 10th gen', 'Ipad Air 5th gen', 'Ipad pro 4th gen', 'iPad Pro 3rd Gen']
        if 'Accessories' in filters['parent_item_group']:
            selected_item_groups += ['(Accessories)']
        if 'Apple Watch' in filters['parent_item_group']:
            selected_item_groups += ['Watch SE 2', 'Watch 8', 'WATCH Ultra', 'Watch 9', 'WATCH Ultra 2']
        
    # If itm_group is selected, prioritize itm_group over parent_item_group
    if filters.get('itm_group'):
        selected_item_groups = filters['itm_group']

    # If no filters are applied, show all item groups
    if not selected_item_groups:
        selected_item_groups = all_item_groups

    # Create column definitions, starting with the customer column
    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 150}
    ]

    # Sanitize dynamic column names (replace spaces with underscores)
    sanitized_groups = [group.replace(' ', '_').lower() for group in selected_item_groups]

    # Create the dynamic SELECT clause based on selected item groups
    group_select_clause = ", ".join(
        f"SUM(CASE WHEN ig.item_group_name = '{group}' THEN si_item.qty ELSE 0 END) AS `{sanitized_group}`"
        for group, sanitized_group in zip(selected_item_groups, sanitized_groups)
    )

    # Construct the base query with filters
    where_clause = (
        "si.docstatus = 1 "
        "AND si.is_return = 0 "
        "AND si.posting_date BETWEEN %s AND %s"
    )

    # Add itm_group filter
    if filters.get('itm_group'):
        group_placeholders = ', '.join(['%s'] * len(filters['itm_group']))
        where_clause += f" AND ig.item_group_name IN ({group_placeholders})"

    # Add parent_item_group filter (only if itm_group is not used)
    if filters.get('parent_item_group') and not filters.get('itm_group'):
        parent_group_placeholders = ', '.join(['%s'] * len(filters['parent_item_group']))
        where_clause += f" AND ig.parent_item_group IN ({parent_group_placeholders})"

    # Add customer filter
    if filters.get('customer'):
        customer_placeholders = ', '.join(['%s'] * len(filters['customer']))
        where_clause += f" AND si.customer IN ({customer_placeholders})"

    # Add apple_id filter, ensuring it is not empty if the filter is checked
    if filters.get('apple_id'):
        where_clause += " AND c.apple_id IS NOT NULL AND c.apple_id != ''"

    # Construct the final query
    query = f"""
    SELECT 
        si.customer AS customer,
        {group_select_clause}
    FROM 
        `tabSales Invoice` si
    INNER JOIN `tabSales Invoice Item` si_item ON si.name = si_item.parent
    INNER JOIN `tabItem` item ON si_item.item_code = item.name
    INNER JOIN `tabItem Group` ig ON item.item_group = ig.name
    INNER JOIN `tabCustomer` c ON si.customer = c.name
    WHERE  
        {where_clause}
    GROUP BY 
        si.customer
    ORDER BY 
        si.customer;
    """
    # query = f"""
    # SELECT 
    #     c.name AS customer,
    #     {group_select_clause}
    # FROM 
    #     `tabCustomer` c
    # LEFT JOIN `tabSales Invoice` si ON c.name = si.customer
    # LEFT JOIN `tabSales Invoice Item` si_item ON si.name = si_item.parent
    # LEFT JOIN `tabItem` item ON si_item.item_code = item.name
    # LEFT JOIN `tabItem Group` ig ON item.item_group = ig.name
    # WHERE  
    #     {where_clause}  -- Adjust this clause to handle cases where si is NULL, if necessary
    # GROUP BY 
    #     c.name
    # ORDER BY 
    #     c.name;
    # """

    
    # Add filter parameters for the query
    params = [filters.get('from_date'), filters.get('to_date')]

    # Extend parameters with itm_group, parent_item_group, and customer filters
    if filters.get('itm_group'):
        params.extend(filters['itm_group'])
    if filters.get('parent_item_group') and not filters.get('itm_group'):
        params.extend(filters['parent_item_group'])
    if filters.get('customer'):
        params.extend(filters['customer'])
    # if filters.get('apple_id') is not None:
    #     params.append(filters['apple_id'])
        

    # Log query and parameters for debugging
    frappe.logger().info(f"Executing query: {query}")
    frappe.logger().info(f"With params: {params}")

    
    try:
        data = frappe.db.sql(query, params, as_dict=True)
        
    except Exception as e:
        frappe.logger().error(f"Error executing query: {e}")
        raise
    

    if filters.get("itm_group") and filters.get("apple_id") is None and len(filters.get('customer')) == 0 :
        all_customer = frappe.db.sql("""SELECT name AS customer FROM `tabCustomer`""", as_dict=True)
        
        for customer_row in all_customer:
            if customer_row.get("customer") not in [customer.get("customer") for customer in data]:
                data.append(customer_row)

    if filters.get("itm_group") and filters.get("apple_id") is not None and len(filters.get('customer')) == 0:
        all_customer = frappe.db.sql("""SELECT name AS customer FROM `tabCustomer` WHERE apple_id > 1""", as_dict=True)
        
        for customer_row in all_customer:
            if customer_row.get("customer") not in [customer.get("customer") for customer in data]:
                data.append(customer_row)


    if len(filters.get("itm_group")) == 0 and filters.get("apple_id") is not None and len(filters.get('customer')) == 0 and len(filters.get('parent_item_group')) == 0:
        all_customer = frappe.db.sql("""SELECT name AS customer FROM `tabCustomer` WHERE apple_id > 1""", as_dict=True)
        
        for customer_row in all_customer:
            if customer_row.get("customer") not in [customer.get("customer") for customer in data]:
                data.append(customer_row)

    if len(filters.get("itm_group")) == 0 and filters.get("apple_id") is None and len(filters.get('customer')) == 0 and len(filters.get('parent_item_group')) == 0:
        all_customer = frappe.db.sql("""SELECT name AS customer FROM `tabCustomer`""", as_dict=True)
        
        for customer_row in all_customer:
            if customer_row.get("customer") not in [customer.get("customer") for customer in data]:
                data.append(customer_row)

    if len(filters.get("itm_group")) == 0 and filters.get("apple_id") is None and len(filters.get('customer')) == 0 and len(filters.get('parent_item_group')) > 0:
        all_customer = frappe.db.sql("""SELECT name AS customer FROM `tabCustomer`""", as_dict=True)
        
        for customer_row in all_customer:
            if customer_row.get("customer") not in [customer.get("customer") for customer in data]:
                data.append(customer_row)

    if len(filters.get("itm_group")) == 0 and filters.get("apple_id") is not None and len(filters.get('customer')) == 0 and len(filters.get('parent_item_group')) > 0:
        all_customer = frappe.db.sql("""SELECT name AS customer FROM `tabCustomer` WHERE apple_id > 1""", as_dict=True)
        
        for customer_row in all_customer:
            if customer_row.get("customer") not in [customer.get("customer") for customer in data]:
                data.append(customer_row)

    # If no data is returned, return a single row with 0 values
    if not data:
        customer_query = "SELECT name AS customer FROM `tabCustomer` WHERE disabled = 0"
        
        # Apply customer filter
        if filters.get('customer'):
            customer_query += f" AND name IN ({customer_placeholders})"
            params = filters['customer']
        else:
            params = []

        # Fetch all customers
        all_customers = frappe.db.sql(customer_query, params, as_dict=True)
      
        # Prepare data with zero values
        data = [{
            "customer": customer.get('customer'),
            **{sanitized_group: 0 for sanitized_group in sanitized_groups},
        } for customer in all_customers]

    # Dynamically add columns for each selected item group
    columns.extend({
        "label": group,
        "fieldname": sanitized_group,
        "fieldtype": "Float",
        "width": 120
    } for group, sanitized_group in zip(selected_item_groups, sanitized_groups))

    # Add total column for sum of all item groups
    columns.append({
        "label": "Total",
        "fieldname": "total",
        "fieldtype": "Float",
        "width": 150
    })

    # Calculate the total column for each row
    for row in data:
        row['total'] = sum(row.get(sanitized_group, 0) for sanitized_group in sanitized_groups)
    
    return columns, data

