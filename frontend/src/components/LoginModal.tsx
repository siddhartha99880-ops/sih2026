import React, { useState } from 'react'
import {
  Building2,
  CheckCircle2,
  FileCheck2,
  Flame,
  Lock,
  Mail,
  ShieldCheck,
  UserCheck,
  X,
} from 'lucide-react'
import { PRESET_ROLES, useAuth, type UserRole } from '../context/AuthContext'

export function LoginModal() {
  const { isLoginModalOpen, closeLoginModal, loginDemoRole, loginWithEmail, signupWithEmail, role: currentRole } = useAuth()
  const [activeTab, setActiveTab] = useState<'quick' | 'firebase'>('quick')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [selectedRole, setSelectedRole] = useState<UserRole>('operator')
  const [isSignUp, setIsSignUp] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (!isLoginModalOpen) return null

  const handleFirebaseSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Please fill in both email and password.')
      return
    }
    setError('')
    setLoading(true)
    try {
      if (isSignUp) {
        await signupWithEmail(email, password, selectedRole)
      } else {
        await loginWithEmail(email, password, selectedRole)
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Authentication failed.'
      setError(message.replace('Firebase: ', ''))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="glass-modal-backdrop" onClick={closeLoginModal}>
      <div className="glass-modal" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="glass-modal-header">
          <div className="flex items-center gap-3">
            <div className="brand-mark-glass">भू</div>
            <div>
              <div className="eyebrow flex items-center gap-1.5 text-blue-400">
                <ShieldCheck size={14} />
                <span>Authoritative Cadastre Portal</span>
              </div>
              <h2 className="modal-title">Select Operational Role</h2>
            </div>
          </div>
          <button className="modal-close-btn" onClick={closeLoginModal} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        {/* Tab switcher */}
        <div className="modal-tabs">
          <button
            className={`modal-tab ${activeTab === 'quick' ? 'active' : ''}`}
            onClick={() => setActiveTab('quick')}
          >
            <UserCheck size={16} />
            <span>Official Roles (1-Click)</span>
          </button>
          <button
            className={`modal-tab ${activeTab === 'firebase' ? 'active' : ''}`}
            onClick={() => setActiveTab('firebase')}
          >
            <Flame size={16} className="text-amber-500" />
            <span>Firebase Auth Email</span>
          </button>
        </div>

        {activeTab === 'quick' ? (
          <div className="role-grid">
            {/* Operator Card */}
            <div
              className={`role-card ${currentRole === 'operator' ? 'current-active' : ''}`}
              onClick={() => loginDemoRole('operator')}
            >
              <div className="role-icon-box">
                <FileCheck2 size={22} />
              </div>
              <div className="role-content">
                <div className="role-badge-pill">
                  Intake Desk
                </div>
                <h3>{PRESET_ROLES.operator.name}</h3>
                <span className="role-desig">{PRESET_ROLES.operator.designation}</span>
                <p className="role-desc">
                  Document intake, deed uploads, OCR quality control, and khasra-parcel association.
                </p>
              </div>
              <button className="role-login-btn">
                Select &rarr;
              </button>
            </div>

            {/* Tehsildar Card */}
            <div
              className={`role-card ${currentRole === 'tehsildar' ? 'current-active' : ''}`}
              onClick={() => loginDemoRole('tehsildar')}
            >
              <div className="role-icon-box">
                <ShieldCheck size={22} />
              </div>
              <div className="role-content">
                <div className="role-badge-pill">
                  Revenue Magistrate
                </div>
                <h3>{PRESET_ROLES.tehsildar.name}</h3>
                <span className="role-desig">{PRESET_ROLES.tehsildar.designation}</span>
                <p className="role-desc">
                  Authoritative cadastral register, deterministic GIS validation, area verification & boundary overlap adjudication.
                </p>
              </div>
              <button className="role-login-btn">
                Select &rarr;
              </button>
            </div>

            {/* Director Card */}
            <div
              className={`role-card ${currentRole === 'director' ? 'current-active' : ''}`}
              onClick={() => loginDemoRole('director')}
            >
              <div className="role-icon-box">
                <Building2 size={22} />
              </div>
              <div className="role-content">
                <div className="role-badge-pill">
                  Commissioner
                </div>
                <h3>{PRESET_ROLES.director.name}</h3>
                <span className="role-desig">{PRESET_ROLES.director.designation}</span>
                <p className="role-desc">
                  Executive infrastructure risk oversight, corridor acquisition alerts, high-level project register & audit hash logs.
                </p>
              </div>
              <button className="role-login-btn">
                Select &rarr;
              </button>
            </div>
          </div>
        ) : (
          <form className="firebase-auth-form" onSubmit={handleFirebaseSubmit}>
            {error && (
              <div className="auth-error-banner">
                <span>{error}</span>
              </div>
            )}

            <div className="auth-field">
              <label>Official Email Address</label>
              <div className="auth-input-wrap">
                <Mail size={16} className="auth-input-icon" />
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="name@revenue.gov.in"
                  required
                />
              </div>
            </div>

            <div className="auth-field">
              <label>Security Password</label>
              <div className="auth-input-wrap">
                <Lock size={16} className="auth-input-icon" />
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                />
              </div>
            </div>

            <div className="auth-field">
              <label>Assign Officer Role</label>
              <select
                value={selectedRole}
                onChange={e => setSelectedRole(e.target.value as UserRole)}
                className="auth-select"
              >
                <option value="operator">Operator (Document Intake & OCR)</option>
                <option value="tehsildar">Tehsildar (GIS Cadastral Verification)</option>
                <option value="director">Director (Infrastructure & Corridor Risk)</option>
              </select>
            </div>

            <button type="submit" className="auth-submit-btn" disabled={loading}>
              {loading ? 'Authenticating…' : isSignUp ? 'Create Officer Account' : 'Authenticate with Firebase'}
            </button>

            <div className="auth-toggle-mode">
              <span>{isSignUp ? 'Already registered?' : 'Need to register a new officer?'}</span>
              <button
                type="button"
                className="toggle-link"
                onClick={() => {
                  setIsSignUp(!isSignUp)
                  setError('')
                }}
              >
                {isSignUp ? 'Sign In' : 'Register New Account'}
              </button>
            </div>
          </form>
        )}

        <div className="modal-footer-note">
          <CheckCircle2 size={14} className="text-emerald-400" />
          <span>Connected to Google Cloud / Firebase project <strong>h2026-b64c0</strong></span>
        </div>
      </div>
    </div>
  )
}
