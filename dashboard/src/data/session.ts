import router from "@/router";
import { createResource } from "frappe-ui";
import { computed, reactive } from "vue";
import { userResource } from "./user";
import { clearBookingCache } from "@/utils";

interface LoginParams {
	email: string;
	password: string;
}

interface LoginResponse {
	default_route?: string;
}

export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"));
	let _sessionUser = cookies.get("user_id");
	if (_sessionUser === "Guest") {
		_sessionUser = null;
	}
	return _sessionUser;
}

export const session = reactive({
	login: createResource({
		url: "login",
		makeParams({ email, password }: LoginParams) {
			return {
				usr: email,
				pwd: password,
			};
		},
		onSuccess(data: LoginResponse) {
			userResource.reload();
			session.user = sessionUser();
			session.login.reset();
			router.replace(data.default_route || "/");
		},
	}),
	logout: createResource({
		url: "logout",
		onSuccess() {
			userResource.reset();
			session.user = sessionUser();
			clearBookingCache();
			const redirect_to = window.location.pathname + window.location.search;
			window.location.href = `/login?redirect-to=${encodeURIComponent(redirect_to)}`;
		},
	}),
	user: sessionUser(),
	isLoggedIn: computed((): boolean => !!session.user),
});
