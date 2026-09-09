import { useState } from 'react'
import { Bell, Building2, ChevronRight, CircleHelp, FileText, FolderKanban, LayoutDashboard, Menu, ShieldCheck, X } from 'lucide-react'

export type View = 'home' | 'documents' | 'parcels' | 'validation' | 'infrastructure'
const navigation = [
  { id: 'home', label: 'Overview', icon: LayoutDashboard }, { id: 'documents', label: 'Documents', icon: FileText }, { id: 'parcels', label: 'Parcels', icon: FolderKanban }, { id: 'validation', label: 'GIS Validation', icon: ShieldCheck }, { id: 'infrastructure', label: 'Infrastructure Risk', icon: Building2 },
] as const

export function Layout({ view, onNavigate, children }: { view: View; onNavigate: (view: View) => void; children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  return <div className="app-shell">
    <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
      <div className="brand"><div className="brand-mark">भू</div><div><strong>BhuDhrishti</strong><span>Dhara Lekha</span></div><button className="icon-button mobile-close" onClick={() => setMobileOpen(false)} aria-label="Close navigation"><X size={18} /></button></div>
      <div className="workspace-label">LAND INTELLIGENCE PLATFORM</div>
      <nav>{navigation.map(({ id, label, icon: Icon }) => <button key={id} className={`nav-item ${view === id ? 'active' : ''}`} onClick={() => { onNavigate(id); setMobileOpen(false) }}><Icon size={18} /><span>{label}</span>{view === id && <ChevronRight size={15} className="nav-current" />}</button>)}</nav>
      <div className="sidebar-footer"><div className="operator-card"><div className="avatar">OP</div><div><strong>Verification desk</strong><span>Operator workspace</span></div></div><button className="support-link"><CircleHelp size={16} /> Support &amp; guidance</button></div>
    </aside>
    {mobileOpen && <button className="scrim" onClick={() => setMobileOpen(false)} aria-label="Close navigation" />}
    <main className="main-shell"><header className="topbar"><button className="icon-button menu-trigger" onClick={() => setMobileOpen(true)} aria-label="Open navigation"><Menu size={20} /></button><div className="breadcrumbs"><span>Land Intelligence</span><ChevronRight size={14} /><strong>{navigation.find(item => item.id === view)?.label}</strong></div><div className="topbar-actions"><span className="environment-chip"><span className="status-dot" /> Local API</span><button className="icon-button" aria-label="Notifications"><Bell size={18} /></button><div className="topbar-avatar">A</div></div></header><div className="page-content">{children}</div></main>
  </div>
}