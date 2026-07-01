import { useEffect } from 'react'

export default function Settings() {
  useEffect(() => { document.title = 'Settings | YX Manage' }, [])
  return <div><h1>Settings</h1></div>
}
