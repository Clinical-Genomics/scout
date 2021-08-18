import { createServer, Model } from 'miragejs'
import { getMockCases } from '../__mocks__/ScoutResponses'
export function makeServer() {
  let server = createServer({
    models: {
      cases: Model,
    },
    seeds(server) {
      server.create('case', { getMockCases })
    },
    routes() {
      this.namespace = 'api/cases'
      this.get('/', (schema) => {
        return schema.cases.all()
      })
      this.get('/:id', (schema, request) => {
        let id = request.params.id
        return schema.cases.find(id)
      })
    },
  })
  return server
}
