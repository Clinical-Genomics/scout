import React from 'react'
import { Link } from 'react-router-dom'
import { FaAngleDown } from 'react-icons/fa'
import { MdBrightness4 } from 'react-icons/md'
import { MdBrightness5 } from 'react-icons/md'
import { Login } from '../Login/Login'
import styles from './Nav.module.css'
import DropdownMenu from 'components/DropdownMenu/DropdownMenu'
import { Tooltip } from 'antd'

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
  toggleDarkMode: () => void
}

const Nav: React.FC<Props> = ({ header, navItems, darkMode, toggleDarkMode }) => {
  return (
    <nav className={styles.Nav} data-testid="NavMenu">
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
          <button
            data-testid="darkMode"
            className="no_button_style flex"
            onClick={() => toggleDarkMode()}
          >
            {darkMode && (
              <Tooltip title="Toggle light theme" placement="bottom">
                <MdBrightness4 className={styles.switchThemeIcon} data-testid="lightModeButton" />
              </Tooltip>
            )}
            {!darkMode && (
              <Tooltip title="Toggle dark theme" placement="bottom">
                <MdBrightness5 className={styles.switchThemeIcon} data-testid="darkModeButton" />
              </Tooltip>
            )}
          </button>
        </li>
        <li className={styles.nav_item}>
          <Login />
        </li>
      </ul>
    </nav>
  )
}

export default Nav
