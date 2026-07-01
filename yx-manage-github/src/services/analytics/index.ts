import type { AnalyticsConfig } from '../../types/analytics'

export function getAnalyticsConfig(): AnalyticsConfig {
  return {
    ga4: {
      measurementId: import.meta.env.VITE_GA_MEASUREMENT_ID || '',
      enabled: Boolean(import.meta.env.VITE_GA_MEASUREMENT_ID)
    },
    mixpanel: {
      token: import.meta.env.VITE_MIXPANEL_TOKEN || '',
      enabled: Boolean(import.meta.env.VITE_MIXPANEL_TOKEN)
    },
    hotjar: {
      hjid: Number(import.meta.env.VITE_HOTJAR_ID) || 0,
      enabled: Number(import.meta.env.VITE_HOTJAR_ID) > 0
    },
    env: (import.meta.env.VITE_APP_ENV as AnalyticsConfig['env']) || 'development',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    debug: import.meta.env.DEV
  }
}

export function isAnalyticsEnabled(): boolean {
  const config = getAnalyticsConfig()
  return config.ga4.enabled || config.mixpanel.enabled || config.hotjar.enabled
}

export function logAnalyticsError(context: string, error: unknown): void {
  if (import.meta.env.DEV) {
    console.error(`[Analytics Error] ${context}:`, error)
  }
}

export function validateEventPayload(
  eventName: string,
  properties: Record<string, unknown>
): boolean {
  if (!eventName || typeof eventName !== 'string') {
    console.error('[Analytics] Invalid event name:', eventName)
    return false
  }
  if (properties && typeof properties !== 'object') {
    console.error('[Analytics] Invalid properties for event:', eventName)
    return false
  }
  return true
}

export function getSessionMetadata(): Record<string, string | number> {
  return {
    session_id: sessionStorage.getItem('yx_analytics_session_id') || 'unknown',
    page_url: window.location.href,
    referrer: document.referrer || 'direct',
    screen_size: `${window.innerWidth}x${window.innerHeight}`,
    timestamp: new Date().toISOString(),
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    user_agent: navigator.userAgent.slice(0, 200)
  }
}
