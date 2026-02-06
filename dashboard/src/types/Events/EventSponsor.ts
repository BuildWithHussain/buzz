
export interface EventSponsor{
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
	/**	Company Name : Data	*/
	company_name: string
	/**	Company Logo : Attach Image	*/
	company_logo: string
	/**	Website : Data	*/
	website?: string
	/**	Event : Link - Buzz Event	*/
	event: string
	/**	Tier : Link - Sponsorship Tier	*/
	tier: string
	/**	Country : Link - Country	*/
	country?: string
	/**	Enquiry : Link - Sponsorship Enquiry	*/
	enquiry?: string
}