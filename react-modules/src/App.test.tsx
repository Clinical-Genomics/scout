import React from 'react'
import { Provider } from 'react-redux'
import { store } from './domain/store'
import { render, fireEvent, screen } from '@testing-library/react'
import { App } from './App'

test('render with redux', () => {
	const { getByText } = render(
		<Provider store={store}>
			<App />
		</Provider>
	)
	getByText('Analyze VCFs quicker and easier')
})

test('darkMode', () => {
	const { getByTestId } = render(
		<Provider store={store}>
			<App />
		</Provider>
	)
	const container = getByTestId('darkMode')
	expect(container.firstChild?.firstChild).toHaveAttribute('data-testid', 'Dark')
	fireEvent.click(screen.getByTestId('darkMode'))
	expect(container.firstChild?.firstChild).toHaveAttribute('data-testid', 'Light')
})
