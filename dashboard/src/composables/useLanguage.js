import { createResource } from "frappe-ui";
import { computed } from "vue";
import { userResource } from "@/data/user";

export function useLanguage() {
	const availableLanguages = createResource({
		url: "buzz.api.get_enabled_languages",
		auto: true,
		cache: "enabled_languages",
	});

	const currentLanguage = computed(() => {
		return userResource.data?.language || "en";
	});

	const switchLanguage = createResource({
		url: "buzz.api.update_user_language",
		onSuccess() {
			// Reload the page to apply new translations
			window.location.reload();
		},
	});

	function changeLanguage(languageCode) {
		switchLanguage.submit({ language_code: languageCode });
	}

	return {
		availableLanguages,
		currentLanguage,
		changeLanguage,
		isSwitching: computed(() => switchLanguage.loading),
	};
}
