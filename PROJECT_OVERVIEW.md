# CODVOICE: Technical Architecture Overview

*Adapted from Piper Neural Text-to-Speech Engine*

## 1. Project Overview

Piper is a fast, local neural text-to-speech (TTS) engine that combines VITS (Variational Inference with adversarial learning for end-to-end Text-to-Speech) neural architecture with espeak-ng phonemization. The system is designed for high-quality, real-time speech synthesis with minimal latency and resource requirements.

**Key Features:**
- Neural VITS-based synthesis using ONNX Runtime
- espeak-ng integration for robust phonemization
- Multi-speaker voice support
- Streaming audio generation
- Cross-platform compatibility (Python, C++, HTTP APIs)
- GPU acceleration support
- Phoneme alignment for lip-sync applications

## 2. Core Architecture

```
Text Input → Phonemization → Neural Model → Audio Output
     ↓           ↓              ↓            ↓
  espeak-ng → Phoneme IDs → VITS/ONNX → WAV Samples
```

**Components:**
- **Text Processor**: Handles input text normalization and sentence segmentation
- **Phonemizer**: espeak-ng bridge for text-to-phoneme conversion
- **Neural Engine**: ONNX Runtime executing VITS model
- **Audio Generator**: Converts model output to PCM audio
- **Alignment System**: Maps phonemes to audio samples for visemes

## 3. Text Processing Pipeline

The text processing follows this flow:

1. **Input Sanitization**: Unicode normalization (NFD)
2. **Sentence Segmentation**: Split text by sentence boundaries
3. **Language Detection**: Automatic or manual language selection
4. **Phoneme Block Processing**: Handle `[[phoneme]]` overrides
5. **Arabic Diacritization**: Optional tashkeel processing for Arabic

**Supported Input Formats:**
- Plain text with automatic phonemization
- Raw phoneme strings with `[[phonemes]]` blocks
- Custom phoneme sequences
- Direct phoneme ID arrays

## 4. Phonemization (espeak-ng Bridge)

The phonemization system converts text to International Phonetic Alphabet (IPA) symbols:

**Process:**
1. **Language Voice Selection**: Set espeak-ng voice (e.g., "en-us", "de", "fr")
2. **Text-to-Phonemes**: Convert text using espeak-ng IPA output
3. **Phoneme Filtering**: Remove language switch flags `(lang)`
4. **Unicode Decomposition**: NFD normalization for accent separation
5. **Phoneme Mapping**: Convert IPA symbols to model-specific phoneme IDs

**Key Files:**
- `phonemize_espeak.py`: Main phonemization interface
- `espeakbridge.c`: C extension for espeak-ng integration
- `phoneme_ids.py`: Phoneme-to-ID mapping utilities

## 5. Voice Model Architecture (VITS + ONNX)

Piper uses the VITS (Variational Inference with adversarial learning for end-to-end Text-to-Speech) architecture:

**VITS Components:**
- **Text Encoder**: Transforms phoneme sequences to latent representations
- **Duration Predictor**: Estimates phoneme timing (Stochastic or Deterministic)
- **Flow-based Generator**: Converts text features to mel-spectrograms
- **Vocoder**: HiFi-GAN-based neural vocoder for audio synthesis
- **Posterior Encoder**: Training-time component for variational inference

**Model Structure:**
```
Phoneme IDs → Text Encoder → Duration Predictor → Flow Generator → Vocoder → Audio
                ↓              ↓                    ↓             ↓
            Hidden Repr.   Alignment Matrix    Mel Features   Raw Audio
```

**ONNX Export:**
- Models exported from PyTorch Lightning checkpoints
- Optimized for inference with ONNX Runtime
- Support for both CPU and GPU execution
- Dynamic batch sizes and sequence lengths

## 6. Audio Generation Pipeline

**Synthesis Flow:**
1. **Phoneme Encoding**: Convert phoneme IDs to embeddings
2. **Duration Prediction**: Estimate phoneme durations
3. **Alignment Generation**: Create phoneme-to-frame alignment
4. **Latent Generation**: Sample from learned distributions
5. **Vocoding**: Convert features to raw audio waveforms

