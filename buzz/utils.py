import functools
from collections.abc import Callable

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def only_if_app_installed(app_name: str, raise_exception: bool = False) -> Callable:
	"""
	Decorator to check if a specified app is installed before running the function.

	:param app_name: The name of the app to check for installation.
	:param raise_exception: If True, raises an exception if the app is not installed.
	                        If False, the function silently returns None.
	:return: The decorated function.
	"""

	def decorator(func: Callable) -> Callable:
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			installed_apps = frappe.get_installed_apps()
			if app_name not in installed_apps:
				if raise_exception:
					frappe.throw(
						frappe._("This feature requires the <b>{0}</b> app to be installed.").format(app_name)
					)
				return None
			return func(*args, **kwargs)

		return wrapper

	return decorator


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


def make_qr_image(data: str) -> bytes:
	"""
	Generate QR code image bytes from data string.

	:param data: The data to encode in the QR code
	:return: PNG image as bytes
	"""
	import io

	import qrcode
	from qrcode.image.styledpil import StyledPilImage
	from qrcode.image.styles.moduledrawers.pil import HorizontalBarsDrawer

	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_H,
		box_size=10,
		border=4,
	)
	qr.add_data(data)
	qr.make(fit=True)

	img = qr.make_image(image_factory=StyledPilImage, module_drawer=HorizontalBarsDrawer())
	output = io.BytesIO()
	img.save(output, format="PNG")
	return output.getvalue()


def generate_qr_code_file(doc, data: str, field_name: str = "qr_code", file_prefix: str = "qr-code") -> str:
	"""
	Generate QR code image and attach as File to a document.

	:param doc: The Frappe document to attach the QR code to
	:param data: The data to encode in the QR code
	:param field_name: The field name to attach the file to (default: "qr_code")
	:param file_prefix: Prefix for the file name (default: "qr-code")
	:return: The file URL of the created QR code image
	"""
	qr_data = make_qr_image(data)
	qr_code_file = frappe.get_doc(
		{
			"doctype": "File",
			"content": qr_data,
			"attached_to_doctype": doc.doctype,
			"attached_to_name": doc.name,
			"attached_to_field": field_name,
			"file_name": f"{file_prefix}-{doc.name}.png",
		}
	).save(ignore_permissions=True)
	return qr_code_file.file_url
