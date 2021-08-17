import { createServer, Model } from 'miragejs'
import { getMockCases } from '../__mocks__/ScoutResponses'
export function makeServer({ environment = 'test' } = {}) {
  let server = createServer({
    environment,
    models: {
      cases: Model,
    },
    seeds(server) {
      server.create('case', { getMockCases })
    },
    routes() {
      this.namespace = '/cases'
      this.get('/', (schema) => {
        return schema.cases.all()
      })
    },
  })
  return server
}
