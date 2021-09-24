import { createServer, Model } from 'miragejs'

const { BACKEND_URL } = process.env
const baseUrl = `${BACKEND_URL}/api/v1/institutes/`

export function makeServer({ environment = 'test' } = {}) {
	const server = createServer({
		models: {
			cases: Model,
		},
		// eslint-disable-next-line @typescript-eslint/no-empty-function
		seeds(server) {},
		routes() {
			this.passthrough(`/${BACKEND_URL}/***`)
		},
	})
	return server
}
