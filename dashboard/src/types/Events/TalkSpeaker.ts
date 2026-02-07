import { SocialMediaLink } from './SocialMediaLink'

export interface TalkSpeaker{
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
	/**	Speaker : Link - Speaker Profile	*/
	speaker: string
	/**	Social Media Links : Table - Social Media Link	*/
	social_media_links?: SocialMediaLink[]
}