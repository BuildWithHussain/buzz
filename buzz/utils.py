import functools

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def add_buzz_user_role(doc, event=None):
	doc.add_roles("Buzz User")


# https://github.com/resilient-tech/india-compliance/blob/f259e9d1408a1cbb85c91146df3b5baa72e5fafb/india_compliance/utils/custom_fields.py
def make_custom_fields(custom_fields, module_name, *args, **kwargs):
	for _doctypes, fields in custom_fields.items():
		if isinstance(fields, dict):
			fields = (fields,)

		for field in fields:
			field["module"] = module_name

	return create_custom_fields(custom_fields, *args, **kwargs)


# https://github.com/resilient-tech/india-compliance/blob/f259e9d1408a1cbb85c91146df3b5baa72e5fafb/india_compliance/utils/custom_fields.py
def get_custom_fields_creator(module_name):
	return functools.partial(make_custom_fields, module_name=module_name)


# https://github.com/resilient-tech/india-compliance/blob/f259e9d1408a1cbb85c91146df3b5baa72e5fafb/india_compliance/utils/custom_fields.py#L54C1-L77C48
def delete_custom_fields(custom_fields):
	"""
	:param custom_fields: a dict like `{'Sales Invoice': [{fieldname: 'test', ...}]}`
	"""

	for doctypes, fields in custom_fields.items():
		if isinstance(fields, dict):
			# only one field
			fields = [fields]

		if isinstance(doctypes, str):
			# only one doctype
			doctypes = (doctypes,)

		for doctype in doctypes:
			frappe.db.delete(
				"Custom Field",
				{
					"fieldname": ("in", [field["fieldname"] for field in fields]),
					"dt": doctype,
				},
			)

			frappe.clear_cache(doctype=doctype)
