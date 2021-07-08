/* eslint-disable react/button-has-type */
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { FaAngleDown } from 'react-icons/fa'
import Tooltip from '@material-ui/core/Tooltip'
import Brightness4OutlinedIcon from '@material-ui/icons/Brightness4Outlined'
import Brightness5OutlinedIcon from '@material-ui/icons/Brightness5Outlined'
import DropdownMenu from 'components/DropdownMenu/DropdownMenu'

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
    <nav className={'styles.Nav'} data-testid="NavMenu">
    </nav>
  )
}

export default Nav
