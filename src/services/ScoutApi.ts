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

export const getInstituteFromURL = () => document?.location.pathname.split('/')[1]
export const getCases = async (): Promise<any> => {
  let response = { cases: [] }
  try {
    const request = await axios.get(`${baseUrl}/institutes/${getInstituteFromURL()}/cases`, {
      headers: getAuthHeaders(),
      withCredentials: true,
    })
    response = request.data
  } catch (error) {
    console.error(error)
  }
  return response
}
