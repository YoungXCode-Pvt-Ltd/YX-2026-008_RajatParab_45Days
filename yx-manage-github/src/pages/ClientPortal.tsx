import { useEffect } from 'react'

export default function ClientPortal() {
  useEffect(() => { document.title = 'Client Portal | YX Manage' }, [])
  return <div><h1>Client Portal</h1></div>
}
