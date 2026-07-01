import { useEffect } from 'react'

export default function Team() {
  useEffect(() => { document.title = 'Team | YX Manage' }, [])
  return <div><h1>Team</h1></div>
}
