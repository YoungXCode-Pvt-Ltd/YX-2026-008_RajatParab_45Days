import mixpanel from 'mixpanel-browser'
import type { UserProperties, EventProperties, EventName } from '../../types/analytics'

const MIXPANEL_TOKEN = import.meta.env.VITE_MIXPANEL_TOKEN as string
const IS_ENABLED = import.meta.env.VITE_MIXPANEL_TOKEN && import.meta.env.VITE_MIXPANEL_TOKEN !== 'your_mixpanel_token_here'

export function initMixpanel(): void {
  if (!IS_ENABLED) {
    if (import.meta.env.DEV) console.warn('[Mixpanel] Token not configured. Skipping initialization.')
    return
  }
  mixpanel.init(MIXPANEL_TOKEN, {
    debug: import.meta.env.DEV,
    track_pageview: false,
    persistence: 'localStorage',
    ignore_dnt: false
  })
  if (import.meta.env.DEV) console.log('[Mixpanel] Initialized')
}

export function identifyMixpanel(user: UserProperties): void {
  if (!IS_ENABLED) return
  mixpanel.identify(user.userId)
  mixpanel.people.set({
    $email: user.email || '',
    $name: user.name || '',
    role: user.role,
    company: user.company || '',
    plan: user.plan || 'free',
    $created: new Date().toISOString()
  })
  if (import.meta.env.DEV) console.log('[Mixpanel] Identified user:', user.userId)
}

export function trackEvent(eventName: EventName, properties?: EventProperties): void {
  if (!IS_ENABLED) return
  const props = {
    ...properties,
    timestamp: new Date().toISOString(),
    app_version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    environment: import.meta.env.VITE_APP_ENV || 'development'
  }
  mixpanel.track(eventName, props)
  if (import.meta.env.DEV) console.log(`[Mixpanel] Tracked: ${eventName}`, props)
}

export function setSuperProperties(properties: EventProperties): void {
  if (!IS_ENABLED) return
  mixpanel.register(properties)
}

export function timeEvent(eventName: EventName): void {
  if (!IS_ENABLED) return
  mixpanel.time_event(eventName)
}

export function resetMixpanel(): void {
  if (!IS_ENABLED) return
  mixpanel.reset()
  if (import.meta.env.DEV) console.log('[Mixpanel] Reset')
}

export function getMixpanelDistinctId(): string | null {
  if (!IS_ENABLED) return null
  return mixpanel.get_distinct_id()
}
