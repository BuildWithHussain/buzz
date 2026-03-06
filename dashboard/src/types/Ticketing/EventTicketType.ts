
export interface EventTicketType{
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
	/**	Title : Data - VIP, Early Bird, etc.	*/
	title: string
	/**	Price : Currency	*/
	price?: number
	/**	Currency : Link - Currency	*/
	currency: string
	/**	Event : Link - Buzz Event	*/
	event: string
	/**	Is Published? : Check	*/
	is_published?: 0 | 1
	/**	Auto Unpublish After : Date - For Early Bird, etc.	*/
	auto_unpublish_after?: string
	/**	Max Tickets Available : Int - Leave it 0 for no limit	*/
	max_tickets_available?: number
	/**	Tickets Sold : Int	*/
	tickets_sold?: number
	/**	Remaining Tickets : Int - -1 if no limit defined above	*/
	remaining_tickets?: number
}