import React from 'react'

const DropdownMenu: React.FC = ({ children }) => (
  <ul data-testid="DropdownMenu" className={`dropdown_menu`}>
    {children}
  </ul>
)
export default DropdownMenu
