import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Logs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLogs()
  }, [])

  const fetchLogs = async () => {
    try {
      const response = await axios.get('/api/admin/logs', {
        headers: {
          'Authorization': 'Bearer codvoice-admin-key-456'
        }
      })
      setLogs(response.data.logs || [])
    } catch (error) {
      console.error('Error fetching logs:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">System Logs</h1>
        
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-medium">Recent Activity</h2>
              <button
                onClick={fetchLogs}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Refresh
              </button>
            </div>
          </div>
          
          <div className="p-6">
            {loading ? (
              <div className="text-center py-8">
                <div className="text-gray-500">Loading logs...</div>
              </div>
            ) : logs.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-500">No logs available</div>
              </div>
            ) : (
              <div className="space-y-2">
                {logs.map((log, index) => (
                  <div key={index} className="flex items-center p-3 bg-gray-50 rounded">
                    <div className="flex-shrink-0 w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                    <div className="text-sm text-gray-700">{log}</div>
                    <div className="ml-auto text-xs text-gray-500">
                      {new Date().toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}