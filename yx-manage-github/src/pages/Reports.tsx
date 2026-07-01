import { useEffect } from 'react'
import { useFunnelPageTracking } from '../hooks/useAnalytics'

export default function Reports() {
  useFunnelPageTracking('report_generation')

  useEffect(() => {
    document.title = 'Reports | YX Manage'
  }, [])

  return <div><h1>Reports</h1></div>
}
