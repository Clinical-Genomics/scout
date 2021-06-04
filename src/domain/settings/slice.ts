/* eslint-disable no-param-reassign */
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { AppState } from './types';


export const initialAppState = {
  darkMode: false,
} as AppState;

const settingsSlice = createSlice({
  name: 'settings',
  initialState: initialAppState,
  reducers: {
    setDarkMode(state, action: PayloadAction<any>) {
      state.darkMode = action.payload;
    },
  },
});

export const { setDarkMode } = settingsSlice.actions;

export default settingsSlice.reducer;
