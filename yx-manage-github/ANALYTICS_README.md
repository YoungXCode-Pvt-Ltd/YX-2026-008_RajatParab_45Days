# YX Manage Analytics Integration Guide

## Overview

This document provides a comprehensive guide to the analytics tracking system implemented for YX Manage. The system integrates three analytics platforms (GA4, Mixpanel, Hotjar) with custom event tracking, funnel analysis, and user segmentation capabilities.

## Architecture

```
src/
└── services/
    └── analytics/
        ├── index.ts      # Analytics config, init orchestration, utilities
        ├── ga4.ts         # Google Analytics 4 integration
        ├── mixpanel.ts    # Mixpanel event tracking
        ├── hotjar.ts      # Hotjar heatmaps & session recordings
        ├── events.ts      # Unified event tracking layer
        ├── funnel.ts      # Funnel analysis system
        └── utils.ts       # Helper utilities
```

## Quick Start

### 1. Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```env
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX     # GA4 Measurement ID (Web stream)
VITE_MIXPANEL_TOKEN=your_token_here     # Mixpanel project token
VITE_HOTJAR_ID=123456                    # Hotjar site ID
VITE_APP_ENV=development                 # development | staging | production
VITE_APP_VERSION=1.0.0                   # Current app version
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Wrap App with AnalyticsProvider

```tsx
// src/main.tsx or src/App.tsx
import { BrowserRouter } from 'react-router-dom'
import { AnalyticsProvider } from './components/AnalyticsProvider'

function App() {
  return (
    <BrowserRouter>
      <AnalyticsProvider>
        <YourRoutes />
      </AnalyticsProvider>
    </BrowserRouter>
  )
}
```

The `AnalyticsProvider` automatically:
- Initializes GA4, Mixpanel, and Hotjar
- Tracks all page views via React Router location changes
- Attaches session metadata to all events

---

## Event Tracking

### Mandatory Business Events (Must Implement Before Production)

These events are required for core business metrics:

```typescript
import { trackProjectEvent, trackInvoiceEvent, trackTaskEvent, trackClientEvent, trackReportEvent } from '../services/analytics/events'

// 1. Project Created
trackProjectEvent('project_created', {
  projectId: 'proj_123',
  projectName: 'New Website',
  clientId: 'client_456',
  budget: 500000,
  priority: 'high'
})

// 2. Invoice Sent
trackInvoiceEvent('invoice_sent', {
  invoiceId: 'inv_789',
  clientId: 'client_456',
  amount: 150000,
  status: 'sent'
})

// 3. Task Completed
trackTaskEvent('task_completed', {
  taskId: 'task_101',
  projectId: 'proj_123',
  assigneeId: 'user_789',
  priority: 'medium'
})

// 4. Client Added
trackClientEvent('client_added', {
  clientId: 'client_456',
  city: 'Mumbai',
  industry: 'FinTech'
})

// 5. Report Viewed
trackReportEvent('report_viewed', {
  reportType: 'revenue',
  dateRange: 'last_30_days'
})
```

### Complete Event Reference

#### Project Events
| Event | Properties | Trigger |
|-------|-----------|---------|
| `project_created` | projectId, projectName, clientId, budget, priority | Create project form submit |
| `project_updated` | projectId, projectName, clientId, budget, priority | Project settings save |
| `project_archived` | projectId, projectName | Archive action confirm |
| `project_completed` | projectId, projectName | Mark complete action |
| `milestone_created` | milestoneId, projectId, milestoneName | Add milestone |

#### Task Events
| Event | Properties | Trigger |
|-------|-----------|---------|
| `task_created` | taskId, projectId, assigneeId, priority | Create task form submit |
| `task_assigned` | taskId, projectId, assigneeId, priority | Assignee change |
| `task_completed` | taskId, projectId, assigneeId, priority | Mark complete |
| `task_status_changed` | taskId, projectId, assigneeId, priority | Status dropdown change |

#### Client Events
| Event | Properties | Trigger |
|-------|-----------|---------|
| `client_added` | clientId, city, industry | Add client form submit |
| `client_updated` | clientId, city, industry | Client info save |
| `client_archived` | clientId | Archive confirm |

#### Invoice Events
| Event | Properties | Trigger |
|-------|-----------|---------|
| `invoice_created` | invoiceId, clientId, amount, status | Draft saved |
| `invoice_sent` | invoiceId, clientId, amount, status | Send button click |
| `invoice_paid` | invoiceId, clientId, amount, status | Payment received |
| `invoice_overdue` | invoiceId, clientId, amount, status | Past due date |

