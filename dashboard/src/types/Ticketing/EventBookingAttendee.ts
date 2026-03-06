
export interface EventBookingAttendee{
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
	/**	Full Name : Data	*/
	full_name: string
	/**	Ticket Type : Link - Event Ticket Type	*/
	ticket_type: string
	/**	Custom Fields : JSON	*/
	custom_fields?: any
	/**	Email : Data	*/
	email: string
	/**	Amount : Currency	*/
	amount?: number
	/**	Currency : Link - Currency	*/
	currency: string
	/**	Add Ons : Link - Attendee Ticket Add-on	*/
	add_ons?: string
	/**	Number of Add Ons : Int	*/
	number_of_add_ons?: number
	/**	Add On Total : Currency	*/
	add_on_total?: number
}