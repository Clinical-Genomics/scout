export interface Notification {
	type: 'error' | 'success' | 'info' | 'warning'
	message: string
	description?: string
}
