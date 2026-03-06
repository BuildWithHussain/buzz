
export interface UTMParameter{
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
	/**	UTM Name : Data	*/
	utm_name: string
	/**	Value : Small Text	*/
	value: string
}