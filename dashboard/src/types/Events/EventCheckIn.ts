
export interface EventCheckIn{
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
	/**	Date : Date	*/
	date?: string
	/**	Ticket : Link - Event Ticket	*/
	ticket: string
	/**	Amended From : Link - Event Check In	*/
	amended_from?: string
}