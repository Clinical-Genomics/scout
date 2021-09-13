import React from 'react'
import { render } from '@testing-library/react'
import DropdownMenu from './DropdownMenu'

const scoutNavItemsTest = [{ linkTitle: 'Test', public: false, link: '/test' }]

test('Dropdown render correctly', () => {
  const { getByTestId } = render(
    <DropdownMenu>
      <li>Test</li>
      <li>Test 2</li>
    </DropdownMenu>
  )
  const container = getByTestId('DropdownMenu')
  expect(container.firstChild?.textContent).toBe('Test')
})
