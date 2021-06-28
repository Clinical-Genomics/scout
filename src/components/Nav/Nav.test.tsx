import React from 'react'
import { render } from '@testing-library/react'
import Nav, { NavItem } from './Nav'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'

const darkMode = false
// eslint-disable-next-line @typescript-eslint/no-empty-function
const toggleDarkMode = () => {}

const scoutNavItems: Array<NavItem> = [{ linkTitle: 'Home', public: false, link: '/home' }]

test('Nav render correctly', () => {
  const { getByTestId } = render(
    <Router>
      <Nav navItems={scoutNavItems} darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
    </Router>
  )
  const container = getByTestId('NavMenu')
  expect(container).toBeInTheDocument()
})
