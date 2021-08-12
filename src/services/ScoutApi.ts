const { BACKEND_URL } = process.env
const baseUrl = `${BACKEND_URL}/api/v1`

export const getAuthHeaders = () => ({
  'Content-Type': 'application/json;charset=UTF-8',
  'Access-Control-Allow-Origin': '*',
  Cookie: document?.cookie,
})

export const getInstituteFromURL = () => document?.location.pathname.split('/')[1]

export const getCaseFromURL = () => document?.location.pathname.split('/')[2]

export const getCases = async (): Promise<any> => {
  let response = { cases: [] }

  try {
    const request = await fetch(`${baseUrl}/institutes/${getInstituteFromURL()}/cases`, {
      mode: 'cors',
      headers: getAuthHeaders(),
    })
    response = await request.json()
  } catch (error) {
    console.error(error)
  }
  return response
}

export const getCaseReport = async (): Promise<any> => {
  let response = { report: [] }

  try {
    const request = await fetch(
      `${baseUrl}/institutes/${getInstituteFromURL()}/${getCaseFromURL()}/case_report`,
      {
        mode: 'cors',
        headers: getAuthHeaders(),
      }
    )
    response = await request.json()
  } catch (error) {
    console.error(error)
  }
  return response
}
