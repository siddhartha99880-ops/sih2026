import { initializeApp, getApps, type FirebaseApp } from 'firebase/app'
import { getAuth, type Auth } from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || '',
  projectId: 'h2026-b64c0',
  authDomain: 'h2026-b64c0.firebaseapp.com',
  storageBucket: 'h2026-b64c0.firebasestorage.app',
}

let appInstance: FirebaseApp | null = null
let authInstance: Auth | null = null

try {
  if (firebaseConfig.apiKey) {
    appInstance = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0]
    authInstance = getAuth(appInstance)
  }
} catch (err) {
  console.warn('Firebase client initialization deferred:', err)
}

export const app = appInstance
export const auth = authInstance
