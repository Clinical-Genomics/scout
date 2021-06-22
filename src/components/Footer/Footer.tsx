import React from 'react'
import styles from './Footer.module.scss'
import packageJson from '../../../package.json'

const Footer: React.FC = () => {
  const lowercaseText = packageJson.name.replaceAll('-', ' ')
  const capitalText = lowercaseText.replace(/\w\S*/g, (w) =>
    w.replace(/^\w/, (c) => c.toUpperCase())
  )
  const currentYear: number = new Date().getFullYear()

  return <footer className={styles.footer}>{`${capitalText} © ${currentYear}`}</footer>
}

export default Footer
