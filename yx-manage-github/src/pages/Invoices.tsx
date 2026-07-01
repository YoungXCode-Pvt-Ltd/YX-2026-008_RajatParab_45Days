import { useEffect } from 'react'
import { useFunnelPageTracking } from '../hooks/useAnalytics'
import { trackFunnelStep } from '../services/analytics/funnel'
import { trackInvoiceEvent } from '../services/analytics/events'

export default function Invoices() {
  useFunnelPageTracking('invoice_workflow')

  useEffect(() => {
    trackInvoiceEvent('invoice_sent', {
      invoiceId: 'demo-invoice-001',
      amount: 50000,
      status: 'sent'
    })
    trackFunnelStep('invoice_workflow', 'invoice_sent')
  }, [])

  return <div><h1>Invoices</h1></div>
}
