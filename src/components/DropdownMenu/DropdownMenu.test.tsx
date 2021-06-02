import React from 'react'
import { shallow } from 'enzyme'
import DropdownMenu from './DropdownMenu'

describe('<DropdownMenu />', () => {
  let component

  beforeEach(() => {
    component = shallow(<DropdownMenu />)
  })

  test('It should mount', () => {
    expect(component.length).toBe(1)
  })
})
