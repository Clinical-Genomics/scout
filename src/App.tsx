import React from 'react'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import { GoogleLogin, GoogleLogout } from 'react-google-login'
import Cookies from 'js-cookie'
import { connect } from 'react-redux'
import { RootState } from './domain/rootReducer'
import {
  setUserInfo as setSettingsAction,
  resetUserInfo as resetSettingsAction,
  setGoogleToken as setGoogleTokenAction,
  resetGoogleToken as resetGoogleTokenAction,
} from './domain/settings/slice'
import { FaAngleDown } from 'react-icons/fa'
import { Layout } from './components/Layout/Layout'
import { Button } from 'antd'
import { Home } from './components/Home/HomePage'
import './App.css'
import DropdownMenu from './components/DropdownMenu/DropdownMenu'
import { CasesPage } from './modules/Cases/CasesPage'
import { CasePage } from 'modules/Case/CasePage'
import { CaseReportPage } from './modules/CaseReportPage/CaseReportPage'

const mapDispatch = {
  setUserInfo: setSettingsAction,
  resetUserInfo: resetSettingsAction,
  setGoogleToken: setGoogleTokenAction,
  resetGoogleToken: resetGoogleTokenAction,
} as const

const { GOOGLE_OAUTH_CLIENT_ID } = process.env

const mapState = ({ settings }: RootState) => ({ settings } as const)
type Props = ReturnType<typeof mapState> & typeof mapDispatch

export const AppComponent = ({
  settings,
  setUserInfo,
  resetUserInfo,
  setGoogleToken,
  resetGoogleToken,
}: Props) => {
  const clientId = GOOGLE_OAUTH_CLIENT_ID || 'no-id'

  const onLoginSuccess = (response: any) => {
    setUserInfo(response.profileObj)
    setGoogleToken(response.tokenId)
    Cookies.set('scout_remember_me', `${response.profileObj.email}|${response.tokenId}`, {
      expires: 365,
      path: '',
    })
  }

  const onLogoutSuccess = () => {
    resetUserInfo()
    resetGoogleToken()
    Cookies.remove('scout_remember_me', { path: '' })
  }

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
          <Route path={`/${settings.currentInstitute}/:caseId`} exact>
            <CasePage />
          </Route>
          <Route path={`/${settings.currentInstitute}/:caseId/case_report`} exact>
            <CaseReportPage />
          </Route>
        </Switch>
        {/* Greeting */}
        <ul className="login">
          {settings.googleToken && (
            <li key="logout" className="nav_item">
              <span className="login-dropdown-header">{`Hi ${settings?.user?.givenName}!`}</span>
              <div className="dropdown_item_space" />
              <FaAngleDown className="collapse_arrow" />
              <DropdownMenu>
                <li>
                  <GoogleLogout
                    render={(renderProps) => (
                      <button
                        className="no_button_style"
                        onClick={renderProps.onClick}
                        disabled={renderProps.disabled}
                      >
                        Logout
                      </button>
                    )}
                    clientId={clientId}
                    buttonText="Sign out"
                    onLogoutSuccess={onLogoutSuccess}
                  />
                </li>
              </DropdownMenu>
            </li>
          )}
          {/* Login button */}
          {!settings?.googleToken && (
            <li key="logout" className="nav_item">
              <span className="login-dropdown-header">Login</span>
              <div className="dropdown_item_space" />
              <FaAngleDown className="collapse_arrow" />
              <DropdownMenu>
                <li>
                  <GoogleLogin
                    render={(renderProps) => (
                      <button
                        className="google-login_button btn_style"
                        onClick={renderProps.onClick}
                        disabled={renderProps.disabled}
                      >
                        Login with Google
                      </button>
                    )}
                    clientId={clientId}
                    onSuccess={onLoginSuccess}
                    isSignedIn={true}
                    cookiePolicy="single_host_origin"
                  />
                </li>
                <li>
                  <Button color="primary">Login with email</Button>
                </li>
              </DropdownMenu>
            </li>
          )}
        </ul>
      </Layout>
    </Router>
  )
}

export const App = connect(mapState, mapDispatch)(AppComponent)
