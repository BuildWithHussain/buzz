import { TicketCancellationItem } from './TicketCancellationItem'

export interface TicketCancellationRequest{
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
	/**	Booking : Link - Event Booking	*/
	booking: string
	/**	Cancel Full Booking? : Check	*/
	cancel_full_booking?: 0 | 1
	/**	Tickets : Table - Ticket Cancellation Item	*/
	tickets?: TicketCancellationItem[]
	/**	Status : Select	*/
	status?: "In Review" | "Accepted" | "Rejected"
	/**	Amended From : Link - Ticket Cancellation Request	*/
	amended_from?: string
}