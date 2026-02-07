
export interface EventCategory{
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
	/**	Enabled : Check	*/
	enabled?: 0 | 1
	/**	Slug : Data	*/
	slug?: string
	/**	Description : Small Text	*/
	description?: string
	/**	Banner Image : Attach Image	*/
	banner_image?: string
	/**	Icon SVG : Code	*/
	icon_svg?: string
}