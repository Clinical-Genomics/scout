import firebase from 'firebase/app'
import 'firebase/auth'
import { firebaseConfig } from './firebaseConfig'

const firebaseApp = firebase.initializeApp(firebaseConfig)

const auth = firebase.auth()
const provider = new firebase.auth.GoogleAuthProvider()

export const signInWithGoogle = () => {
  auth
    .signInWithPopup(provider)
    .then((res) => {
      console.log(res.user)
    })
    .catch((error) => {
      console.log(error.message)
    })
}
