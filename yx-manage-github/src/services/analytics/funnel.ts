import { trackEvent, trackPage } from './events'
import { v4 } from './utils'
import type {
  FunnelName,
  FunnelDefinition,
  FunnelEvent,
  EventProperties,
  PageViewProperties
} from '../../types/analytics'

const FUNNEL_DEFINITIONS: FunnelDefinition[] = [
  {
    name: 'project_creation',
    steps: [
      { name: 'dashboard_page', order: 1 },
      { name: 'open_create_project', order: 2 },
      { name: 'fill_project_details', order: 3 },
      { name: 'assign_team', order: 4 },
      { name: 'project_created', order: 5 }
    ]
  },
  {
    name: 'invoice_workflow',
    steps: [
      { name: 'invoice_form_opened', order: 1 },
      { name: 'invoice_preview', order: 2 },
      { name: 'invoice_sent', order: 3 },
      { name: 'invoice_paid', order: 4 }
    ]
  },
  {
    name: 'task_workflow',
    steps: [
      { name: 'task_created', order: 1 },
      { name: 'task_assigned', order: 2 },
      { name: 'task_in_progress', order: 3 },
      { name: 'task_review', order: 4 },
      { name: 'task_completed', order: 5 }
    ]
  },
  {
    name: 'client_onboarding',
    steps: [
      { name: 'client_form_opened', order: 1 },
      { name: 'client_details_filled', order: 2 },
      { name: 'client_added', order: 3 }
    ]
  },
  {
    name: 'report_generation',
    steps: [
      { name: 'dashboard_opened', order: 1 },
      { name: 'report_viewed', order: 2 },
      { name: 'report_exported', order: 3 }
    ]
  }
]

const activeSessions = new Map<string, Set<string>>()

function getSessionId(): string {
  let sessionId = sessionStorage.getItem('yx_analytics_session_id')
  if (!sessionId) {
    sessionId = v4()
    sessionStorage.setItem('yx_analytics_session_id', sessionId)
  }
  return sessionId
}

function getUserId(): string {
  return localStorage.getItem('yx_user_id') || 'anonymous'
}

export function getFunnelDefinition(name: FunnelName): FunnelDefinition | undefined {
  return FUNNEL_DEFINITIONS.find(f => f.name === name)
}

export function getAllFunnels(): FunnelDefinition[] {
  return FUNNEL_DEFINITIONS
}

export function trackFunnelStep(
  funnelName: FunnelName,
  stepName: string,
  properties?: EventProperties
): void {
  const funnel = getFunnelDefinition(funnelName)
  if (!funnel) {
    console.error(`[Funnel] Unknown funnel: ${funnelName}`)
    return
  }

  const step = funnel.steps.find(s => s.name === stepName)
  if (!step) {
    console.error(`[Funnel] Unknown step "${stepName}" in funnel "${funnelName}"`)
    return
  }

  const sessionId = getSessionId()
  const userId = getUserId()

  if (!activeSessions.has(funnelName)) {
    activeSessions.set(funnelName, new Set())
  }
  const completedSteps = activeSessions.get(funnelName)!
  completedSteps.add(stepName)

  const funnelEvent: FunnelEvent = {
    funnelName,
    stepName,
    stepOrder: step.order,
    userId,
    sessionId,
    properties: {
      ...properties,
      step_order: step.order,
      total_steps: funnel.steps.length,
      progress_pct: Math.round((step.order / funnel.steps.length) * 100)
    },
    timestamp: Date.now()
  }

  trackEvent('funnel_step_completed', funnelEvent as unknown as EventProperties)

  if (import.meta.env.DEV) {
    console.log(`[Funnel] ${funnelName} -> ${stepName} (${step.order}/${funnel.steps.length})`)
  }

  if (step.order === funnel.steps.length) {
    trackEvent('funnel_completed', {
      funnel_name: funnelName,
      steps_completed: completedSteps.size,
      total_steps: funnel.steps.length,
      session_id: sessionId,
      user_id: userId
    })
    if (import.meta.env.DEV) console.log(`[Funnel] COMPLETED: ${funnelName}`)
  }
}

export function trackFunnelFlow(
  funnelName: FunnelName,
  pageViewProps: PageViewProperties
): void {
  trackPage(pageViewProps)
  const funnel = getFunnelDefinition(funnelName)
  if (!funnel) return

  const matchedStep = funnel.steps.find(s => {
    const path = pageViewProps.path.toLowerCase()
    const stepName = s.name.toLowerCase()
    return path.includes(stepName.replace(/_/g, '-')) || path.includes(stepName.replace(/_/g, '/'))
  })

  if (matchedStep) {
    trackFunnelStep(funnelName, matchedStep.name)
  }
}

export function abandonFunnel(funnelName: FunnelName, reason?: string): void {
  const funnel = getFunnelDefinition(funnelName)
  if (!funnel) return

  const completedSteps = activeSessions.get(funnelName)
  const stepsDone = completedSteps?.size || 0

  trackEvent('funnel_abandoned', {
    funnel_name: funnelName,
    steps_completed: stepsDone,
    total_steps: funnel.steps.length,
    drop_off_step: stepsDone + 1,
    reason: reason || 'unknown',
    session_id: getSessionId()
  })

  activeSessions.delete(funnelName)
  if (import.meta.env.DEV) console.log(`[Funnel] ABANDONED: ${funnelName} at step ${stepsDone + 1}`)
}

export function getFunnelCompletionRate(stepsCompleted: number, totalSteps: number): number {
  if (totalSteps === 0) return 0
  return Math.round((stepsCompleted / totalSteps) * 100)
}

export { FUNNEL_DEFINITIONS }
