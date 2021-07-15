const { BACKEND_URL } = process.env
const baseUrl = `${BACKEND_URL}/api/v1`

export const getAuthHeaders = () => ({
  'Content-Type': 'application/json;charset=UTF-8',
  'Access-Control-Allow-Origin': '*',
  Cookie: document?.cookie,
})

export const getInstituteFromURL = () => document?.location.pathname.split('/')[1]

export const getCases = async (): Promise<any> => {
  let response = { analyses: [] }

  try {
    const request = await fetch(`${baseUrl}/institutes/${getInstituteFromURL()}/cases`, {
      mode: 'cors',
      headers: getAuthHeaders(),
    })
    response = await request.json()
  } catch (error) {
    alert(error)
  }
  return response
}
