import { TicketAddOnValue } from './TicketAddOnValue'

export interface AttendeeTicketAddOn{
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
	attendee_name?: string
	/**	Add ons : Table - Ticket Add-on Value	*/
	add_ons?: TicketAddOnValue[]
}