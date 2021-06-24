import React from 'react'
import { render, fireEvent } from '@testing-library/react'

import App from './App'

test('App render correctly', () => {
  const { getByText } = render(<App />)
  getByText('Analyze VCFs quicker and easier')
})
