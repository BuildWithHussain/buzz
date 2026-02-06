import { TalkSpeaker } from './TalkSpeaker'

export interface EventTalk{
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
	/**	Title : Data	*/
	title: string
	/**	Submitted By : Link - User	*/
	submitted_by: string
	/**	Proposal : Link - Talk Proposal	*/
	proposal?: string
	/**	Event : Link - Buzz Event	*/
	event: string
	/**	Speakers : Table - Talk Speaker	*/
	speakers?: TalkSpeaker[]
	/**	Description : Text Editor	*/
	description?: string
}