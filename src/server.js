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
      this.urlPrefix = 'https://scout-mocks-data.herokuapp.com'
      this.namespace = '/cases'
      this.get('/', (schema) => {
        let response = schema.cases.all().models[0].attrs.getMockCases.cases
        return response
      })
      this.get('/:id', (schema, request) => {
        let id = request.params.id
        return schema.cases.find(id)
      })
    },
  })
  return server
}
