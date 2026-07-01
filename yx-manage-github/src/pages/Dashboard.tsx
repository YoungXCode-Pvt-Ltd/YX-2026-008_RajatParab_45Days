import { useEffect } from 'react'
import { useFunnelPageTracking } from '../hooks/useAnalytics'
import { trackFunnelStep } from '../services/analytics/funnel'
import { trackReportEvent } from '../services/analytics/events'

export default function Dashboard() {
  useFunnelPageTracking('project_creation')

  useEffect(() => {
    trackReportEvent('dashboard_opened', { reportType: 'dashboard' })

    const timer = setTimeout(() => {
      trackFunnelStep('project_creation', 'open_create_project')
    }, 5000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div>
      <h1>Dashboard</h1>
      <p>YX Manage - Analytics Tracking Active</p>
    </div>
  )
}
