import { createResource } from "frappe-ui";
import type { FrappeError } from "@/types/Frappe/FrappeError";

export const userResource = createResource({
	url: "buzz.api.get_user_info",
	cache: "User",
	onError(error: FrappeError) {
		if (error && error.exc_type === "AuthenticationError") {
			window.location.href = "/login?redirect-to=dashboard";
		}
	},
});
