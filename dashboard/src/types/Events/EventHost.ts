import { SocialMediaLink } from './SocialMediaLink'

export interface EventHost{
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
	/**	Logo : Attach Image	*/
	logo?: string
	/**	Country : Link - Country	*/
	country?: string
	/**	Social Media Links : Table - Social Media Link	*/
	social_media_links?: SocialMediaLink[]
	/**	By Line : Data	*/
	by_line?: string
	/**	Address : Small Text	*/
	address?: string
	/**	About : Text Editor	*/
	about?: string
}