**Audio Specifications:**
- Sample Rate: 22050 Hz (configurable)
- Bit Depth: 16-bit signed PCM
- Channels: Mono (1 channel)
- Format: WAV, raw PCM, or streaming chunks

## 7. Streaming Audio Generation

Piper supports real-time streaming synthesis:

**Streaming Process:**
1. **Sentence-by-Sentence**: Process text in sentence chunks
2. **Incremental Synthesis**: Generate audio as phonemes are processed
3. **Chunk Delivery**: Return `AudioChunk` objects with metadata
4. **Buffer Management**: Minimize memory usage with streaming buffers

**AudioChunk Structure:**
```python
@dataclass
class AudioChunk:
    sample_rate: int
    sample_width: int
    sample_channels: int
    audio_float_array: np.ndarray
    phonemes: list[str]
    phoneme_ids: list[int]
    phoneme_id_samples: Optional[np.ndarray]  # Alignments
    phoneme_alignments: Optional[list[PhonemeAlignment]]
```

## 8. Alignment System (Phoneme Alignment for Visemes)

The alignment system provides precise timing information for lip-sync applications:

**Alignment Process:**
1. **Model Patching**: Modify ONNX model to output alignment data
2. **Phoneme Tracking**: Map each phoneme to audio sample counts
3. **Temporal Alignment**: Calculate precise timing for each phoneme
4. **Viseme Mapping**: Convert phonemes to mouth shapes

**Alignment Data:**
- **Phoneme-to-Sample Mapping**: Number of audio samples per phoneme
- **Temporal Boundaries**: Start/end times for each phoneme
- **Viseme Compatibility**: Direct mapping to facial animation systems

## 9. Python API

The Python API provides high-level access to Piper functionality:

**Core Classes:**
- `PiperVoice`: Main voice synthesis interface
- `SynthesisConfig`: Configuration for synthesis parameters
- `AudioChunk`: Container for audio data and metadata

**Usage Example:**
```python
from piper import PiperVoice, SynthesisConfig

# Load voice
voice = PiperVoice.load("model.onnx", use_cuda=True)

# Configure synthesis
config = SynthesisConfig(
    speaker_id=0,
    length_scale=1.0,
    noise_scale=0.667,
    noise_w_scale=0.8
)

# Generate audio
for chunk in voice.synthesize("Hello world", config):
    # Process audio chunk
    audio_data = chunk.audio_int16_bytes
```

## 10. HTTP API

The HTTP server provides REST endpoints for TTS synthesis:

**Endpoints:**
- `POST /`: Synthesize text to audio
- `GET /voices`: List available voices
- `GET /all-voices`: List all Piper voices from repository
- `POST /download`: Download voice models

**Request Format:**
```json
{
  "text": "Text to synthesize",
  "voice": "en_US-lessac-medium",
  "speaker": "speaker_name",
  "speaker_id": 0,
  "length_scale": 1.0,
  "noise_scale": 0.667,
  "noise_w_scale": 0.8
}
```

**Response**: WAV audio file (binary)

## 11. CLI System

Command-line interface for batch processing and testing:

**Key Features:**
- File input/output processing
- Batch synthesis with directory output
- Real-time audio playback
- Raw audio streaming to stdout
- Voice model management

**Usage:**
```bash
# Basic synthesis
python -m piper -m voice.onnx -f output.wav "Hello world"

# Batch processing
python -m piper -m voice.onnx -d output_dir/ -i input.txt

# Streaming output
python -m piper -m voice.onnx --output-raw "Text" | aplay
```

## 12. Voice Model Format (.onnx + .onnx.json)

Voice models consist of two files:

**ONNX Model (.onnx):**
- Neural network weights and architecture
- ONNX Runtime compatible format
- Optimized for inference performance
- Support for CPU and GPU execution

**Configuration (.onnx.json):**
```json
{
  "audio": {"sample_rate": 22050},
  "espeak": {"voice": "en-us"},
  "inference": {
    "noise_scale": 0.667,
    "length_scale": 1.0,
    "noise_w": 0.8
  },
  "phoneme_id_map": {"a": [14], "b": [15]},
  "num_speakers": 1,
  "speaker_id_map": {},
  "language": {"code": "en_US"}
}
```

## 13. Voice Model Repository Structure

