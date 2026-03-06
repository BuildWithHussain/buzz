import { EventBookingAttendee } from './EventBookingAttendee'
import { AdditionalField } from './AdditionalField'
import { UTMParameter } from '../Events/UTMParameter'

export interface EventBooking{
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
	/**	Event : Link - Buzz Event	*/
	event: string
	/**	User : Link - User	*/
	user: string
	/**	Naming Series : Select	*/
	naming_series?: "B.###"
	/**	Attendees : Table - Event Booking Attendee	*/
	attendees: EventBookingAttendee[]
	/**	Additional Fields : Table - Additional Field	*/
	additional_fields?: AdditionalField[]
	/**	Net Amount : Currency	*/
	net_amount?: number
	/**	Tax Percentage : Percent	*/
	tax_percentage?: number
	/**	Tax Label : Data	*/
	tax_label?: string
	/**	Tax Amount : Currency	*/
	tax_amount?: number
	/**	Total Amount : Currency	*/
	total_amount?: number
	/**	Currency : Link - Currency	*/
	currency: string
	/**	Coupon Code : Link - Buzz Coupon Code	*/
	coupon_code?: string
	/**	Discount Amount : Currency	*/
	discount_amount?: number
	/**	Amended From : Link - Event Booking	*/
	amended_from?: string
	/**	UTM Parameters : Table - UTM Parameter	*/
	utm_parameters?: UTMParameter[]
}