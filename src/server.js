import { createServer, Model } from 'miragejs'
import { getMockCases, getMockCaseReport } from '../__mocks__/ScoutResponses'
export function makeServer() {
  let server = createServer({
    models: {
      cases: Model,
    },
    seeds(server) {
      server.create('case', { getMockCases }), server.create('case', { getMockCaseReport })
    },
    routes() {
      this.urlPrefix = 'https://scout-mocks-data.herokuapp.com'
      this.get('cases/', (schema) => {
        let response = schema.cases.all().models[0].attrs.getMockCases
        return response
      })
      this.get('case_report/', (schema) => {
        let response = schema.cases.all().models[1].attrs.getMockCaseReport
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
