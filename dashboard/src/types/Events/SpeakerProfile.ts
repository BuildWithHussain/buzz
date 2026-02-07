import { SocialMediaLink } from './SocialMediaLink'

export interface SpeakerProfile{
	name: number
	creation: string
	modified: string
	owner: string
	modified_by: string
	docstatus: 0 | 1 | 2
	parent?: string
	parentfield?: string
	parenttype?: string
	idx?: number
	/**	User : Link - User	*/
	user: string
	/**	Display Name : Data	*/
	display_name?: string
	/**	Display Image : Attach Image	*/
	display_image?: string
	/**	Designation : Data	*/
	designation?: string
	/**	Company : Data	*/
	company?: string
	/**	Social Media Links : Table - Social Media Link	*/
	social_media_links?: SocialMediaLink[]
}