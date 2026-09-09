import React, { useState } from 'react'
import {
  Bell,
  Building2,
  ChevronRight,
  FileText,
  FolderKanban,
  LayoutDashboard,
  LogOut,
  Menu,
  ShieldCheck,
  UserCheck,
  X,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { LoginModal } from './LoginModal'

export type View = 'home' | 'documents' | 'parcels' | 'validation' | 'infrastructure'

const navigation = [
  { id: 'home', label: 'Overview', icon: LayoutDashboard, badge: null },
  { id: 'documents', label: 'Documents', icon: FileText, badge: 'Intake' },
  { id: 'parcels', label: 'Parcels', icon: FolderKanban, badge: 'Cadastre' },
  { id: 'validation', label: 'GIS Validation', icon: ShieldCheck, badge: 'Spatial' },
  { id: 'infrastructure', label: 'Infrastructure Risk', icon: Building2, badge: 'Corridors' },
] as const

export function Layout({
  view,
  onNavigate,
  children,
}: {
  view: View
  onNavigate: (view: View) => void
  children: React.ReactNode
}) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const { user, role, openLoginModal, logout, firebaseUser } = useAuth()

  const roleStyles = {
    operator: {
      badgeBg: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
      avatarBg: 'bg-emerald-600 text-white',
      accentGlow: 'glow-emerald',
    },
    tehsildar: {
      badgeBg: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      avatarBg: 'bg-amber-600 text-white',
      accentGlow: 'glow-amber',
    },
    director: {
      badgeBg: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
      avatarBg: 'bg-indigo-600 text-white',
      accentGlow: 'glow-indigo',
    },
  }[role]

  return (
    <div className="app-shell glass-canvas">
      {/* Subtle iOS ambient glass lighting */}
      <div className="ambient-orb orb-primary" />
      <div className="ambient-orb orb-secondary" />

      {/* Login Modal */}
      <LoginModal />

      {/* Glass Sidebar */}
      <aside className={`sidebar glass-sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
        {/* Brand Header */}
        <div className="brand">
          <div className="brand-mark-glass">भू</div>
          <div>
            <div className="flex items-center gap-1.5">
              <strong className="brand-title">BhuDhrishti</strong>
              <span className="platform-tag">2.0</span>
            </div>
            <span className="brand-sub">Dhara Lekha · SIH 2026</span>
          </div>
          <button
            className="icon-button mobile-close"
            onClick={() => setMobileOpen(false)}
            aria-label="Close navigation"
          >
            <X size={18} />
          </button>
        </div>

        {/* Current Role Card */}
        <div className="role-profile-pill" onClick={openLoginModal} title="Click to switch role">
          <div className={`role-avatar-circle ${roleStyles.avatarBg}`}>
            {user.avatar}
          </div>
          <div className="role-meta">
            <div className="role-name-row">
              <strong className="officer-name">{user.name}</strong>
              <span className={`role-tag ${roleStyles.badgeBg}`}>
                {user.badge}
              </span>
            </div>
            <span className="officer-jurisdiction">{user.jurisdiction}</span>
          </div>
          <UserCheck size={14} className="role-switch-icon" />
        </div>

        <div className="workspace-label">
          <span>OPERATIONAL SUITE</span>
          <span className="live-pulse" />
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          {navigation.map(({ id, label, icon: Icon, badge }) => {
            const isActive = view === id
            const isRoleFocus =
              (role === 'operator' && id === 'documents') ||
              (role === 'tehsildar' && (id === 'validation' || id === 'parcels')) ||
              (role === 'director' && (id === 'infrastructure' || id === 'home'))

            return (
              <button
                key={id}
                className={`nav-item glass-nav-item ${isActive ? 'active' : ''} ${
                  isRoleFocus ? 'role-focus' : ''
                }`}
                onClick={() => {
                  onNavigate(id as View)
                  setMobileOpen(false)
                }}
              >
                <div className="nav-icon-wrap">
                  <Icon size={18} />
                </div>
                <span className="nav-label">{label}</span>
                {badge && <span className="nav-badge-pill">{badge}</span>}
                {isActive && <ChevronRight size={15} className="nav-current" />}
              </button>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="sidebar-footer">
          <button className="support-link glass-action-btn" onClick={openLoginModal}>
            <UserCheck size={16} />
            <span>Switch Officer Role</span>
          </button>
          {firebaseUser && (
            <button className="support-link glass-action-btn text-rose-300" onClick={logout}>
              <LogOut size={16} />
              <span>Sign Out Firebase</span>
            </button>
          )}
        </div>
      </aside>

      {/* Mobile Scrim */}
      {mobileOpen && (
        <button
          className="scrim"
          onClick={() => setMobileOpen(false)}
          aria-label="Close navigation"
        />
      )}

      {/* Main Content Shell */}
      <main className="main-shell">
        {/* Topbar */}
        <header className="topbar glass-topbar">
          <button
            className="icon-button menu-trigger"
            onClick={() => setMobileOpen(true)}
            aria-label="Open navigation"
          >
            <Menu size={20} />
          </button>

          <div className="breadcrumbs">
            <span>Land Intelligence</span>
            <ChevronRight size={14} className="text-slate-500" />
            <strong className="text-slate-100">
              {navigation.find(item => item.id === view)?.label}
            </strong>
          </div>

          <div className="topbar-actions">
            {/* Live Cloud Status */}
            <div className="cloud-chip">
              <span className="status-dot animate-pulse" />
              <span>Firestore Active</span>
            </div>

            {/* Role Switcher Pill in Topbar */}
            <button
              className={`topbar-role-button ${roleStyles.badgeBg}`}
              onClick={openLoginModal}
            >
              <UserCheck size={13} />
              <span>{user.designation.split('/')[0].trim()}</span>
              <span className="switch-hint">Switch</span>
            </button>

            {/* Notifications */}
            <button className="icon-button glass-icon-btn" aria-label="Notifications">
              <Bell size={17} />
              <span className="notif-badge" />
            </button>

            {/* User Avatar */}
            <div
              className={`topbar-avatar ${roleStyles.avatarBg} cursor-pointer`}
              onClick={openLoginModal}
              title={`Logged in as ${user.name}`}
            >
              {user.avatar}
            </div>
          </div>
        </header>

        {/* Content Container */}
        <div className="page-content animate-fade-in">{children}</div>
      </main>
    </div>
  )
}
