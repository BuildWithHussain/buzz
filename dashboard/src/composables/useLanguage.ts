import { createResource } from "frappe-ui";
import { computed, type ComputedRef } from "vue";
import { userResource } from "@/data/user";

interface LanguageComposable {
  availableLanguages: any;
  currentLanguage: ComputedRef<string>;
  changeLanguage: (languageCode: string) => void;
  isSwitching: ComputedRef<boolean>;
}

export function useLanguage(): LanguageComposable {
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

	function changeLanguage(languageCode: string) {
		switchLanguage.submit({ language_code: languageCode });
	}

	return {
		availableLanguages,
		currentLanguage,
		changeLanguage,
		isSwitching: computed(() => switchLanguage.loading),
	};
}
