
export interface ProposalSpeaker{
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
	/**	First Name : Data	*/
	first_name: string
	/**	Last Name : Data	*/
	last_name?: string
	/**	Email : Data	*/
	email: string
}