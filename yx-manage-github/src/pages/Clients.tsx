import { useEffect } from 'react'

export default function Clients() {
  useEffect(() => {
    document.title = 'Clients | YX Manage'
  }, [])
  return <div><h1>Clients</h1></div>
}
