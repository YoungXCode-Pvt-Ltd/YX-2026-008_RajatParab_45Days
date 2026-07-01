import { useEffect } from 'react'
import { useFunnelPageTracking } from '../hooks/useAnalytics'
import { trackFunnelStep } from '../services/analytics/funnel'

export default function Projects() {
  useFunnelPageTracking('project_creation')

  useEffect(() => {
    trackFunnelStep('project_creation', 'fill_project_details')
  }, [])

  return <div><h1>Projects</h1></div>
}
