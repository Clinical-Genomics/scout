import { combineReducers } from '@reduxjs/toolkit';
import settings from './settings/slice';

export const rootReducer = combineReducers({ settings });

export type RootState = ReturnType<typeof rootReducer>;