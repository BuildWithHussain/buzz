export function isImage(extention) {
	if (!extention) return false;
	return ["png", "jpg", "jpeg", "gif", "svg", "bmp", "webp"].includes(extention.toLowerCase());
}

export function validateIsImageFile(file) {
	const extn = file.name.split(".").pop().toLowerCase();
	if (!isImage(extn)) {
		return "Only image files are allowed";
	}
}

/**
 * Clear all booking-related data from localStorage
 * This removes all keys that start with 'event-booking-'
 */
export function clearBookingCache() {
	const keysToRemove = [];
	for (let i = 0; i < localStorage.length; i++) {
		const key = localStorage.key(i);
		if (key && key.startsWith("event-booking-")) {
			keysToRemove.push(key);
		}
	}
	keysToRemove.forEach((key) => localStorage.removeItem(key));
}

/**
 * Redirect to login page with current path as redirect-to parameter
 */
export function redirectToLogin() {
	const currentPath = window.location.pathname + window.location.search;
	window.location.href = `/login?redirect-to=${encodeURIComponent(currentPath)}`;
}
