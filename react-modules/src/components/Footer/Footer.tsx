import React from 'react'
import styles from './Footer.module.css'
import packageJson from '../../../package.json'

const Footer: React.FC = () => {
	const lowercaseText = packageJson.name.replace('-', ' ')
	const capitalText = lowercaseText.replace(/\w\S*/g, (w) =>
		w.replace(/^\w/, (c) => c.toUpperCase())
	)
	const currentYear: number = new Date().getFullYear()

	return (
		<footer
			data-testid="footer"
			className={styles.footer}
		>{`${capitalText} © ${currentYear}`}</footer>
	)
}

export default Footer
