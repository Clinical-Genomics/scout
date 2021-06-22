/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { useEffect } from 'react'
import { ThemeProvider, createMuiTheme } from '@material-ui/core/styles'
import Nav, { NavItem } from 'components/Nav/Nav'
import logo_scout from 'assets/logo_scout.png'
import Footer from 'components/Footer/Footer'
import { Paper } from '@material-ui/core'
import { connect } from 'react-redux';
import { RootState } from '../../domain/rootReducer';
import styles from './Layout.module.scss'
import { setDarkMode as setSettingsAction } from '../../domain/settings/slice';

const mapDispatch = { setDarkMode: setSettingsAction } as const;
const mapState = ({ settings }: RootState) => ({ settings } as const);

const headerScout = {
  icon: logo_scout,
  title: 'Scout',
}

/* Scout Navigation items */
const scoutNavItems: Array<NavItem> = [
  { linkTitle: 'Home', public: false, link: '/home' },
  { linkTitle: 'Genes', public: false, link: '/genes' },
  { linkTitle: 'Gene Panels', public: false, link: '/gene-panels' },
  { linkTitle: 'Phenotype', public: false, link: '/phenotype' },
  { linkTitle: 'Diagnoses', public: false, link: '/diagnoses' },
  { linkTitle: 'Manages variants', public: false, link: '/manages-variants' },
  { linkTitle: 'Users', public: false, link: '/users' },
  { linkTitle: 'Institutes', public: false, link: '/institutes' },
  { linkTitle: 'Dashboard', public: false, link: '/dashboard' },
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

function LayoutComponent({ children, settings, setDarkMode }: any) {

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
  const theme = createMuiTheme({
    palette: {
      type: settings.darkMode ? 'dark' : 'light',
    },
  })
  return (
    <ThemeProvider theme={theme}>
      <Paper>
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
      </Paper>
    </ThemeProvider>
  )
}

export const Layout = connect(mapState, mapDispatch)(LayoutComponent);