Voice models follow a standardized naming convention:

**Format**: `{language}-{name}-{quality}.onnx`
- **Language**: ISO language code (e.g., `en_US`, `de_DE`)
- **Name**: Voice identifier (e.g., `lessac`, `thorsten`)
- **Quality**: Model size (`low`, `medium`, `high`)

**Repository Organization:**
```
voices/
├── en_US-lessac-medium.onnx
├── en_US-lessac-medium.onnx.json
├── de_DE-thorsten-medium.onnx
└── de_DE-thorsten-medium.onnx.json
```

## 14. Multi-speaker Support

Piper supports multiple speakers within a single model:

**Configuration:**
- Speaker embeddings in neural architecture
- Speaker ID mapping in configuration
- Runtime speaker selection

**Usage:**
```python
# Multi-speaker synthesis
config = SynthesisConfig(speaker_id=2)
voice.synthesize("Text", config)
```

## 15. GPU Acceleration Support

ONNX Runtime provides GPU acceleration:

**Supported Providers:**
- CUDA (NVIDIA GPUs)
- DirectML (Windows)
- OpenVINO (Intel hardware)
- TensorRT (NVIDIA optimization)

**Configuration:**
```python
# Enable CUDA
voice = PiperVoice.load("model.onnx", use_cuda=True)
```

## 16. Training Pipeline (PyTorch Lightning)

Training uses PyTorch Lightning for scalability:

**Training Components:**
- **Dataset**: Audio/text pairs with phoneme alignment
- **Model**: VITS architecture with discriminators
- **Lightning Module**: Training loop and optimization
- **Callbacks**: Checkpointing, logging, validation

**Training Command:**
```bash
python -m piper.train fit \
  --data.csv_path metadata.csv \
  --data.audio_dir audio/ \
  --model.sample_rate 22050 \
  --data.espeak_voice en-us
```

## 17. Export Pipeline (Checkpoint → ONNX)

Convert trained models to ONNX format:

**Export Process:**
1. Load PyTorch Lightning checkpoint
2. Extract generator model
3. Remove weight normalization
4. Export to ONNX with dynamic shapes
5. Validate exported model

**Export Command:**
```bash
python -m piper.train.export_onnx \
  --checkpoint model.ckpt \
  --output-file model.onnx
```

## 18. Supported Languages

Piper supports 40+ languages through espeak-ng:

**Major Languages:**
- English (US, UK, AU)
- German, French, Spanish
- Italian, Portuguese, Dutch
- Russian, Polish, Czech
- Chinese (Mandarin), Japanese
- Arabic, Hindi, Turkish

**Language Configuration:**
- espeak-ng voice selection
- Language-specific phoneme mappings
- Custom phonemization rules

## 19. Performance Characteristics

**Synthesis Speed:**
- Real-time factor: 0.1-0.5x (faster than real-time)
- Latency: 50-200ms first audio
- Memory usage: 100-500MB per voice
- CPU usage: 10-50% single core

**Model Sizes:**
- Low quality: 5-15MB
- Medium quality: 15-50MB
- High quality: 50-150MB

## 20. Latency Considerations

**Latency Sources:**
1. **Text Processing**: 1-5ms
2. **Phonemization**: 5-20ms
3. **Neural Inference**: 20-100ms
4. **Audio Generation**: 10-50ms

**Optimization Strategies:**
- Sentence-level streaming
- Model quantization
- GPU acceleration
- Batch processing

## 21. CPU vs GPU Inference

**CPU Inference:**
- Lower memory usage
- Consistent performance
- Better for multiple concurrent requests
- No GPU driver dependencies

**GPU Inference:**
- 2-10x faster synthesis
- Higher memory usage
- Better for batch processing
- Requires CUDA/GPU setup

---

# Converting Piper into CODVOICE

## Production Voice Service Architecture

Transform Piper into a scalable SaaS voice synthesis platform for:

- **AI Voice Agents**: Real-time conversational AI
- **SaaS Voice APIs**: Multi-tenant voice services
- **AI Assistants**: Virtual assistant applications
- **Voice Widgets**: Embeddable voice components
- **Customer Service Bots**: Automated support systems

## Core Service Components

### 1. Streaming Audio Responses

