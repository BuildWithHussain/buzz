
export interface TicketAddOn{
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
	/**	Enabled? : Check	*/
	enabled?: 0 | 1
	/**	Title : Data	*/
	title: string
	/**	Event : Link - Buzz Event	*/
	event: string
	/**	Price : Currency	*/
	price?: number
	/**	Description : Small Text	*/
	description?: string
	/**	Currency : Link - Currency	*/
	currency?: string
	/**	User Selects Option? : Check	*/
	user_selects_option?: 0 | 1
	/**	Options : Small Text	*/
	options?: string
}