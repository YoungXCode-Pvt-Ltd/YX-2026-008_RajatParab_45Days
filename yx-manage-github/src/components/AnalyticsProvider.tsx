import { useEffect, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { initGA4, trackPageView } from '../services/analytics/ga4'
import { initMixpanel } from '../services/analytics/mixpanel'
import { initHotjar } from '../services/analytics/hotjar'
import { usePageTracking } from '../hooks/useAnalytics'
import { getAnalyticsConfig } from '../services/analytics'

interface AnalyticsProviderProps {
  children: ReactNode
}

export function AnalyticsProvider({ children }: AnalyticsProviderProps) {
  const location = useLocation()
  const config = getAnalyticsConfig()

  useEffect(() => {
    if (config.ga4.enabled) initGA4()
    if (config.mixpanel.enabled) initMixpanel()
    if (config.hotjar.enabled) initHotjar()

    if (import.meta.env.DEV) {
      console.log('[Analytics] Provider initialized with config:', {
        ga4: config.ga4.enabled,
        mixpanel: config.mixpanel.enabled,
        hotjar: config.hotjar.enabled,
        env: config.env
      })
    }
  }, [])

  usePageTracking()

  return <>{children}</>
}
