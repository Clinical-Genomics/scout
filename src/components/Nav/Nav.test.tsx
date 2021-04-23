import React from 'react';
import { shallow } from 'enzyme';
import Nav from './Nav';

describe('<Nav />', () => {
  let component;

  beforeEach(() => {
    component = shallow(<Nav />);
  });

  test('It should mount', () => {
    expect(component.length).toBe(1);
  });
});
