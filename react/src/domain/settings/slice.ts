/* eslint-disable no-param-reassign */
import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { AppState, UserInfo } from './types'

const userInitialState = {
  googleId: null,
  imageUrl: null,
  email: null,
  givenName: null,
}

export const initialState = {
  user: userInitialState,
  darkMode: false,
  institutes: [],
  currentInstitute: 'cust000',
} as AppState

const settingsSlice = createSlice({
  name: 'settings',
  initialState: initialState,
  reducers: {
    setUserInfo(state, action: PayloadAction<UserInfo>) {
      state.user = action.payload
    },
    resetUserInfo(state) {
      state.user = initialState.user
    },
    setGoogleToken(state, action: PayloadAction<any>) {
      state.googleToken = action.payload
    },
    resetGoogleToken(state) {
      state.googleToken = initialState.googleToken
    },
    setDarkMode(state, action: PayloadAction<any>) {
      state.darkMode = action.payload
    },
  },
})

export const { setUserInfo, resetUserInfo, setGoogleToken, resetGoogleToken, setDarkMode } =
  settingsSlice.actions

export default settingsSlice.reducer
