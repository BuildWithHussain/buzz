import { AdditionalField } from '../Ticketing/AdditionalField'

export interface EventFeedback{
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
	/**	Comment : Small Text	*/
	comment?: string
	/**	Ticket : Link - Event Ticket	*/
	ticket: string
	/**	Rating : Rating	*/
	rating: any
	/**	Additional Fields : Table - Additional Field	*/
	additional_fields?: AdditionalField[]
}