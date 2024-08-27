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
        'Ipad Air 5th gen', 'Ipad pro 4th gen', 'iPad Pro 3rd Gen'
    ]

    # Initialize selected_item_groups
    selected_item_groups = []

    # Apply parent_item_group logic first
    if filters.get('parent_item_group'):
        if 'AirPods' in filters['parent_item_group']:
            selected_item_groups += ['Airpod 2', 'Airpod 3', 'Airpod Pro', 'Airpod Pro2']
        if 'iPhone' in filters['parent_item_group']:
            selected_item_groups += ['11', '12', '13', '14', '14 Plus', '14 Pro', '14 Pro Max', '15', '15 Plus', '15 Pro', '15 Pro Max']
        if 'iPad' in filters['parent_item_group']:
            selected_item_groups += ['iPad Air 6th gen', 'iPad Pro 5th gen', 'Ipad 9th gen', 'iPad 10th gen', 'Ipad Air 5th gen', 'Ipad pro 4th gen', 'iPad Pro 3rd Gen']

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
    WHERE  
        {where_clause}
    GROUP BY 
        si.customer
    ORDER BY 
        si.customer;
    """

    # Add filter parameters for the query
    params = [filters.get('from_date'), filters.get('to_date')]

    # Extend parameters with itm_group, parent_item_group, and customer filters
    if filters.get('itm_group'):
        params.extend(filters['itm_group'])
    if filters.get('parent_item_group') and not filters.get('itm_group'):
        params.extend(filters['parent_item_group'])
    if filters.get('customer'):
        params.extend(filters['customer'])

    # Log query and parameters for debugging
    frappe.logger().info(f"Executing query: {query}")
    frappe.logger().info(f"With params: {params}")

    try:
        # Execute the SQL query
        data = frappe.db.sql(query, params, as_dict=True)
    except Exception as e:
        frappe.logger().error(f"Error executing query: {e}")
        raise

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

