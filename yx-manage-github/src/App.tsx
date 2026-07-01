import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AnalyticsProvider } from './components/AnalyticsProvider'
import Dashboard from './pages/Dashboard'
import Clients from './pages/Clients'
import Projects from './pages/Projects'
import ProjectDetails from './pages/ProjectDetails'
import Tasks from './pages/Tasks'
import Invoices from './pages/Invoices'
import Reports from './pages/Reports'
import Team from './pages/Team'
import Settings from './pages/Settings'
import ClientPortal from './pages/ClientPortal'

export default function App() {
  return (
    <BrowserRouter>
      <AnalyticsProvider>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/clients" element={<Clients />} />
          <Route path="/clients/:id" element={<ClientPortal />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:id" element={<ProjectDetails />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/invoices" element={<Invoices />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/team" element={<Team />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </AnalyticsProvider>
    </BrowserRouter>
  )
}
