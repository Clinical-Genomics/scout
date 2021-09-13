import { createServer, Model } from 'miragejs'
import { getMockCases, getMockCaseReport, getMockPhenotypes } from '../__mocks__/ScoutResponses'

const { BACKEND_URL } = process.env
const baseUrl = `${BACKEND_URL}/api/v1/institutes/`
export function makeServer({ environment = 'test' } = {}) {
  const server = createServer({
    models: {
      cases: Model,
    },
    seeds(server) {
      server.create('case', { getMockCases } as any),
        server.create('case', { getMockCaseReport } as any),
        server.create('case', { getMockPhenotypes } as any)
    },
    routes() {
      /* Need to be replaced when replacing the real API calls */
      /* this.urlPrefix = `${baseUrl}/`
      this.get(`${getInstituteFromURL()}/cases/`, (schema) => {
        let response = schema.cases.all().models[0].attrs.getMockCases
        return response
      })
      this.get(`${getInstituteFromURL()}/case_report/`, (schema) => {
        let response = schema.cases.all().models[1].attrs.getMockCaseReport
        return response
      })
      this.get(`${getInstituteFromURL()}/:id`, (schema, request) => {
        let id = request.params.id
        return schema.cases.find(id)
      }) */
      this.urlPrefix = `https://scout-mocks-data.herokuapp.com`
      this.get(`/cases`, (schema: any) => {
        const response = schema.cases.all().models[0].attrs.getMockCases
        return response
      })
      this.get(`/case_report`, (schema: any) => {
        const response = schema.cases.all().models[1].attrs.getMockCaseReport
        return response
      })
      this.get(`/phenotypes`, (schema: any) => {
        const response = schema.cases.all().models[2].attrs.getMockPhenotypes
        return response.phenotypes
      })
    },
  })
  return server
}
