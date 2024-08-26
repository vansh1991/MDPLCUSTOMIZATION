// Copyright (c) 2023, vansh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Closing', {
	refresh: function (frm) {

		frm.add_custom_button(__("Sales Order"), function () {
			cur_frm.set_value("reference_document", "Sales Order")
			frappe.call({
				method: "mdpl_customization.mdpl_customization.doctype.bulk_closing.bulk_closing.get_record",
				args: {
					"doc": frm.doc.reference_document
				},
				async: true,
				callback: function (r) {

					if (r) {
						frm.doc.item = []
						$.each(r.message, function (i, d) {
							// console.log(d)
							var row = frappe.model.add_child(frm.doc, "Reference Doc Records", "item");
							row.reference_doctype = frm.doc.reference_document;
							row.reference_docname = d.name
							row.party = d.customer
							row.grand_total = d.grand_total
							row.status = d.status


						});
						frm.refresh_fields("item");
						frm.save();
					} else {
						frm.doc.item = []
						frappe.throw("No Record Found for Closing")
					}
				},
				always: function () {
					frappe.ui.form.is_saving = false;
				}
				
			})
		}, __("Get Records From"));
		frm.add_custom_button(__("Purchase Order"), function () {
			cur_frm.set_value("reference_document", "Purchase Order")
			frappe.call({
				method: "mdpl_customization.mdpl_customization.doctype.bulk_closing.bulk_closing.get_record",
				args: {
					"doc": frm.doc.reference_document
				},
				callback: function (r) {
					if (r) {
						frm.doc.item = []
						$.each(r.message, function (i, d) {
							// console.log(d)
							var row = frappe.model.add_child(frm.doc, "Reference Doc Records", "item");
							row.reference_doctype = frm.doc.reference_document;
							row.reference_docname = d.name
							row.party = d.supplier
							row.grand_total = d.grand_total
							row.status = d.status


						});
						frm.refresh_fields("item");
						frm.save();
					} else {
						frm.doc.item = []
						frappe.throw("No Record Found for Closing")
					}
				},
				always: function () {
					frappe.ui.form.is_saving = false;
				}
			})
		}, __("Get Records From"));
		frm.add_custom_button(__("Delivery Note"), function () {
			cur_frm.set_value("reference_document", "Delivery Note")
			frappe.call({
				method: "mdpl_customization.mdpl_customization.doctype.bulk_closing.bulk_closing.get_record",
				args: {
					"doc": frm.doc.reference_document
				},
				callback: function (r) {
					if (r) {
						frm.doc.item = []
						$.each(r.message, function (i, d) {
							// console.log(d)
							var row = frappe.model.add_child(frm.doc, "Reference Doc Records", "item");
							row.reference_doctype = frm.doc.reference_document;
							row.reference_docname = d.name
							row.party = d.customer
							row.grand_total = d.grand_total
							row.status = d.status


						});
						frm.refresh_fields("item");
						frm.save();
					} else {
						frm.doc.item = []
						frappe.throw("No Record Found for Closing")
					}
				},
				always: function () {
					frappe.ui.form.is_saving = false;
				}
			})
		}, __("Get Records From"));
		cur_frm.page.set_inner_btn_group_as_primary(__("Get Records From"));
		if (frm.doc.reference_document == "Delivery Note") {
			frm.add_custom_button(__("Close"), function () {
				if (frm.doc.reference_document == "Delivery Note") {
					var item_data = cur_frm.get_selected();
					if (item_data.item) {
						$.each(item_data.item, function (i, d) {
							var d_data = locals["Reference Doc Records"][d];
							console.log(d_data)
							var name_data = d_data.reference_docname
							close_delivery_note(name_data)
						});

					}
					else {
						frappe.throw("Please Select the item Row to Close or Hold the Record")
					}

				}
			}, __("Mark Status"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Mark Status"));

		} else if (frm.doc.reference_document == "Sales Order" || frm.doc.reference_document == "Purchase Order") {
			frm.add_custom_button(__("Hold"), function () {
				if (frm.doc.reference_document == "Sales Order") {
					hold_sales_order(frm.doc)

				}else if(frm.doc.reference_document == "Purchase Order"){
					hold_purchase_order(frm.doc)
				}

			}, __("Mark Status"));
			frm.add_custom_button(__("Close"), function () {

				if (frm.doc.reference_document == "Sales Order") {
					var item_data = cur_frm.get_selected();
					if (item_data.item) {
						$.each(item_data.item, function (i, d) {
							var d_data = locals["Reference Doc Records"][d];
							console.log(d_data)
							var name_data = d_data.reference_docname
							close_sales_order(name_data)
						});

					}
					else {
						frappe.throw("Please Select the item Row to Close or Hold the Record")
					}

				} else if (frm.doc.reference_document == "Purchase Order") {
					var item_data = cur_frm.get_selected();
					if (item_data.item) {
						$.each(item_data.item, function (i, d) {
							var d_data = locals["Reference Doc Records"][d];
							console.log(d_data)
							var name_data = d_data.reference_docname
							close_purchase_order(name_data)
						});

					}
					else {
						frappe.throw("Please Select the item Row to Close or Hold the Record")
					}

				}


			}, __("Mark Status"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Mark Status"));
		}

		// cur_frm.save()
	},
	validate: function (frm) {
		if (frm.doc.updated == 1) {
			get_record()
			cur_frm.set_value("updated", 0)
		}


	}

});

function hold_sales_order(doc) {
	var me = doc;
	var item_data = cur_frm.get_selected();
	if (item_data.item) {
		var d = new frappe.ui.Dialog({
			title: __('Reason for Hold'),
			fields: [
				{
					"fieldname": "reason_for_hold",
					"fieldtype": "Text",
					"reqd": 1,
				}
			],
			primary_action: function () {
				var data = d.get_values();
				var item_data = cur_frm.get_selected();
				$.each(item_data.item, function (i, d) {
					var d_data = locals["Reference Doc Records"][d];
					console.log(d_data)
					var name_data = d_data.reference_docname

					frappe.call({
						method: "frappe.desk.form.utils.add_comment",
						args: {
							reference_doctype: d_data.reference_doctype,
							reference_name: d_data.reference_docname,
							content: __('Reason for hold:') + ' ' + data.reason_for_hold,
							comment_email: frappe.session.user,
							comment_by: frappe.session.user_fullname
						},
						callback: function (r) {
							if (!r.exc) {
								update_status_sales_order('Hold', 'On Hold', name_data)

							}
						},
						always: function () {
							frappe.ui.form.is_saving = false;
						}
					});


				});
				d.hide();
			}
		});
		d.show();

	} else {
		frappe.throw("Please Select the item Row to Close or Hold the Record")
	}

}
function close_sales_order(name_data) {
	update_status_sales_order("Close", "Closed", name_data)
}
function update_status_sales_order(label, status, name_data) {
	frappe.ui.form.is_saving = true;
	frappe.call({
		method: "erpnext.selling.doctype.sales_order.sales_order.update_status",
		args: { status: status, name: name_data },
		callback: function (r) {
			cur_frm.set_value("updated_by", frappe.session.user)
			cur_frm.set_value("last_updated", frappe.datetime.now_datetime())
			frappe.show_alert({
				message: __(name_data + ' Successfully Closed'),
				indicator: 'green'
			}, 5);

			setTimeout(function () {
				cur_frm.doc.item = []
				cur_frm.save()
				cur_frm.set_value("updated", 1)

			}, 2000);

		},
		always: function () {
			frappe.ui.form.is_saving = false;
		}
	});
}

function close_delivery_note(name_data) {
	update_status_delivery_note("Closed",name_data)
}


function update_status_delivery_note(status,name_data) {
	frappe.ui.form.is_saving = true;
	frappe.call({
		method: "erpnext.stock.doctype.delivery_note.delivery_note.update_delivery_note_status",
		args: { docname: name_data, status: status },
		callback: function (r) {
			if (!r.exc)
				cur_frm.set_value("updated_by", frappe.session.user)
				cur_frm.set_value("last_updated", frappe.datetime.now_datetime())
				frappe.show_alert({
					message: __(name_data + ' Successfully Closed'),
					indicator: 'green'
				}, 5);

				setTimeout(function () {
					cur_frm.doc.item = []
					cur_frm.save()
					cur_frm.set_value("updated", 1)

				}, 2000);
		},
		always: function () {
			frappe.ui.form.is_saving = false;
		}
	})
}



function hold_purchase_order(doc) {
	var me = doc;
	var item_data = cur_frm.get_selected();
	if (item_data.item) {
		var d = new frappe.ui.Dialog({
			title: __('Reason for Hold'),
			fields: [
				{
					"fieldname": "reason_for_hold",
					"fieldtype": "Text",
					"reqd": 1,
				}
			],
			primary_action: function () {

				var data = d.get_values();
				var item_data = cur_frm.get_selected();
				$.each(item_data.item, function (i, d) {
					var d_data = locals["Reference Doc Records"][d];
					console.log(d_data)
					var name_data = d_data.reference_docname

					frappe.call({
						method: "frappe.desk.form.utils.add_comment",
						args: {
							reference_doctype: d_data.reference_doctype,
							reference_name: d_data.reference_docname,
							content: __('Reason for hold:') + ' ' + data.reason_for_hold,
							comment_email: frappe.session.user,
							comment_by: frappe.session.user_fullname
						},
						callback: function (r) {
							if (!r.exc) {
								console.log(r)
								update_status_po('Hold', 'On Hold',name_data)
							}
						},
						always: function () {
							frappe.ui.form.is_saving = false;
						}
					});
				});
				d.hide();
			}
		});
		d.show();
	} else {
		frappe.throw("Please Select the item Row to Close or Hold the Record")
	}
}


function close_purchase_order(name_data) {
	update_status_po('Close', 'Closed', name_data)
}


function update_status_po(label, status, name_data) {
	frappe.call({
		method: "erpnext.buying.doctype.purchase_order.purchase_order.update_status",
		args: { status: status, name: name_data },
		callback: function (r) {
			if (r){
				cur_frm.set_value("updated_by", frappe.session.user)
				cur_frm.set_value("last_updated", frappe.datetime.now_datetime())
				frappe.show_alert({
					message: __(name_data + ' Successfully Marked Status Hold'),
					indicator: 'green'
				}, 5);
				setTimeout(function () {
					cur_frm.doc.item = []
					cur_frm.save()
					cur_frm.set_value("updated", 1)
	
				}, 2000);

			}
			
		},
		always: function () {
			frappe.ui.form.is_saving = false;
		}
	})
}


function get_record() {
	frappe.call({
		method: "mdpl_customization.mdpl_customization.doctype.bulk_closing.bulk_closing.get_record",
		args: {
			"doc": cur_frm.doc.reference_document
		},
		callback: function (r) {

			if (r) {
				cur_frm.doc.item = []
				console.log(r.message)
				$.each(r.message, function (i, d) {

					var row = frappe.model.add_child(cur_frm.doc, "Reference Doc Records", "item");
					row.reference_doctype = cur_frm.doc.reference_document;
					row.reference_docname = d.name
					row.party = d.customer
					row.grand_total = d.grand_total
					row.status = d.status


				});
				cur_frm.refresh_fields("item");
				cur_frm.save()



			} else {
				cur_frm.doc.item = []
				frappe.throw("No Record Found for Closing")
			}
		},
		always: function () {
			frappe.ui.form.is_saving = false;
		}
	})
}