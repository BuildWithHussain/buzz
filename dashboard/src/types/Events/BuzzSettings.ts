
export interface BuzzSettings{
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
	/**	Support Email : Data - Will be linked in emails, etc.	*/
	support_email?: string
	/**	Allow Transfer Ticket Before Event Start (Days) : Int	*/
	allow_transfer_ticket_before_event_start_days?: number
	/**	Allow Add Ons Change Before Event Start (Days) : Int	*/
	allow_add_ons_change_before_event_start_days?: number
	/**	Allow Ticket Cancellation Request Before Event Start (Days) : Int	*/
	allow_ticket_cancellation_request_before_event_start_days?: number
	/**	Default Ticket Email Template : Link - Email Template - Default template for ticket confirmation emails. Can be overridden per event.	*/
	default_ticket_email_template?: string
	/**	Default Feedback Email Template : Link - Email Template - Default template for feedback emails. Can be overridden per event.
<br>
Template uses: <code>{{ feedback_link }}</code>, <code>{{ attendee_name }}</code>, and <code>{{ event_title }}</code>.	*/
	default_feedback_email_template?: string
	/**	Auto Send Pitch Deck : Check	*/
	auto_send_pitch_deck?: 0 | 1
	/**	Default Email Template : Link - Email Template - Default template for sponsorship pitch deck emails. Can be overridden per event.	*/
	default_sponsor_deck_email_template?: string
	/**	Default Reply To : Data	*/
	default_sponsor_deck_reply_to: string
	/**	Default CC : Small Text	*/
	default_sponsor_deck_cc?: string
}