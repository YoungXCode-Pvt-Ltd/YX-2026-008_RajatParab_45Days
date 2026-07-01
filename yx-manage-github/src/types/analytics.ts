export interface ProjectEventProperties {
  projectId: string
  projectName: string
  clientId?: string
  budget?: number
  priority?: 'low' | 'medium' | 'high' | 'critical'
}

export interface TaskEventProperties {
  taskId: string
  projectId?: string
  assigneeId?: string
  priority?: 'low' | 'medium' | 'high' | 'critical'
}

export interface ClientEventProperties {
  clientId: string
  city?: string
  industry?: string
}

export interface InvoiceEventProperties {
  invoiceId: string
  clientId?: string
  amount?: number
  status?: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled'
}

export interface ReportEventProperties {
  reportType?: string
  dateRange?: string
}

export interface MilestoneEventProperties {
  milestoneId: string
  projectId: string
  milestoneName?: string
}

export interface CommentEventProperties {
  commentId: string
  taskId: string
  projectId?: string
}

export interface PageViewProperties {
  page: string
  title?: string
  referrer?: string
  path: string
}

export interface UserProperties {
  userId: string
  email?: string
  name?: string
  role: UserRole
  company?: string
  plan?: string
}

export type UserRole = 'admin' | 'manager' | 'developer' | 'designer' | 'intern' | 'client'

export interface EventProperties {
  [key: string]: string | number | boolean | undefined | null
}

export type EventName =
  | 'project_created'
  | 'project_updated'
  | 'project_archived'
  | 'project_completed'
  | 'milestone_created'
  | 'task_created'
  | 'task_assigned'
  | 'task_completed'
  | 'task_status_changed'
  | 'task_commented'
  | 'client_added'
  | 'client_updated'
  | 'client_archived'
  | 'invoice_created'
  | 'invoice_sent'
  | 'invoice_paid'
  | 'invoice_overdue'
  | 'report_viewed'
  | 'report_exported'
  | 'dashboard_opened'
  | 'page_viewed'
  | 'user_logged_in'
  | 'user_logged_out'
  | 'user_registered'
  | 'funnel_step_completed'
  | 'funnel_completed'
  | 'funnel_abandoned'

export type FunnelName =
  | 'project_creation'
  | 'invoice_workflow'
  | 'task_workflow'
  | 'client_onboarding'
  | 'report_generation'

export interface FunnelStep {
  name: string
  order: number
}

export interface FunnelDefinition {
  name: FunnelName
  steps: FunnelStep[]
}

export interface FunnelEvent {
  funnelName: FunnelName
  stepName: string
  stepOrder: number
  userId: string
  sessionId: string
  properties?: EventProperties
  timestamp: number
}

export interface AnalyticsConfig {
  ga4: {
    measurementId: string
    enabled: boolean
  }
  mixpanel: {
    token: string
    enabled: boolean
  }
  hotjar: {
    hjid: number
    enabled: boolean
  }
  env: 'development' | 'staging' | 'production'
  version: string
  debug: boolean
}
