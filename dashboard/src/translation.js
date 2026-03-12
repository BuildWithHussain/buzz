import { createResource } from "frappe-ui";

export default function translationPlugin(app) {
	app.config.globalProperties.__ = translate;
	window.__ = translate;
	if (!window.translatedMessages) fetchTranslations();
}

function format(message, replace) {
	return message.replace(/{(\d+)}/g, (match, number) =>
		typeof replace[number] != "undefined" ? replace[number] : match
	);
}

function translate(message, replace, context = null) {
	const translatedMessages = window.translatedMessages || {};
	let translatedMessage = "";

	if (context) {
		const key = `${message}:${context}`;
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

function fetchTranslations(lang) {
	createResource({
		url: "buzz.api.get_translations",
		auto: true,
		transform: (data) => {
			window.translatedMessages = data;
		},
	});
}
