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
import { Home } from './components/Home/HomePage'
import './App.css'
import DropdownMenu from './components/DropdownMenu/DropdownMenu'
import { Menu, Dropdown, Button, message, Space, Tooltip } from 'antd'
import { DownOutlined, MailOutlined, GoogleOutlined } from '@ant-design/icons'
import { CasesPage } from './modules/Cases/CasesPage'

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

  const loginMenu = (
    <Menu>
      <Menu.Item key="1" icon={<GoogleOutlined />}>
        <GoogleLogin
          render={(renderProps) => (
            <button
              onClick={renderProps.onClick}
              disabled={renderProps.disabled}
              className="google-login_button"
            >
              Login with Google
            </button>
          )}
          clientId={clientId}
          onSuccess={onLoginSuccess}
          isSignedIn={true}
          cookiePolicy="single_host_origin"
        />
      </Menu.Item>
      <Menu.Item key="2" icon={<MailOutlined />} disabled>
        Login with Email
      </Menu.Item>
    </Menu>
  )

  const loginOutMenu = (
    <Menu>
      <Menu.Item key="1">
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
      </Menu.Item>
    </Menu>
  )

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
        {/* Greeting */}
        <ul className="login">
          {settings.googleToken && (
            <li key="logout" className="nav_item">
              <div className="dropdown_item_space" />
              <Dropdown overlay={loginOutMenu} placement="bottomLeft">
                <Button>
                  <span className="login-dropdown-header">{`Hi ${settings?.user?.givenName}!`}</span>{' '}
                  <DownOutlined />
                </Button>
              </Dropdown>
            </li>
          )}
          {/* Login button */}
          {!settings?.googleToken && (
            <li key="logout" className="nav_item">
              <div className="dropdown_item_space" />
              <Dropdown overlay={loginMenu} placement="bottomLeft">
                <Button>
                  Login <DownOutlined />
                </Button>
              </Dropdown>
            </li>
          )}
        </ul>
      </Layout>
    </Router>
  )
}

export const App = connect(mapState, mapDispatch)(AppComponent)
