import frappe


def execute():
	BuzzCouponCode = frappe.qb.DocType("Buzz Coupon Code")

	# 1. Set applies_to = "Event" for all Free Tickets coupons
	(
		frappe.qb.update(BuzzCouponCode)
		.set(BuzzCouponCode.applies_to, "Event")
		.where(BuzzCouponCode.coupon_type == "Free Tickets")
		.where((BuzzCouponCode.applies_to.isnull()) | (BuzzCouponCode.applies_to == ""))
	).run()

	# 2. Set applies_to = "Event" for Discount coupons that have event set
	(
		frappe.qb.update(BuzzCouponCode)
		.set(BuzzCouponCode.applies_to, "Event")
		.where(BuzzCouponCode.coupon_type == "Discount")
		.where(BuzzCouponCode.event.isnotnull())
		.where(BuzzCouponCode.event != "")
		.where((BuzzCouponCode.applies_to.isnull()) | (BuzzCouponCode.applies_to == ""))
	).run()

	# 3. Set applies_to = "Event Category" for Discount coupons that have event_category set
	(
		frappe.qb.update(BuzzCouponCode)
		.set(BuzzCouponCode.applies_to, "Event Category")
		.where(BuzzCouponCode.coupon_type == "Discount")
		.where(BuzzCouponCode.event_category.isnotnull())
		.where(BuzzCouponCode.event_category != "")
		.where((BuzzCouponCode.applies_to.isnull()) | (BuzzCouponCode.applies_to == ""))
	).run()

	# Coupons with neither event nor event_category remain as global (applies_to = '')
