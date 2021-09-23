import { createErrorNotification } from './helpers/helpers'

const axios = require('axios').default
const { BACKEND_URL } = process.env
const baseUrl = `${BACKEND_URL}/api/v1`

export const getAuthHeaders = () => ({
	headers: {
		Authorization: `Bearer ${document?.cookie},
    'Content-Type': 'application/json;charset=UTF-8',
    'Access-Control-Allow-Origin': '*'`,
	},
})

export const getPhenotypesSearch = async (search: any): Promise<any> => {
	let response = { phenotype: [] }

	try {
		const request = await axios.get(`${baseUrl}/phenotypes/search/${search}`, {
			headers: getAuthHeaders(),
		})
		response = await request.data
	} catch (error: any) {
		createErrorNotification(error)
	}
	return response
}
