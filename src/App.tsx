import React from 'react'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import { Layout } from './components/Layout/Layout'
import { Home } from './components/Pages/Home/HomePage'

import './App.scss'

function App() {
  return (
    <Router>
      <Layout>
        <Switch>
          <Route path="/about">About</Route>
          <Route path="/users">Users</Route>
          <Route path="/">
            <Home />
          </Route>
        </Switch>
      </Layout>
    </Router>
  )
}

export default App
