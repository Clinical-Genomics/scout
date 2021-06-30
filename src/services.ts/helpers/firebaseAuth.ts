import firebase from 'firebase/app'
import 'firebase/auth'
import { firebaseConfig } from './firebaseConfig'

const firebaseApp = firebase.initializeApp(firebaseConfig)

const auth = firebase.auth()
const provider = new firebase.auth.GoogleAuthProvider()

export { auth, provider }
