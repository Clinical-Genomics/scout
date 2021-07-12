import React from 'react'
import { Provider } from 'react-redux'
import { store } from '../../domain/store'
import packageJson from '../../../package.json'
import { render } from '@testing-library/react'
import { Home } from './HomePage'

test('Version number render correctly', () => {
  const { getByTestId } = render(
    <Provider store={store}>
      <Home />
    </Provider>
  )
  const container = getByTestId('version')
  const scoutVersion = packageJson.version
  expect(container.textContent).toBe(`Version: ${scoutVersion}`)
})
