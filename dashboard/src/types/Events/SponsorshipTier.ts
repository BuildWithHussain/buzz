
export interface SponsorshipTier{
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
	/**	Title : Data	*/
	title: string
	/**	Event : Link - Buzz Event	*/
	event: string
	/**	Price : Currency	*/
	price?: number
	/**	Currency : Link - Currency	*/
	currency?: string
}