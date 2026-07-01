import { trackEvent } from './mixpanel'
import { trackPageView, identifyUserGA4, trackEventGA4 } from './ga4'
import { hotjarIdentify, hotjarSetAttributes } from './hotjar'
import type {
  EventName,
  EventProperties,
  PageViewProperties,
  UserProperties,
  ProjectEventProperties,
  TaskEventProperties,
  ClientEventProperties,
  InvoiceEventProperties,
  ReportEventProperties,
  MilestoneEventProperties,
  CommentEventProperties
} from '../../types/analytics'

export function identifyUser(user: UserProperties): void {
  identifyUserGA4(user)
  hotjarIdentify(user.userId, { role: user.role })
  hotjarSetAttributes({
    role: user.role,
    plan: user.plan || 'free',
    company: user.company || ''
  })
}

export function trackPage(page: PageViewProperties): void {
  trackEvent('page_viewed', {
    page: page.page,
    path: page.path,
    title: page.title || page.page,
    referrer: page.referrer || document.referrer
  })
  trackPageView(page)
}

export function trackProjectEvent(
  event: Extract<EventName,
    | 'project_created' | 'project_updated'
    | 'project_archived' | 'project_completed'
  >,
  properties: ProjectEventProperties
): void {
  trackEvent(event, properties as unknown as EventProperties)
  trackEventGA4('Project', event, properties.projectName)
}

export function trackTaskEvent(
  event: Extract<EventName,
    | 'task_created' | 'task_assigned'
    | 'task_completed' | 'task_status_changed'
  >,
  properties: TaskEventProperties
): void {
  trackEvent(event, properties as unknown as EventProperties)
  trackEventGA4('Task', event, properties.taskId)
}

export function trackClientEvent(
  event: Extract<EventName, 'client_added' | 'client_updated' | 'client_archived'>,
  properties: ClientEventProperties
): void {
  trackEvent(event, properties as unknown as EventProperties)
  trackEventGA4('Client', event, properties.clientId)
}

export function trackInvoiceEvent(
  event: Extract<EventName,
    | 'invoice_created' | 'invoice_sent'
    | 'invoice_paid' | 'invoice_overdue'
  >,
  properties: InvoiceEventProperties
): void {
  trackEvent(event, properties as unknown as EventProperties)
  trackEventGA4('Invoice', event, properties.invoiceId)
}

export function trackReportEvent(
  event: Extract<EventName, 'report_viewed' | 'report_exported' | 'dashboard_opened'>,
  properties: ReportEventProperties
): void {
  trackEvent(event, properties as unknown as EventProperties)
  trackEventGA4('Report', event, properties.reportType || '')
}

export function trackMilestoneEvent(properties: MilestoneEventProperties): void {
  trackEvent('milestone_created', properties as unknown as EventProperties)
  trackEventGA4('Milestone', 'milestone_created', properties.milestoneName)
}

export function trackCommentEvent(properties: CommentEventProperties): void {
  trackEvent('task_commented', properties as unknown as EventProperties)
  trackEventGA4('Task', 'task_commented', properties.taskId)
}

export { trackEvent, timeEvent, resetMixpanel, setSuperProperties } from './mixpanel'

export const MandatoryEvents: EventName[] = [
  'project_created',
  'invoice_sent',
  'task_completed',
  'client_added',
  'report_viewed'
]
