import React from 'react'
import { render } from '@testing-library/react'
import Nav, { NavItem } from './Nav'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'

const darkMode = false
// eslint-disable-next-line @typescript-eslint/no-empty-function
const toggleDarkMode = () => {}

const scoutNavItemsTest: Array<NavItem> = [{ linkTitle: 'Test', public: false, link: '/test' }]

test('Nav render correctly', () => {
  const { getByTestId } = render(
    <Router>
      <Nav navItems={scoutNavItemsTest} darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
    </Router>
  )
  const container = getByTestId('NavMenu')
  expect(container.firstChild.textContent).toBe('Test')
})
