const HOTJAR_ID = Number(import.meta.env.VITE_HOTJAR_ID) || 0
const IS_ENABLED = HOTJAR_ID > 0

interface HotjarConfig {
  hjid: number
  hjsv: number
}

declare global {
  interface Window {
    hj: (...args: unknown[]) => void
    _hjSettings?: HotjarConfig
  }
}

export function initHotjar(): void {
  if (!IS_ENABLED) {
    if (import.meta.env.DEV) console.warn('[Hotjar] ID not configured. Skipping initialization.')
    return
  }

  window._hjSettings = { hjid: HOTJAR_ID, hjsv: 6 }

  const script = document.createElement('script')
  script.async = true
  script.src = `https://static.hotjar.com/c/hotjar-${HOTJAR_ID}.js?sv=6`
  script.onload = () => {
    if (import.meta.env.DEV) console.log('[Hotjar] Initialized:', HOTJAR_ID)
  }
  document.head.appendChild(script)
}

export function hotjarIdentify(
  userId: string,
  properties?: Record<string, string | number | boolean>
): void {
  if (!IS_ENABLED || !window.hj) return
  window.hj('identify', userId, properties)
}

export function hotjarEvent(eventName: string, metadata?: Record<string, unknown>): void {
  if (!IS_ENABLED || !window.hj) return
  window.hj('event', eventName, metadata)
}

export function hotjarSetAttributes(
  attributes: Record<string, string | number | boolean>
): void {
  if (!IS_ENABLED || !window.hj) return
  window.hj('set', 'attributes', attributes)
}

export function hotjarTriggerFunnel(
  funnelId: number,
  step: number,
  options?: Record<string, unknown>
): void {
  if (!IS_ENABLED || !window.hj) return
  window.hj('trigger', 'funnel', { id: funnelId, step, ...options })
}
