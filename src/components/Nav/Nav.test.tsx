import React from 'react'
import { shallow } from 'enzyme'
import Nav, { NavItem } from './Nav'

describe('<Nav />', () => {
  let component
  const cgNavItems: Array<NavItem> = [
    { linkTitle: 'Beställninger', public: true, link: '/orders' },
    { linkTitle: 'Provkrav', public: true, link: '/requirements' },
    { linkTitle: 'Applikationer', public: true, link: '/applications' },
    { linkTitle: 'Dataleverans', public: true, link: '/delivery' },
    {
      linkTitle: 'Support',
      public: true,
      dropdownList: [
        { linkTitle: 'FAQ', public: true, link: '/faq' },
        { linkTitle: 'Kontakt', public: true, link: '/contact' },
        { linkTitle: 'Feedback', public: false, link: '/feedback' },
        { linkTitle: 'Help', public: false, link: '/help' },
      ],
    },
    { linkTitle: 'New order', public: false, link: '/new-order' },
    { linkTitle: 'Status', public: false, link: '/status' },
    { linkTitle: 'Items', public: false, link: '/items' },
  ]

  beforeEach(() => {
    component = shallow(<Nav navItems={cgNavItems} />)
  })

  test('It should mount', () => {
    expect(component.length).toBe(1)
  })
})
