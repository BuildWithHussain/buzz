import { createApp } from "vue"

import App from "./App.vue"
import router from "./router"
import { initSocket } from "./socket"

import translationPlugin from "./translation"

import {
	Alert,
	Badge,
	Button,
	Dialog,
	ErrorMessage,
	FormControl,
	Input,
	TextInput,
	frappeRequest,
	pageMetaPlugin,
	resourcesPlugin,
	setConfig,
} from "frappe-ui"

import "./index.css"

const globalComponents = {
	Button,
	TextInput,
	Input,
	FormControl,
	ErrorMessage,
	Dialog,
	Alert,
	Badge,
}

const trackingScripts = (window as any).tracking_scripts
if (trackingScripts) {
	const container = document.createElement("div")
	container.innerHTML = trackingScripts
	for (const node of Array.from(container.childNodes)) {
		if (node.nodeType === Node.ELEMENT_NODE && (node as Element).tagName === "SCRIPT") {
			const source = node as HTMLScriptElement
			const script = document.createElement("script")
			for (const attr of Array.from(source.attributes)) {
				script.setAttribute(attr.name, attr.value)
			}
			script.text = source.text
			document.head.appendChild(script)
		} else {
			document.head.appendChild(node)
		}
	}
}

const app = createApp(App)

setConfig("resourceFetcher", frappeRequest)

app.use(router)
app.use(translationPlugin)
app.use(resourcesPlugin)
app.use(pageMetaPlugin)

const socket = initSocket()
app.config.globalProperties.$socket = socket

for (const [key, component] of Object.entries(globalComponents)) {
	app.component(key, component)
}

app.mount("#app")
