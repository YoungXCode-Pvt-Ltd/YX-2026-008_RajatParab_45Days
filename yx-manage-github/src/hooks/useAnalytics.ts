import { useEffect, useCallback, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { trackPage } from '../services/analytics/events'
import { trackFunnelFlow } from '../services/analytics/funnel'
import { trackEvent } from '../services/analytics/mixpanel'
import { trackTimingGA4 } from '../services/analytics/ga4'
import type { FunnelName, PageViewProperties, EventName, EventProperties } from '../types/analytics'

export function usePageTracking(): void {
  const location = useLocation()

  useEffect(() => {
    const props: PageViewProperties = {
      page: document.title || location.pathname.split('/')[1] || 'dashboard',
      path: location.pathname,
      title: document.title,
      referrer: document.referrer
    }
    trackPage(props)
  }, [location])
}

export function useFunnelPageTracking(funnelName: FunnelName): void {
  const location = useLocation()

  useEffect(() => {
    const props: PageViewProperties = {
      page: document.title || location.pathname.split('/')[1] || 'dashboard',
      path: location.pathname,
      title: document.title
    }
    trackFunnelFlow(funnelName, props)
  }, [location, funnelName])
}

export function useTrackEvent(eventName: EventName) {
  return useCallback(
    (properties?: EventProperties) => {
      trackEvent(eventName, properties)
    },
    [eventName]
  )
}

export function useTrackTiming() {
  const timers = useRef<Map<string, number>>(new Map())

  const startTimer = useCallback((name: string) => {
    timers.current.set(name, Date.now())
  }, [])

  const endTimer = useCallback(
    (name: string, category?: string) => {
      const start = timers.current.get(name)
      if (!start) return 0
      const duration = Date.now() - start
      trackTimingGA4(category || 'user_action', name, duration)
      timers.current.delete(name)
      return duration
    },
    []
  )

  return { startTimer, endTimer }
}

export function useAnalytics() {
  return {
    trackPage: useCallback((props: PageViewProperties) => trackPage(props), []),
    trackEvent: useCallback(
      (name: EventName, props?: EventProperties) => {
        trackEvent(name, props)
      },
      []
    )
  }
}