**WebSocket Streaming Architecture:**
```python
# Real-time streaming synthesis
async def stream_synthesis(websocket, text):
    voice = await load_voice_async(voice_id)
    async for chunk in voice.synthesize_stream(text):
        await websocket.send_bytes(chunk.audio_int16_bytes)
```

**Implementation:**
- WebSocket-based audio streaming
- Chunked audio delivery (100-200ms chunks)
- Real-time synthesis pipeline
- Adaptive bitrate streaming

### 2. WebSocket Audio Streaming

**Protocol Design:**
```json
{
  "type": "synthesis_request",
  "text": "Hello world",
  "voice_id": "en_US_neural_001",
  "config": {
    "speed": 1.0,
    "pitch": 0.0,
    "emotion": "neutral"
  }
}
```

**Response Stream:**
```json
{
  "type": "audio_chunk",
  "chunk_id": 1,
  "audio_data": "base64_encoded_pcm",
  "is_final": false,
  "alignments": [...]
}
```

### 3. Multi-Voice API

**Voice Management System:**
- Dynamic voice loading/unloading
- Voice model caching and optimization
- Multi-tenant voice isolation
- Voice quality tiers (standard, premium, custom)

**API Endpoints:**
```
GET /api/v1/voices - List available voices
POST /api/v1/synthesis - Synthesize text
WS /api/v1/stream - WebSocket streaming
POST /api/v1/voices/clone - Voice cloning
```

### 4. Voice Selection

**Intelligent Voice Matching:**
- Language detection and voice selection
- Emotion-based voice selection
- Context-aware voice switching
- A/B testing for voice optimization

**Voice Metadata:**
```json
{
  "voice_id": "en_US_neural_001",
  "language": "en_US",
  "gender": "female",
  "age_group": "adult",
  "style": "conversational",
  "emotions": ["neutral", "happy", "sad"],
  "quality_tier": "premium"
}
```

### 5. Latency Optimization

**Performance Strategies:**
- **Model Quantization**: INT8/FP16 optimization
- **Model Caching**: Pre-loaded voice models
- **Predictive Loading**: Anticipate voice usage
- **Edge Deployment**: Regional voice servers
- **Connection Pooling**: Reuse ONNX sessions

**Target Latencies:**
- First audio chunk: <100ms
- Streaming chunks: <50ms
- Voice switching: <200ms

### 6. Model Caching

**Multi-Level Caching:**
```python
class VoiceCache:
    def __init__(self):
        self.memory_cache = {}  # Hot voices in RAM
        self.disk_cache = {}    # Warm voices on SSD
        self.remote_cache = {}  # Cold voices in cloud storage
    
    async def get_voice(self, voice_id):
        # Check memory → disk → remote
        return await self.load_with_fallback(voice_id)
```

**Cache Strategies:**
- LRU eviction for memory management
- Predictive pre-loading based on usage patterns
- Distributed caching across service instances

### 7. Server Deployment

**Microservices Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │────│  Voice Service  │────│  Model Storage  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│  Cache Service  │──────────────┘
                        └─────────────────┘
```

**Service Components:**
- **API Gateway**: Request routing, authentication, rate limiting
- **Voice Service**: Core synthesis engine
- **Model Storage**: Voice model repository
- **Cache Service**: Distributed model caching
- **Monitoring**: Performance metrics and alerting

### 8. Docker Containerization

**Multi-Stage Dockerfile:**
```dockerfile
# Build stage
FROM python:3.11-slim as builder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY src/ /app/src/
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "codvoice.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Container Optimization:**
- Multi-stage builds for smaller images
- GPU-enabled containers for acceleration
- Health checks and graceful shutdown
- Resource limits and monitoring

### 9. Horizontal Scaling

**Auto-Scaling Strategy:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codvoice-synthesis
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codvoice-synthesis
  template:
    spec:
      containers:
      - name: synthesis
        image: codvoice/synthesis:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

**Scaling Considerations:**
- Stateless service design
- Load balancing with session affinity
- Auto-scaling based on CPU/memory/queue depth
- Circuit breakers for fault tolerance

### 10. Voice Cloning Pipeline

