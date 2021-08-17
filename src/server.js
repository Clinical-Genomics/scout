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
      this.namespace = 'api/cases'
      this.get('/', (schema, request) => {
        return schema.cases.all()
      })
      this.get('/:id', (schema, request) => {
        let id = request.params.id
        return schema.cases.find(id)
      })
      this.post('/', (schema, request) => {
        let attrs = JSON.parse(request.requestBody)
        return schema.cases.create(attrs)
      })
      this.patch('/:id', (schema, request) => {
        let newAttrs = JSON.parse(request.requestBody)
        let id = request.params.id
        let note = schema.cases.find(id)
        return note.update(newAttrs)
      })
      this.delete('/:id', (schema, request) => {
        let id = request.params.id
        return schema.cases.find(id).destroy()
      })
    },
  })
  return server
}
