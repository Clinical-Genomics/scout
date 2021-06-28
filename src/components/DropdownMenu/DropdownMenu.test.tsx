import React from 'react'
import { render } from '@testing-library/react'
import Dropdown from './DropdownMenu'

test('Dropdown render correctly', () => {
  const { getByTestId } = render(<Dropdown />)
  const container = getByTestId('DropdownMenu')
  expect(container).toBeInTheDocument()
})
