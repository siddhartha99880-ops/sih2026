import { initializeApp, getApps } from 'firebase/app'
import { getAuth } from 'firebase/auth'

const firebaseConfig = {
  projectId: 'h2026-b64c0',
  authDomain: 'h2026-b64c0.firebaseapp.com',
  storageBucket: 'h2026-b64c0.firebasestorage.app',
}

export const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0]
export const auth = getAuth(app)
