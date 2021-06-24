import React from 'react'
import { render } from '@testing-library/react'
import Dropdown from './DropdownMenu'

test('Dropdown render correctly', () => {
  const { getByTestId } = render(<Dropdown />)
  const DropdownMenu = getByTestId('DropdownMenu')
  expect(DropdownMenu).toBeInTheDocument()
})
