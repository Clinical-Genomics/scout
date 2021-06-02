/* eslint-disable react/button-has-type */
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { GoogleLogin, GoogleLogout } from 'react-google-login'
import DropdownMenu from 'components/DropdownMenu/DropdownMenu'
import { FaAngleDown } from 'react-icons/fa'
import Tooltip from '@material-ui/core/Tooltip'
import Brightness4OutlinedIcon from '@material-ui/icons/Brightness4Outlined'
import Brightness5OutlinedIcon from '@material-ui/icons/Brightness5Outlined'
import styles from './Nav.module.scss'

export interface Header {
  icon?: string // Path to icon
  title?: string // Name of webpage
}

export interface NavItem {
  linkTitle: string
  public: boolean
  externalLink?: string
  link?: string
  dropdownList?: Array<NavItem>
}

interface Props {
  header?: Header
  navItems: Array<NavItem>
  darkMode: boolean
  toggleDarkMode: Function
}

const { REACT_APP_GOOGLE_OAUTH_CLIENT_ID } = process.env
const clientId = REACT_APP_GOOGLE_OAUTH_CLIENT_ID || 'no-id'

const Nav: React.FC<Props> = ({ header, navItems, darkMode, toggleDarkMode }) => {
  const [userInfo, setUserInfo] = useState('')
  const [isLoaded, setIsLoaded] = useState(false)

  const onLoginSuccess = (response: any) => {
    setUserInfo(response.profileObj.name)
    setIsLoaded(true)
  }

  const onLogoutSuccess = () => {
    setIsLoaded(false)
  }

  return (
    <nav className={styles.Nav}>
      <ul>
        {/* Header */}
        {header?.icon && header?.title && (
          <li key={header.title} className={styles.nav_item}>
            <header>
              <Link to="/" className={styles.header}>
                {header?.icon && <img src={header.icon} alt="Logo" />}
                {header?.title && <span>{header.title}</span>}
              </Link>
            </header>
          </li>
        )}

        {/* Nav items */}
        {navItems.map((navItem) => (
          <li key={navItem.linkTitle} className={styles.nav_item}>
            {/* Link */}
            {navItem.link && <Link to={navItem.link}>{navItem.linkTitle}</Link>}
            {/* External links */}
            {navItem.externalLink && (
              <a href={navItem.externalLink} target="_blank" rel="noopener noreferrer">
                {navItem.linkTitle}
              </a>
            )}

            {/* Dropdown menu */}
            {navItem.dropdownList && (
              <>
                <span>{navItem.linkTitle}</span>
                <div className={styles.dropdown_item_space} />
                <FaAngleDown className={styles.collapse_arrow} />

                <DropdownMenu>
                  {navItem.dropdownList.map((dropDownItem) => (
                    <li key={dropDownItem.linkTitle}>
                      <Link to={dropDownItem.link ? dropDownItem.link : '/'}>
                        {dropDownItem.linkTitle}
                      </Link>
                    </li>
                  ))}
                </DropdownMenu>
              </>
            )}
          </li>
        ))}
      </ul>
      <ul className={styles.nav_settings}>
        <li className={styles.nav_item}>
          <button className="no_button_style flex" onClick={() => toggleDarkMode()}>
            {darkMode && (
              <Tooltip title="Toggle light/dark theme">
                <Brightness5OutlinedIcon />
              </Tooltip>
            )}
            {!darkMode && (
              <Tooltip title="Toggle light/dark theme">
                <Brightness4OutlinedIcon />
              </Tooltip>
            )}
          </button>
        </li>
        {/* Greeting */}
        {isLoaded && (
          <li key="logout" className={styles.nav_item}>
            <span>{`Hi ${userInfo}!`}</span>
            <div className={styles.dropdown_item_space} />
            <FaAngleDown className={styles.collapse_arrow} />
            <DropdownMenu>
              <li>
                <GoogleLogout
                  render={(renderProps) => (
                    <button
                      className="no_button_style"
                      onClick={renderProps.onClick}
                      disabled={renderProps.disabled}
                    >
                      Sign out
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
        {!isLoaded && (
          <li>
            <GoogleLogin
              render={(renderProps) => (
                <button
                  className={`${styles.login_button} btn_style`}
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
    </nav>
  )
}

export default Nav
