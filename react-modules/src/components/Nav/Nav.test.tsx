import React from 'react'
import { BrowserRouter as Router } from 'react-router-dom'
import { Provider } from 'react-redux'
import { store } from '../../domain/store'
import { render } from '@testing-library/react'
import Nav, { NavItem } from './Nav'

const darkMode = false
// eslint-disable-next-line @typescript-eslint/no-empty-function
const toggleDarkMode = () => {}

const scoutNavItemsTest: Array<NavItem> = [{ linkTitle: 'Test', public: false, link: '/test' }]

test('Nav render correctly', () => {
	const { getByTestId } = render(
		<Provider store={store}>
			<Router>
				<Nav navItems={scoutNavItemsTest} darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
			</Router>
		</Provider>
	)
	const container = getByTestId('NavMenu')
	expect(container?.firstChild?.textContent).toBe('Test')
})
