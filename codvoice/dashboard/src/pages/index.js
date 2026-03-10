import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Dashboard() {
  const [voices, setVoices] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [testText, setTestText] = useState('Hello, this is a test of CODVOICE.')
  const [selectedVoice, setSelectedVoice] = useState('')

  useEffect(() => {
    fetchVoices()
    fetchAnalytics()
  }, [])

  const fetchVoices = async () => {
    try {
      const response = await axios.get('/api/admin/voices')
      setVoices(response.data)
      if (response.data.length > 0) {
        setSelectedVoice(response.data[0].name)
      }
    } catch (error) {
      console.error('Error fetching voices:', error)
    }
  }

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get('/api/admin/analytics')
      setAnalytics(response.data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    }
  }

  const testTTS = async () => {
    try {
      const response = await axios.post('/api/tts', {
        text: testText,
        voice: selectedVoice
      }, {
        headers: {
          'Authorization': 'Bearer codvoice-default-key-123'
        },
        responseType: 'blob'
      })
      
      const audioUrl = URL.createObjectURL(response.data)
      const audio = new Audio(audioUrl)
      audio.play()
    } catch (error) {
      console.error('Error testing TTS:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">CODVOICE Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Total Requests</h3>
            <p className="text-3xl font-bold text-blue-600">
              {analytics?.total_requests || 0}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Active Voices</h3>
            <p className="text-3xl font-bold text-green-600">
              {voices.filter(v => v.enabled).length}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">System Status</h3>
            <p className="text-3xl font-bold text-green-600">Healthy</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-bold mb-4">Test TTS</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Text</label>
              <textarea
                value={testText}
                onChange={(e) => setTestText(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                rows={3}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Voice</label>
              <select
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
              >
                {voices.map(voice => (
                  <option key={voice.id} value={voice.name}>{voice.name}</option>
                ))}
              </select>
            </div>
            <button
              onClick={testTTS}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Test Speech
            </button>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Voice Management</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Language</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {voices.map(voice => (
                  <tr key={voice.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {voice.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {voice.language}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        voice.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {voice.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}