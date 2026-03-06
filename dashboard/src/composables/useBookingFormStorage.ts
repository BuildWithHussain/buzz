import { useStorage } from "@vueuse/core";

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
	const attendees = useStorage(`${storageKeyPrefix}-attendees`, []);
	const attendeeIdCounter = useStorage(`${storageKeyPrefix}-counter`, 0);
	const bookingCustomFields = useStorage(`${storageKeyPrefix}-custom-fields`, {});

	const guestFullName = useStorage(`${storageKeyPrefix}-guest-name`, "");
	const guestEmail = useStorage(`${storageKeyPrefix}-guest-email`, "");
	const guestPhone = useStorage(`${storageKeyPrefix}-guest-phone`, "");

	/**
	 * Clear all stored booking form data
	 * This should be called when payment is successful
	 */
	const clearStoredData = () => {
		attendees.value = [];
		attendeeIdCounter.value = 0;
		bookingCustomFields.value = {};
		guestFullName.value = "";
		guestEmail.value = "";
		guestPhone.value = "";
	};

	/**
	 * Check if there's any stored booking data
	 */
	const hasStoredData = () => {
		return attendees.value.length > 0 || Object.keys(bookingCustomFields.value).length > 0;
	};

	return {
		attendees,
		attendeeIdCounter,
		bookingCustomFields,
		guestFullName,
		guestEmail,
		guestPhone,
		clearStoredData,
		hasStoredData,
	};
}
