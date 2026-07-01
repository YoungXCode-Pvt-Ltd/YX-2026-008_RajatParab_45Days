import { useEffect } from 'react'

export default function Tasks() {
  useEffect(() => { document.title = 'Tasks | YX Manage' }, [])
  return <div><h1>Tasks</h1></div>
}
