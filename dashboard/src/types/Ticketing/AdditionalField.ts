
export interface AdditionalField{
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
	/**	Label : Data	*/
	label?: string
	/**	Fieldname : Data	*/
	fieldname: string
	/**	Value : Data	*/
	value: string
	/**	Fieldtype : Data	*/
	fieldtype?: string
}