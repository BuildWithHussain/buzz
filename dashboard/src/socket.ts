import { io, type Socket } from "socket.io-client";
// @ts-ignore: sites folder is outside dashboard
import siteConfig from "../../../../sites/common_site_config.json";

let socket: Socket | null = null;

export function initSocket() {
	const host = window.location.hostname;
	const siteName = (window as any).site_name;
	const socketio_port = siteConfig.socketio_port;
	const port = window.location.port ? `:${socketio_port}` : "";
	const protocol = port ? "http" : "https";
	const url = `${protocol}://${host}${port}/${siteName}`;

	socket = io(url, {
		withCredentials: true,
		reconnectionAttempts: 5,
	});
	return socket;
}

export function useSocket() {
	return socket;
}
