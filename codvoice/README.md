# CODVOICE - Cloud TTS Platform

A production-ready cloud Text-to-Speech platform built on Piper TTS, designed to replace ElevenLabs in voice agent systems.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- 10GB disk space

### One-Command Deployment

**Windows:**
```bash
cd codvoice
start.bat
```

**Linux/Mac:**
```bash
cd codvoice
chmod +x start.sh
./start.sh
```

**Manual Docker Compose:**
```bash
cd codvoice
docker-compose up -d
```

## Services

After deployment, the following services will be available:

- **Admin Dashboard**: http://localhost
- **API Server**: http://localhost/api
- **Health Check**: http://localhost/api/health

## API Usage

### Authentication
All API requests require an API key in the Authorization header:
```
Authorization: Bearer codvoice-default-key-123
```

**Admin Access:**
```
Authorization: Bearer codvoice-admin-key-456
```

**Rate Limiting:** 100 requests per minute per API key.

### Basic TTS Synthesis
```bash
curl -X POST http://localhost/api/tts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer codvoice-default-key-123" \
  -d '{"text": "Hello world", "voice": "en_US-lessac-medium"}' \
  --output speech.wav
```

### Streaming TTS
```bash
curl -X POST http://localhost/api/tts/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer codvoice-default-key-123" \
  -d '{"text": "Hello world", "voice": "en_US-lessac-medium"}' \
  --output speech.wav
```

### Advanced Parameters
```json
{
  "text": "Hello world",
  "voice": "en_US-lessac-medium",
  "speaker_id": 0,
  "length_scale": 1.0,
  "noise_scale": 0.667,
  "noise_w_scale": 0.8
}
```

### List Available Voices
```bash
curl http://localhost/api/voices
```

## Admin Dashboard

Access the admin dashboard at http://localhost to:

- View usage analytics
- Test TTS synthesis  
- Upload voice models
- Manage voice models
- Monitor system health
- View request logs

**Admin Pages:**
- Dashboard: http://localhost
- Voice Upload: http://localhost/upload
- System Logs: http://localhost/logs

**Admin Authentication Required:** Use `codvoice-admin-key-456`

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    nginx    │────│ codvoice-api│────│Redis Queue  │
│   (proxy)   │    │  (FastAPI)  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │            ┌─────────────┐    ┌─────────────┐
       │────────────│  postgres   │    │codvoice-    │
       │            │ (database)  │    │worker (x2)  │
       │            └─────────────┘    └─────────────┘
       │                                       │
┌─────────────┐                       ┌─────────────┐
│codvoice-admin│                       │codvoice-tts │
│  (Next.js)  │                       │   (Piper)   │
└─────────────┘                       └─────────────┘
```

**New Features:**
- Redis worker queue for scalable TTS processing
- Rate limiting (100 requests/minute per API key)
- Admin authentication for dashboard
- Startup voice preloading for better performance
- Horizontal worker scaling

## Voice Agent Integration

CODVOICE is designed to integrate seamlessly into voice agent architectures:

```
User Speech → Browser STT → LLM → CODVOICE API → Audio Response
```

### JavaScript Integration
```javascript
async function synthesizeSpeech(text) {
  const response = await fetch('/api/tts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer codvoice-default-key-123'
    },
    body: JSON.stringify({
      text: text,
      voice: 'en_US-lessac-medium'
    })
  });
  
  const audioBlob = await response.blob();
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  audio.play();
}
```

### Python Integration
```python
import requests

def synthesize_speech(text):
    response = requests.post('http://localhost/api/tts', 
        headers={
            'Authorization': 'Bearer codvoice-default-key-123',
            'Content-Type': 'application/json'
        },
        json={
            'text': text,
            'voice': 'en_US-lessac-medium'
        }
    )
    
    with open('speech.wav', 'wb') as f:
        f.write(response.content)
```

## Voice Management

### Adding New Voices

1. Access the admin dashboard at http://localhost
2. Go to Voice Management section
3. Upload .onnx model and .onnx.json config files
4. Voice will be automatically available via API

### Voice Model Format

CODVOICE uses Piper-compatible ONNX models:
- `voice_name.onnx` - Neural network model
- `voice_name.onnx.json` - Voice configuration

## Performance

- **Latency**: <100ms first audio for real-time conversations
- **Throughput**: 50+ concurrent requests per instance
- **Memory**: 100-500MB per loaded voice model
- **Scaling**: Horizontal scaling with Docker Compose

## Monitoring

### Health Checks
```bash
curl http://localhost/api/health
```

### Analytics API
```bash
curl http://localhost/api/admin/analytics
```

### System Status
```bash
curl http://localhost/api/admin/system
```

## Configuration

### Environment Variables

**Backend (codvoice-api):**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `TTS_ENGINE_URL`: TTS engine URL

**TTS Engine (codvoice-tts):**
- `CUDA_VISIBLE_DEVICES`: GPU device selection

### Database Schema

The system uses PostgreSQL with the following tables:
- `voices` - Voice model metadata
- `tts_requests` - Request analytics
- `api_keys` - API key management

## Troubleshooting

### Common Issues

**Services not starting:**
```bash
docker-compose logs
```

**API not responding:**
```bash
docker-compose restart codvoice-api
```

**Voice not found:**
- Check if voice files exist in `/models` directory
- Verify voice is enabled in admin dashboard

### Logs
```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs codvoice-api
docker-compose logs codvoice-tts
```

## Development

### Local Development Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# TTS Engine
cd tts-engine
pip install -r requirements.txt
uvicorn piper_runtime:app --port 8001

# Dashboard
cd dashboard
npm install
npm run dev
```

### Adding Features

1. Backend API: Modify files in `backend/api/`
2. TTS Engine: Update `tts-engine/piper_runtime.py`
3. Admin Dashboard: Edit files in `dashboard/src/`

## Production Deployment

### Scaling
```bash
# Scale workers horizontally
docker-compose up --scale codvoice-worker=5

# Scale API servers
docker-compose up --scale codvoice-api=3
```

### Security
- Change default API keys
- Use HTTPS with SSL certificates
- Configure firewall rules
- Enable authentication

### Monitoring
- Add Prometheus metrics
- Configure log aggregation
- Set up health check alerts

## License

GPL v3.0 - See LICENSE file for details.

## Support

- Issues: GitHub Issues
- Documentation: This README
- Community: GitHub Discussions