#### Report Events
| Event | Properties | Trigger |
|-------|-----------|---------|
| `report_viewed` | reportType, dateRange | Report page load |
| `report_exported` | reportType, dateRange | Export button click |
| `dashboard_opened` | reportType: 'dashboard' | Dashboard page load |

---

## Page View Tracking

Page views are **automatically tracked** by `AnalyticsProvider` via `usePageTracking()` hook. No manual instrumentation needed.

Pages tracked:
- `/` - Dashboard
- `/clients` - Clients List
- `/clients/:id` - Client Portal
- `/projects` - Projects List
- `/projects/:id` - Project Details
- `/tasks` - Tasks
- `/invoices` - Invoices
- `/reports` - Reports
- `/team` - Team
- `/settings` - Settings

### Manual Page Tracking

```typescript
import { trackPage } from '../services/analytics/events'

trackPage({
  page: 'Custom Page',
  path: '/custom-path',
  title: 'Custom Page Title'
})
```

---

## User Identification

Call `identifyUser()` after login/signup to associate events with known users:

```typescript
import { identifyUser } from '../services/analytics/events'

identifyUser({
  userId: 'user_789',
  email: 'user@example.com',
  name: 'John Doe',
  role: 'manager',           // 'admin' | 'manager' | 'developer' | 'designer' | 'intern' | 'client'
  company: 'Acme Corp',
  plan: 'enterprise'
})
```

---

## Funnel Tracking

### Available Funnels

| Funnel Name | Steps | Tracked In |
|------------|-------|-----------|
| `project_creation` | Dashboard → Open Create → Fill Details → Assign Team → Created | Dashboard, Projects |
| `invoice_workflow` | Form → Preview → Sent → Paid | Invoices |
| `task_workflow` | Created → Assigned → In Progress → Review → Completed | Tasks |
| `client_onboarding` | Form Opened → Details Filled → Added | Clients |
| `report_generation` | Dashboard → Report Viewed → Exported | Dashboard, Reports |

### Manual Step Tracking

```typescript
import { trackFunnelStep, abandonFunnel } from '../services/analytics/funnel'

// Track a step
trackFunnelStep('invoice_workflow', 'invoice_preview', {
  invoiceId: 'inv_789',
  amount: 150000
})

// Mark funnel as abandoned (e.g., user navigates away)
abandonFunnel('project_creation', 'user_navigated_away')
```

### Automatic Page-Based Funnel Tracking

Use the `useFunnelPageTracking` hook in page components to automatically match funnel steps to routes:

```typescript
import { useFunnelPageTracking } from '../hooks/useAnalytics'

function CreateProjectPage() {
  useFunnelPageTracking('project_creation')
  // ... component
}
```

---

## User Segmentation

Segments are tracked automatically via `user_role` and `user_plan` properties attached to every event.

### Predefined Segments
- **Admin**: Full access, sees all analytics
- **Manager**: Project/task oversight
- **Developer**: Task execution
- **Designer**: Design tasks
- **Intern**: Limited access tasks
- **Client**: Client portal access

### Segment Comparison (in Mixpanel/GA4)

| Dimension | Mixpanel | GA4 |
|-----------|----------|-----|
| Feature Usage | Events breakdown by `role` | Events by user_role |
| Session Duration | People → Sessions → Avg by role | User engagement by user_role |
| Retention | Retention report segmented by role | Cohort analysis by user_role |
| Productivity | Completed tasks / user by role | Custom event count by user_role |

---

## Analytics Dashboard Metrics

### Product Metrics
```sql
-- DAX / Mixpanel equivalent
Daily Active Users (DAU)  = COUNT_DISTINCT(userId) WHERE date = today
Weekly Active Users (WAU) = COUNT_DISTINCT(userId) WHERE date >= today - 7
Monthly Active Users (MAU)= COUNT_DISTINCT(userId) WHERE date >= today - 30
Avg Session Duration      = AVG(session_duration)
User Retention            = users_returning / users_acquired
```

### Business Metrics
```sql
Projects Created  = COUNT(event) WHERE event = 'project_created'
Tasks Completed   = COUNT(event) WHERE event = 'task_completed'
Clients Added     = COUNT(event) WHERE event = 'client_added'
Revenue Generated = SUM(amount) WHERE event = 'invoice_paid'
Invoices Sent     = COUNT(event) WHERE event = 'invoice_sent'
Invoices Paid     = COUNT(event) WHERE event = 'invoice_paid'
```

