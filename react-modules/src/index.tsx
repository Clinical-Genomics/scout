import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import { Provider } from 'react-redux'
import { App } from './App'
import { store } from './domain/store'
import { makeServer } from './server'

if (process.env.MOCK === 'true') {
	makeServer()
}

ReactDOM.render(
	<React.StrictMode>
		<Provider store={store}>
			<App />
		</Provider>
	</React.StrictMode>,
	document.getElementById('app')
)
