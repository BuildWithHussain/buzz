
export interface EventPayment{
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
	/**	Reference DocType : Link - DocType	*/
	reference_doctype?: string
	/**	Reference Name : Dynamic Link	*/
	reference_docname?: string
	/**	Amount : Currency	*/
	amount?: number
	/**	Currency : Link - Currency	*/
	currency?: string
	/**	Payment Received : Check	*/
	payment_received?: 0 | 1
	/**	Payment Gateway : Link - Payment Gateway	*/
	payment_gateway?: string
	/**	Payment ID : Data	*/
	payment_id?: string
	/**	Order ID : Data	*/
	order_id?: string
}