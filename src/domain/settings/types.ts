export type UserInfo = {
  googleId: string | null
  imageUrl: string | null
  email: string | null
  givenName: string | null
}

export type AppState = {
  user: UserInfo | null
  googleToken: string | null
  darkMode: boolean
}
