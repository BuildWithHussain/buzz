import frappe


def execute():
	frappe.reload_doc("ticketing", "doctype", "buzz_coupon_code")

	# 1. Set applies_to = "Event" for all Free Tickets coupons
	# (Free Tickets MUST be event-specific per validation rules)
	frappe.db.sql("""
		UPDATE `tabBuzz Coupon Code`
		SET applies_to = 'Event'
		WHERE coupon_type = 'Free Tickets'
		  AND (applies_to IS NULL OR applies_to = '')
	""")

	# 2. Set applies_to = "Event" for Discount coupons that have event set
	frappe.db.sql("""
		UPDATE `tabBuzz Coupon Code`
		SET applies_to = 'Event'
		WHERE coupon_type = 'Discount'
		  AND event IS NOT NULL AND event != ''
		  AND (applies_to IS NULL OR applies_to = '')
	""")

	# 3. Set applies_to = "Event Category" for Discount coupons that have event_category set
	frappe.db.sql("""
		UPDATE `tabBuzz Coupon Code`
		SET applies_to = 'Event Category'
		WHERE coupon_type = 'Discount'
		  AND event_category IS NOT NULL AND event_category != ''
		  AND (applies_to IS NULL OR applies_to = '')
	""")

	# Coupons with neither event nor event_category remain as global (applies_to = '')
