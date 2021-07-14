const { BACKEND_URL } = process.env
const baseUrl = `${BACKEND_URL}/api/v1/`

import { store } from '../domain/store'

export const getAuthHeaders = (token: string) => ({
  'Content-Type': 'application/json;charset=UTF-8',
  'Access-Control-Allow-Origin': '*',
  Accept: 'application/json, text/plain, */*',
  Authorization: `Bearer ${token}`,
})

const getToken = () => {
  const token = store?.getState()?.settings?.googleToken
  return token ? token : ''
}

export const getAnalyses = async (
  token: string = getToken(),
  isVisible?: boolean
): Promise<any> => {
  let response = { analyses: [] }

  try {
    const request = await fetch(`${baseUrl}/institutes/cust00/cases`, {
      mode: 'cors',
      headers: getAuthHeaders(token),
    })
    response = await request.json()
  } catch (error) {
    alert(error)
  }
  return response
}
