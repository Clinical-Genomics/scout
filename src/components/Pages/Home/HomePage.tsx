import React, { useEffect } from 'react'
import { makeStyles } from '@material-ui/core/styles'
import { connect } from 'react-redux'
import { RootState } from '../../../domain/rootReducer'
import packageJson from '../../../../package.json'
import { setDarkMode as setSettingsAction } from '../../../domain/settings/slice'

const mapDispatch = { setDarkMode: setSettingsAction } as const
const mapState = ({ settings }: RootState) => ({ settings } as const)
type Props = ReturnType<typeof mapState> & typeof mapDispatch

const useStyles = makeStyles({
  root: {
    minWidth: 275,
    width: '60vw',
    height: '45vh',
  },
  title: {
    fontSize: 45,
    fontWeight: 400,
  },
  h2: {
    fontSize: 25,
    fontWeight: 400,
  },
  divider: {
    marginBottom: 30,
    marginTop: 20,
  },
  body: {
    fontSize: 16,
  },
  version: {
    fontSize: 20,
    marginTop: 30,
    fontWeight: 400,
  },
})

function HomePage({ settings, setDarkMode }: Props) {
  const scoutVersion = packageJson.version
  // eslint-disable-next-line
  useEffect(() => {
    /** Check local storage */
    const darkModeStorage = localStorage.getItem('darkMode')
    if (darkModeStorage === 'true') {
      setDarkMode(true)
    } else if (darkModeStorage === 'false') {
      setDarkMode(false)
    }
  })
  const classes = useStyles()
  return <div className={'styles.containe'}>Hellou</div>
}

export const Home = connect(mapState, mapDispatch)(HomePage)
