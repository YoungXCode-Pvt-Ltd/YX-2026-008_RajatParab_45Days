import { useEffect } from 'react'

export default function ProjectDetails() {
  useEffect(() => { document.title = 'Project Details | YX Manage' }, [])
  return <div><h1>Project Details</h1></div>
}
