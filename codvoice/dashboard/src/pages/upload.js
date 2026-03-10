import { useState } from 'react'
import axios from 'axios'

export default function VoiceUpload() {
  const [name, setName] = useState('')
  const [language, setLanguage] = useState('en_US')
  const [modelFile, setModelFile] = useState(null)
  const [configFile, setConfigFile] = useState(null)
  const [uploading, setUploading] = useState(false)

  const handleUpload = async (e) => {
    e.preventDefault()
    
    if (!name || !modelFile || !configFile) {
      alert('Please fill all fields and select both files')
      return
    }

    setUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('name', name)
      formData.append('language', language)
      formData.append('model_file', modelFile)
      formData.append('config_file', configFile)

      await axios.post('/api/admin/voices/upload', formData, {
        headers: {
          'Authorization': 'Bearer codvoice-admin-key-456',
          'Content-Type': 'multipart/form-data'
        }
      })

      alert('Voice uploaded successfully!')
      setName('')
      setModelFile(null)
      setConfigFile(null)
      
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Upload Voice Model</h1>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <form onSubmit={handleUpload} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Voice Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="e.g., en_US-custom-medium"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="en_US">English (US)</option>
                <option value="en_GB">English (UK)</option>
                <option value="de_DE">German</option>
                <option value="fr_FR">French</option>
                <option value="es_ES">Spanish</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Model File (.onnx)</label>
              <input
                type="file"
                accept=".onnx"
                onChange={(e) => setModelFile(e.target.files[0])}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Config File (.onnx.json)</label>
              <input
                type="file"
                accept=".json"
                onChange={(e) => setConfigFile(e.target.files[0])}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                required
              />
            </div>

            <button
              type="submit"
              disabled={uploading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {uploading ? 'Uploading...' : 'Upload Voice'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}