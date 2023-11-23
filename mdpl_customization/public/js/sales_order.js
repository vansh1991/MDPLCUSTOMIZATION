frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if(!frm.__islocal){
            
            if(frm.doc.docstatus == 0 && !frm.doc.credit_limit_approval){
                frm.add_custom_button(__('Send Approval Request'), function(){
                    frappe.call({
                        method: "mattermost_integration.doc_events.purchase_receipt.create_credit_limit",
                        args:{name:frm.doc.name}, //dotted path to server method
                        callback: function(r) {
                            // code snippet
                            console.log(r)
                        }
                    });
                }, __("Credit Limit"));
            }

        }
        
      
  }
});
