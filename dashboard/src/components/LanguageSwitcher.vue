<template>
	<Dropdown :options="languageOptions">
		<template #default="{ open }">
			<Button variant="ghost" size="md" :loading="isSwitching">
				<LucideLanguages class="w-4 h-4" />
			</Button>
		</template>
	</Dropdown>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Dropdown, Button } from "frappe-ui";
import LucideLanguages from "~icons/lucide/languages";
import { useLanguage } from "@/composables/useLanguage";

interface Language {
	name: string;
	language_name?: string;
	language_code: string;
}

const { availableLanguages, currentLanguage, changeLanguage, isSwitching } = useLanguage();

const languageOptions = computed(() => {
	if (!availableLanguages.data || availableLanguages.data.length === 0) {
		return [];
	}

	return availableLanguages.data.map((lang: Language) => ({
		label: lang.language_name || lang.name,
		icon: currentLanguage.value === lang.language_code ? "check" : undefined,
		onClick: () => changeLanguage(lang.language_code),
	}));
});
</script>
