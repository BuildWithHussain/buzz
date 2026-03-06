
export interface TicketAddOnValue{
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
	/**	Add on : Link - Ticket Add-on	*/
	add_on: string
	/**	Value : Autocomplete	*/
	value: any
	/**	Price : Currency	*/
	price?: number
	/**	Currency : Link - Currency	*/
	currency?: string
}