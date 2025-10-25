import frappe


def add_buzz_user_role(doc, event=None):
	doc.add_roles("Buzz User")