### Feature Usage Metrics
```sql
Most Used Features   = TOP(event_name, 10) BY count
Least Used Features  = BOTTOM(event_name, 10) BY count
Drop-off Pages       = page WHERE exit_rate > 50%
Most Visited Pages   = TOP(page_path, 10) BY pageviews
```

---

## GA4 Explorations Setup

### Pre-built Exploration Reports

1. **User Paths**: Login → Dashboard → Projects/Tasks/Reports/Invoices
2. **Exit Pages**: Sessions ending without interaction
3. **Drop-off Pages**: Page with high bounce rate before conversion
4. **Session Depth**: Number of pages viewed per session

### Configuring in GA4

1. Go to **Explore** → **Blank**
2. Set **Technique**: Path exploration
3. Add **Page path and screen class** as dimension
4. Add **Event name** as dimension
5. Set filters: `event_name contains 'funnel'`
6. Save as: `YX Manage - User Journey`

---

## Hotjar Configuration

### Pages with Heatmaps & Recordings

| Page | Heatmap | Recording | Scroll Depth |
|------|---------|-----------|-------------|
| Dashboard | Yes | Yes (10%) | Yes |
| Projects | Yes | Yes (10%) | Yes |
| Tasks | Yes | Yes (10%) | Yes |
| Invoices | Yes | Yes (5%) | Yes |
| Reports | Yes | Yes (5%) | Yes |

### Hotjar Funnel Setup

Create in Hotjar dashboard:
1. **Funnel Name**: Project Creation
   - Step 1: Dashboard page visited
   - Step 2: Create project button clicked  
   - Step 3: Form fields filled
   - Step 4: Project created

2. **Funnel Setup Code**:
```typescript
import { hotjarTriggerFunnel } from '../services/analytics/hotjar'

// Trigger Hotjar funnel step (configure funnel ID in Hotjar dashboard)
hotjarTriggerFunnel(HOTJAR_FUNNEL_ID, 1)
```

---

## Testing Checklist

### Staging/QA Verification
- [ ] GA4 debug mode shows events in real-time
- [ ] Mixpanel live view shows all events
- [ ] Hotjar recordings are capturing sessions
- [ ] All page views fire on route change
- [ ] Mandatory events fire correctly
- [ ] Event properties contain all required fields
- [ ] User identification works on login/logout
- [ ] Funnel steps are tracked in correct order
- [ ] Funnel abandonment fires on navigation away
- [ ] User role is attached to all events

### Production Launch
- [ ] All analytics tokens configured in production env
- [ ] Debug mode disabled
- [ ] Event validation passes for all mandatory events
- [ ] Funnel analysis reports created in GA4/Mixpanel
- [ ] Dashboard metrics verified against manual count
- [ ] Performance impact assessed (< 100ms per event)
- [ ] Privacy/compliance reviewed (GDPR consent if needed)

---

## Common Issues & Troubleshooting

### Events not appearing in Mixpanel
1. Check `VITE_MIXPANEL_TOKEN` is set correctly
2. Verify `mixpanel.init()` is called (check console)
3. Ensure `identify()` has been called for the user
4. Check browser console for CORS/blocked requests

### GA4 not showing real-time data
1. Debug mode may need to be enabled via browser extension
2. Data can take 24-48 hours to appear in standard reports
3. Use GA4 DebugView for immediate verification

### Hotjar recordings not available
1. Verify `VITE_HOTJAR_ID` is correct
2. Check Hotjar site status in dashboard
3. Recordings only capture a sample (configurable in Hotjar)

---

## Files Summary

| File | Purpose |
|------|---------|
| `src/services/analytics/index.ts` | Main export, config, init orchestration |
| `src/services/analytics/ga4.ts` | GA4 initialization, page tracking, custom events |
| `src/services/analytics/mixpanel.ts` | Mixpanel init, event tracking, user identification |
| `src/services/analytics/hotjar.ts` | Hotjar init, heatmaps, session recording, funnels |
| `src/services/analytics/events.ts` | Unified event tracking layer (all platforms) |
| `src/services/analytics/funnel.ts` | Funnel definitions, step tracking, abandonment |
| `src/services/analytics/utils.ts` | UUID generation, debounce, formatting utilities |
| `src/types/analytics.ts` | TypeScript types for all analytics objects |
| `src/hooks/useAnalytics.ts` | React hooks for page/event/funnel/timing tracking |
| `src/components/AnalyticsProvider.tsx` | Root provider that initializes all platforms |
| `.env.example` | Environment variable template |
