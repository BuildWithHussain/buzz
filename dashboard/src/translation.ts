import { createResource } from "frappe-ui";
import type { App } from "vue";

export default function translationPlugin(app: App) {
	app.config.globalProperties.__ = translate;
	(window as any).__ = translate;
	if (!(window as any).translatedMessages) fetchTranslations();
}

function format(message: string, replace: any[]) {
	return message.replace(/{(\d+)}/g, function (match, number) {
		return typeof replace[number] != "undefined" ? replace[number] : match;
	});
}

function translate(message: string, replace: any[] = [], context: string | null = null) {
	let translatedMessages = (window as any).translatedMessages || {};
	let translatedMessage = "";

	if (context) {
		let key = `${message}:${context}`;
		if (translatedMessages[key]) {
			translatedMessage = translatedMessages[key];
		}
	}

	if (!translatedMessage) {
		translatedMessage = translatedMessages[message] || message;
	}

	const hasPlaceholders = /{\d+}/.test(message);
	if (!hasPlaceholders) {
		return translatedMessage;
	}

	return format(translatedMessage, replace);
}

function fetchTranslations() {
	createResource({
		url: "buzz.api.get_translations",
		auto: true,
		transform: (data: any) => {
			(window as any).translatedMessages = data;
		},
	});
}
