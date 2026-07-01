import ReactGA from 'react-ga4'
import type { PageViewProperties, UserProperties } from '../../types/analytics'

const GA4_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID as string
const IS_ENABLED = import.meta.env.VITE_GA_MEASUREMENT_ID && import.meta.env.VITE_GA_MEASUREMENT_ID !== 'G-XXXXXXXXXX'

export function initGA4(): void {
  if (!IS_ENABLED) {
    if (import.meta.env.DEV) console.warn('[GA4] Measurement ID not configured. Skipping initialization.')
    return
  }
  ReactGA.initialize(GA4_MEASUREMENT_ID, {
    gaOptions: { siteSpeedSampleRate: 100 }
  })
  if (import.meta.env.DEV) console.log('[GA4] Initialized:', GA4_MEASUREMENT_ID)
}

export function trackPageView(props: PageViewProperties): void {
  if (!IS_ENABLED) return
  ReactGA.send({
    hitType: 'pageview',
    page: props.path,
    title: props.title || props.page,
    location: window.location.href
  })
  if (import.meta.env.DEV) console.log('[GA4] Page view:', props.path)
}

export function identifyUserGA4(user: UserProperties): void {
  if (!IS_ENABLED) return
  ReactGA.set({
    userId: user.userId,
    user_role: user.role,
    user_plan: user.plan || 'free'
  })
}

export function trackEventGA4(
  category: string,
  action: string,
  label?: string,
  value?: number
): void {
  if (!IS_ENABLED) return
  ReactGA.event({ category, action, label, value })
}

export function trackTimingGA4(
  category: string,
  variable: string,
  value: number,
  label?: string
): void {
  if (!IS_ENABLED) return
  ReactGA.send({
    hitType: 'timing',
    timingCategory: category,
    timingVar: variable,
    timingValue: value,
    timingLabel: label
  })
}

export function trackExceptionGA4(description: string, fatal: boolean = false): void {
  if (!IS_ENABLED) return
  ReactGA.send({
    hitType: 'exception',
    exDescription: description,
    exFatal: fatal
  })
}
