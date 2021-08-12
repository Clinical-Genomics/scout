import React from 'react'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import { connect } from 'react-redux'
import { RootState } from './domain/rootReducer'
import {
  setUserInfo as setSettingsAction,
  resetUserInfo as resetSettingsAction,
  setGoogleToken as setGoogleTokenAction,
  resetGoogleToken as resetGoogleTokenAction,
} from './domain/settings/slice'
import { Layout } from './components/Layout/Layout'
import { Home } from './components/Home/HomePage'
import './App.css'
import { CasesPage } from './modules/Cases/CasesPage'

const mapDispatch = {
  setUserInfo: setSettingsAction,
  resetUserInfo: resetSettingsAction,
  setGoogleToken: setGoogleTokenAction,
  resetGoogleToken: resetGoogleTokenAction,
} as const

const mapState = ({ settings }: RootState) => ({ settings } as const)
type Props = ReturnType<typeof mapState> & typeof mapDispatch

export const AppComponent = ({ settings }: Props) => {
  return (
    <Router>
      <Layout>
        <Switch>
          <Route path="/" exact>
            <Home />
          </Route>
          <Route path={`/${settings.currentInstitute}/cases`} exact>
            <CasesPage />
          </Route>
        </Switch>
      </Layout>
    </Router>
  )
}

export const App = connect(mapState, mapDispatch)(AppComponent)