**Custom Voice Training:**
```python
class VoiceCloner:
    async def clone_voice(self, audio_samples, speaker_name):
        # 1. Audio preprocessing and validation
        processed_audio = await self.preprocess_audio(audio_samples)
        
        # 2. Automatic transcription
        transcripts = await self.transcribe_audio(processed_audio)
        
        # 3. Fine-tune base model
        model = await self.fine_tune_model(processed_audio, transcripts)
        
        # 4. Export to ONNX
        onnx_model = await self.export_to_onnx(model)
        
        return voice_id
```

**Cloning Process:**
- Audio quality validation
- Automatic speech recognition for transcripts
- Few-shot learning with base models
- Quality assessment and validation

### 11. Phoneme Alignment for Lip-Sync

**Real-time Alignment API:**
```python
class AlignmentService:
    async def get_alignments(self, text, voice_id):
        voice = await self.load_voice(voice_id)
        chunks = []
        
        async for chunk in voice.synthesize(text, include_alignments=True):
            alignments = self.process_alignments(chunk.phoneme_alignments)
            chunks.append({
                'audio': chunk.audio_int16_bytes,
                'alignments': alignments,
                'visemes': self.phonemes_to_visemes(alignments)
            })
        
        return chunks
```

**Viseme Mapping:**
- Phoneme-to-viseme conversion
- Temporal alignment with audio
- 3D facial animation compatibility
- Real-time streaming support

---

# Technical Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                CODVOICE ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Client    │    │   Client    │    │   Client    │    │   Client    │     │
│  │   (Web)     │    │   (Mobile)  │    │   (API)     │    │ (WebSocket) │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │                  │            │
│         └──────────────────┼──────────────────┼──────────────────┘            │
│                            │                  │                               │
│  ┌─────────────────────────┼──────────────────┼─────────────────────────────┐ │
│  │                    API GATEWAY                                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │    Auth     │  │Rate Limiting│  │Load Balancer│  │   Routing   │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────┼──────────────────┼─────────────────────────────┘ │
│                            │                  │                               │
│  ┌─────────────────────────┼──────────────────┼─────────────────────────────┐ │
│  │                   SYNTHESIS SERVICE                                     │ │
│  │                            │                  │                         │ │
│  │  ┌─────────────┐    ┌──────┴──────┐    ┌──────┴──────┐                 │ │
│  │  │Text Processor│    │HTTP Handler │    │WS Handler   │                 │ │
│  │  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                 │ │
│  │         │                  │                  │                         │ │
│  │  ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐                 │ │
│  │  │ Phonemizer  │    │Voice Manager│    │Stream Manager│                │ │
│  │  │(espeak-ng)  │    │             │    │             │                 │ │
│  │  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                 │ │
│  │         │                  │                  │                         │ │
│  │  ┌──────┴──────────────────┴──────────────────┴──────┐                 │ │
│  │  │                NEURAL ENGINE                      │                 │ │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│                 │ │
│  │  │  │ONNX Runtime │  │ GPU Accel   │  │Model Cache  ││                 │ │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘│                 │ │
│  │  └─────────────────────────────────────────────────────┘                 │ │
│  └─────────────────────────┼──────────────────┼─────────────────────────────┘ │
│                            │                  │                               │
│  ┌─────────────────────────┼──────────────────┼─────────────────────────────┐ │
│  │                   STORAGE LAYER                                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │Voice Models │  │Model Cache  │  │User Data    │  │Metrics DB   │    │ │
│  │  │   (ONNX)    │  │  (Redis)    │  │ (Postgres)  │  │(InfluxDB)   │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        MONITORING & OBSERVABILITY                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │  Prometheus │  │   Grafana   │  │    Jaeger   │  │   ELK Stack │    │   │
│  │  │  (Metrics)  │  │(Dashboards) │  │  (Tracing)  │  │  (Logging)  │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘

Data Flow:
1. Client Request → API Gateway → Synthesis Service
2. Text Processing → Phonemization → Neural Inference
3. Audio Generation → Streaming/Response → Client
4. Caching: Model Cache ↔ Voice Models
5. Monitoring: All components → Observability Stack
```

This architecture provides a production-ready foundation for CODVOICE, enabling scalable, real-time voice synthesis for AI applications with enterprise-grade reliability and performance.