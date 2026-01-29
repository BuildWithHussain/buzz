import { useStorage } from "@vueuse/core";
import type { EventBookingAttendee } from "@/types/doctypes";

export interface Attendee extends Omit<Partial<EventBookingAttendee>, "add_ons" | "custom_fields"> {
	id: number;
	add_ons: Record<
		string,
		{
			selected: boolean;
			option: string | null;
		}
	>;
	custom_fields: Record<string, any>;
}

/**
 * Composable for managing booking form localStorage data
 * This allows components to access and clear booking form data stored in localStorage
 * @param {string} eventRoute - The event route to scope the storage keys
 */
export function useBookingFormStorage(eventRoute: string) {
	if (!eventRoute) {
		throw new Error("eventRoute is required for useBookingFormStorage");
	}

	// Scope storage keys to the specific event route
	const storageKeyPrefix = `event-booking-${eventRoute}`;
	const attendees = useStorage<Attendee[]>(`${storageKeyPrefix}-attendees`, []);
	const attendeeIdCounter = useStorage<number>(`${storageKeyPrefix}-counter`, 0);
	const bookingCustomFields = useStorage<Record<string, any>>(`${storageKeyPrefix}-custom-fields`, {});

	/**
	 * Clear all stored booking form data
	 * This should be called when payment is successful
	 */
	const clearStoredData = () => {
		attendees.value = [];
		attendeeIdCounter.value = 0;
		bookingCustomFields.value = {};
	};

	/**
	 * Check if there's any stored booking data
	 */
	const hasStoredData = (): boolean => {
		return attendees.value.length > 0 || Object.keys(bookingCustomFields.value).length > 0;
	};

	return {
		attendees,
		attendeeIdCounter,
		bookingCustomFields,
		clearStoredData,
		hasStoredData,
	};
}
