import { clearBookingCache } from "@/utils"
import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"
import { userResource } from "./user"

interface LoginParams {
	email: string
	password: string
}

export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	let _sessionUser = cookies.get("user_id")
	if (_sessionUser === "Guest") {
		_sessionUser = null
	}
	return _sessionUser
}

export const session = reactive({
	login: createResource({
		url: "login",
		makeParams({ email, password }: LoginParams) {
			return {
				usr: email,
				pwd: password,
			}
		},
		onSuccess() {
			window.location.reload()
		},
	}),
	logout: createResource({
		url: "logout",
		onSuccess() {
			userResource.reset()
			session.user = sessionUser()
			clearBookingCache()
			window.location.reload()
		},
	}),
	user: sessionUser(),
	isLoggedIn: computed((): boolean => !!session.user),
})
