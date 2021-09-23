import React, { useEffect } from 'react'
import logo_scout from 'assets/logo_scout.png'
import { connect } from 'react-redux'
import { RootState } from 'domain/rootReducer'
import styles from './Layout.module.css'
import { setDarkMode as setSettingsAction } from 'domain/settings/slice'
import Nav, { NavItem } from 'components/Nav/Nav'
import Footer from 'components/Footer/Footer'

const mapDispatch = { setDarkMode: setSettingsAction } as const
const mapState = ({ settings }: RootState) => ({ settings } as const)

const headerScout = {
  icon: logo_scout,
  title: 'Scout',
}

function LayoutComponent({ children, settings, setDarkMode }: any) {
  /* Scout Navigation items */
  const scoutNavItems: Array<NavItem> = [
    { linkTitle: 'Home', public: false, link: '/' },
    { linkTitle: 'Cases', public: false, link: `/${settings.currentInstitute}/cases` },
    { linkTitle: 'Phenotypes', public: false, link: `/${settings.currentInstitute}/phenotypes` },
    {
      linkTitle: 'User guide',
      public: true,
      externalLink: 'https://clinical-genomics.github.io/scout/',
    },
    {
      linkTitle: 'Open issues',
      public: true,
      externalLink: 'https://github.com/Clinical-Genomics/scout/issues',
    },
  ]

  useEffect(() => {
    /** Check local storage */
    const darkModeStorage = localStorage.getItem('darkMode')
    if (darkModeStorage !== undefined) {
      setDarkMode(darkModeStorage === 'true')
      return
    }

    // Check OS dark/light mode
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      // Dark
      setDarkMode(true)
    }
  }, [setDarkMode])

  // TODO: Check if there is a better way to solve the asynchronous problem
  const toggleDarkMode = () => {
    const newMode = !settings.darkMode
    setDarkMode(newMode)
    localStorage.setItem('darkMode', newMode.toString())
  }

  return (
    <div>
      {settings?.darkMode && (
        <link
          rel="stylesheet"
          type="text/css"
          href={'https://cdnjs.cloudflare.com/ajax/libs/antd/4.4.3/antd.dark.css'}
        />
      )}
      <div className={`${styles.Layout} ${settings.darkMode ? 'dark_mode' : ''}`}>
        <header>
          <Nav
            header={headerScout}
            navItems={scoutNavItems}
            darkMode={settings.darkMode}
            toggleDarkMode={toggleDarkMode}
          />
        </header>
        <main>{children}</main>
        <Footer />
      </div>
    </div>
  )
}

export const Layout = connect(mapState, mapDispatch)(LayoutComponent)
