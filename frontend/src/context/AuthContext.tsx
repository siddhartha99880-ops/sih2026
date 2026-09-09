import React, { createContext, useContext, useEffect, useState } from 'react'
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  type User as FirebaseUser,
} from 'firebase/auth'
import { auth } from '../services/firebase'

export type UserRole = 'operator' | 'tehsildar' | 'director'

export interface UserProfile {
  uid: string
  name: string
  email: string
  role: UserRole
  designation: string
  jurisdiction: string
  badge: string
  avatar: string
  color: string
}

export const PRESET_ROLES: Record<UserRole, UserProfile> = {
  operator: {
    uid: 'demo-operator-01',
    name: 'Ramesh Kulkarni',
    email: 'operator.blr@land.gov.in',
    role: 'operator',
    designation: 'Land Records Verification Operator',
    jurisdiction: 'Bengaluru North Division',
    badge: 'Operator Desk',
    avatar: 'RK',
    color: '#0d9488',
  },
  tehsildar: {
    uid: 'demo-tehsildar-01',
    name: 'Dr. Ananya Sharma',
    email: 'tehsildar.pune@revenue.gov.in',
    role: 'tehsildar',
    designation: 'Sub-Divisional Magistrate / Tehsildar',
    jurisdiction: 'Mulshi Sub-Division, Pune',
    badge: 'Revenue Magistrate',
    avatar: 'AS',
    color: '#d97706',
  },
  director: {
    uid: 'demo-director-01',
    name: 'Vikramaditya Roy, IAS',
    email: 'director.cadastre@gov.in',
    role: 'director',
    designation: 'Director of Land Records & Commissioner',
    jurisdiction: 'National Land Intelligence Board',
    badge: 'Commissioner',
    avatar: 'VR',
    color: '#4f46e5',
  },
}

interface AuthContextType {
  user: UserProfile
  firebaseUser: FirebaseUser | null
  role: UserRole
  setRole: (role: UserRole) => void
  loginDemoRole: (role: UserRole) => void
  loginWithEmail: (email: string, pass: string, role?: UserRole) => Promise<void>
  signupWithEmail: (email: string, pass: string, role?: UserRole) => Promise<void>
  logout: () => Promise<void>
  isLoginModalOpen: boolean
  openLoginModal: () => void
  closeLoginModal: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const LOCAL_ROLE_KEY = 'bhudhrishti_user_role'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [role, setRoleState] = useState<UserRole>(() => {
    try {
      const saved = localStorage.getItem(LOCAL_ROLE_KEY) as UserRole | null
      if (saved && PRESET_ROLES[saved]) return saved
    } catch {
      // ignore
    }
    return 'tehsildar'
  })

  const [user, setUser] = useState<UserProfile>(PRESET_ROLES[role])
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null)
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false)

  useEffect(() => {
    setUser(PRESET_ROLES[role])
    try {
      localStorage.setItem(LOCAL_ROLE_KEY, role)
    } catch {
      // ignore
    }
  }, [role])

  useEffect(() => {
    if (!auth) return
    const unsubscribe = onAuthStateChanged(auth, fbUser => {
      setFirebaseUser(fbUser)
      if (fbUser && fbUser.email) {
        setUser(prev => ({
          ...prev,
          uid: fbUser.uid,
          email: fbUser.email || prev.email,
          name: fbUser.displayName || prev.name,
        }))
      }
    })
    return () => unsubscribe()
  }, [])

  const loginDemoRole = (selectedRole: UserRole) => {
    setRoleState(selectedRole)
    setIsLoginModalOpen(false)
  }

  const setRole = (selectedRole: UserRole) => {
    setRoleState(selectedRole)
  }

  const loginWithEmail = async (email: string, pass: string, chosenRole: UserRole = 'operator') => {
    if (!auth) {
      setUser({
        ...PRESET_ROLES[chosenRole],
        email,
        name: email.split('@')[0].replace('.', ' ').toUpperCase(),
      })
      setRoleState(chosenRole)
      setIsLoginModalOpen(false)
      return
    }
    const cred = await signInWithEmailAndPassword(auth, email, pass)
    setFirebaseUser(cred.user)
    setRoleState(chosenRole)
    setIsLoginModalOpen(false)
  }

  const signupWithEmail = async (email: string, pass: string, chosenRole: UserRole = 'operator') => {
    if (!auth) {
      setUser({
        ...PRESET_ROLES[chosenRole],
        email,
        name: email.split('@')[0].replace('.', ' ').toUpperCase(),
      })
      setRoleState(chosenRole)
      setIsLoginModalOpen(false)
      return
    }
    const cred = await createUserWithEmailAndPassword(auth, email, pass)
    setFirebaseUser(cred.user)
    setRoleState(chosenRole)
    setIsLoginModalOpen(false)
  }

  const logout = async () => {
    if (auth) {
      try {
        await signOut(auth)
      } catch {
        // ignore
      }
    }
    setFirebaseUser(null)
    setRoleState('tehsildar')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        firebaseUser,
        role,
        setRole,
        loginDemoRole,
        loginWithEmail,
        signupWithEmail,
        logout,
        isLoginModalOpen,
        openLoginModal: () => setIsLoginModalOpen(true),
        closeLoginModal: () => setIsLoginModalOpen(false),
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
