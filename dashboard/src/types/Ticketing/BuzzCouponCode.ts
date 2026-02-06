import { CouponFreeAddOn } from './CouponFreeAddOn'

export interface BuzzCouponCode{
	name: string
	creation: string
	modified: string
	owner: string
	modified_by: string
	docstatus: 0 | 1 | 2
	parent?: string
	parentfield?: string
	parenttype?: string
	idx?: number
	/**	Code : Data - Leave empty to auto-generate	*/
	code?: string
	/**	Coupon Type : Select	*/
	coupon_type: "Free Tickets" | "Discount"
	/**	Applies To : Select	*/
	applies_to?: "" | "Event" | "Event Category"
	/**	Is Active : Check	*/
	is_active?: 0 | 1
	/**	Event : Link - Buzz Event	*/
	event?: string
	/**	Event Category : Link - Event Category	*/
	event_category?: string
	/**	Ticket Type : Link - Event Ticket Type	*/
	ticket_type?: string
	/**	Number of Free Tickets : Int	*/
	number_of_free_tickets?: number
	/**	Discount Type : Select	*/
	discount_type?: "Percentage" | "Flat Amount"
	/**	Discount Value : Float	*/
	discount_value?: number
	/**	Maximum Discount Amount : Float	*/
	maximum_discount_amount?: number
	/**	Minimum Order Value : Float	*/
	minimum_order_value?: number
	/**	Valid From : Date - Coupon active from this date (leave empty for immediate)	*/
	valid_from?: string
	/**	Valid Till : Date - Coupon expires after this date (leave empty for no expiry)	*/
	valid_till?: string
	/**	Max Usage Count : Int - 0 is unlimited	*/
	max_usage_count?: number
	/**	Max Usage Per User : Int - 0 = unlimited	*/
	max_usage_per_user?: number
	/**	Free Add-ons : Table - Coupon Free Add-on	*/
	free_add_ons?: CouponFreeAddOn[]
	/**	Times Used : Int	*/
	times_used?: number
	/**	Free Tickets Claimed : Int	*/
	free_tickets_claimed?: number
}