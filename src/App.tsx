import React, { useEffect } from 'react'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import { connect } from 'react-redux';
import { RootState } from './domain/rootReducer';
import Layout from './components/Layout/Layout'
import HomePage from './components/Pages/Home/HomePage'
import { setDarkMode as setSettingsAction } from './domain/settings/slice';
import './App.scss'

const mapDispatch = { setDarkMode: setSettingsAction } as const;
const mapState = ({ settings }: RootState) => ({ settings } as const);
type Props = ReturnType<typeof mapState> & typeof mapDispatch;

function AppComponent({ settings, setDarkMode }: Props) {

  useEffect(() => {
    /** Check local storage */
    const darkModeStorage = localStorage.getItem('darkMode')
    if (darkModeStorage !== undefined) {
      setDarkMode(true)
      return
    }

    // Check OS dark/light mode
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      // Dark
      setDarkMode(true)
    }
  })


  return (
    <Router>
      <Layout>
        <Switch>
          <Route path="/about">About</Route>
          <Route path="/users">Users</Route>
          <Route path="/">
            <HomePage />
          </Route>
        </Switch>
      </Layout>
    </Router>
  )
}

export const App = connect(mapState, mapDispatch)(AppComponent);
