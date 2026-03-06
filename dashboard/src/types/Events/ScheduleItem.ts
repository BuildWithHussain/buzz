
export interface ScheduleItem{
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
	/**	Date : Date	*/
	date: string
	/**	Track : Link - Event Track	*/
	track: string
	/**	Type : Select	*/
	type: "Talk" | "Break"
	/**	Description : Data - Tea Break, Lunch, etc.	*/
	description?: string
	/**	Talk : Link - Event Talk	*/
	talk?: string
	/**	Start Time : Time	*/
	start_time: string
	/**	End Time : Time	*/
	end_time: string
}