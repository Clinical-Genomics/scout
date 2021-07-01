import React, { useState } from 'react'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import { GoogleLogin, GoogleLogout } from 'react-google-login'
import { connect } from 'react-redux'
import { RootState } from './domain/rootReducer'
import {
  setUserInfo as setSettingsAction,
  resetUserInfo as resetSettingsAction,
  setGoogleToken as setGoogleTokenAction,
  resetGoogleToken as resetGoogleTokenAction,
} from './domain/settings/slice'
import DropdownMenu from 'components/DropdownMenu/DropdownMenu'
import { FaAngleDown } from 'react-icons/fa'
import { Layout } from './components/Layout/Layout'
import { Home } from './components/Pages/Home/HomePage'
import './App.scss'

const mapDispatch = {
  setUserInfo: setSettingsAction,
  resetUserInfo: resetSettingsAction,
  setGoogleToken: setGoogleTokenAction,
  resetGoogleToken: resetGoogleTokenAction,
} as const

const mapState = ({ settings }: RootState) => ({ settings } as const)

type Props = ReturnType<typeof mapState> & typeof mapDispatch
/*{ setUserInfo, resetUserInfo, setGoogleToken, resetGoogleToken }*/
export const AppComponent = ({
  settings,
  setUserInfo,
  resetUserInfo,
  setGoogleToken,
  resetGoogleToken,
}: Props) => {
  const { REACT_APP_GOOGLE_OAUTH_CLIENT_ID } = process.env
  const clientId = REACT_APP_GOOGLE_OAUTH_CLIENT_ID || 'no-id'
  const [isLoaded, setIsLoaded] = useState(false)

  const onLoginSuccess = (response: any) => {
    setUserInfo(response.profileObj)
    setGoogleToken(response.tokenId)
    setIsLoaded(true)
  }

  const onLogoutSuccess = () => {
    resetUserInfo()
    resetGoogleToken()
    setIsLoaded(false)
  }

  return (
    <Router>
      <Layout>
        <Switch>
          <Route path="/about">About</Route>
          <Route path="/users">Users</Route>
          <Route path="/">
            <Home />
          </Route>
        </Switch>
        {/* Greeting */}
        <ul className="test">
          {settings.googleToken && (
            <li key="logout" className="nav_item">
              <span>{`Hi ${settings?.user?.givenName}!`}</span>
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
                        Sign out test
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
            <li>
              <GoogleLogin
                render={(renderProps) => (
                  <button
                    className="login_button btn_style"
                    onClick={renderProps.onClick}
                    disabled={renderProps.disabled}
                  >
                    Login with Google
                  </button>
                )}
                clientId={clientId}
                buttonText="Login"
                onSuccess={onLoginSuccess}
                isSignedIn={true}
                cookiePolicy="single_host_origin"
              />
            </li>
          )}
        </ul>
      </Layout>
    </Router>
  )
}

export const App = connect(mapState, mapDispatch)(AppComponent)
