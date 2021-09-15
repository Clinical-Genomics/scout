import React from 'react'
import styles from './DropdownMenu.module.css'

const DropdownMenu: React.FC = ({ children }) => (
	<ul data-testid="DropdownMenu" className={`${styles.DropdownMenu} dropdown_menu`}>
		{children}
	</ul>
)
export default DropdownMenu
