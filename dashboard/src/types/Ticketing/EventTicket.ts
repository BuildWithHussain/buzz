import { AdditionalField } from './AdditionalField'
import { TicketAddOnValue } from './TicketAddOnValue'

export interface EventTicket{
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
	/**	Attendee Name : Data	*/
	attendee_name: string
	/**	Event : Link - Buzz Event	*/
	event?: string
	/**	Booking : Link - Event Booking	*/
	booking?: string
	/**	Coupon Used  : Link - Bulk Ticket Coupon	*/
	coupon_used?: string
	/**	Attendee Email : Data	*/
	attendee_email: string
	/**	Ticket Type : Link - Event Ticket Type	*/
	ticket_type: string
	/**	QR Code : Attach Image	*/
	qr_code?: string
	/**	Additional Fields : Table - Additional Field	*/
	additional_fields?: AdditionalField[]
	/**	Add Ons : Table - Ticket Add-on Value	*/
	add_ons?: TicketAddOnValue[]
	/**	Amended From : Link - Event Ticket	*/
	amended_from?: string
}