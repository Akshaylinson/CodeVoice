# Piper Text-to-Speech Project Summary

## Project Overview

**Project Name:** Piper  
**Version:** 1.4.1  
**License:** GPL-3.0-or-later  
**Organization:** Open Home Foundation (OHF-Voice)  
**Primary Purpose:** Fast and local neural text-to-speech engine with embedded espeak-ng for phonemization

## Executive Summary

Piper is a high-performance, privacy-focused neural text-to-speech (TTS) engine designed to run locally without cloud dependencies. It leverages ONNX Runtime for efficient inference and embeds espeak-ng for phoneme generation, making it suitable for accessibility applications, voice assistants, and embedded systems.

## Key Features

### Core Capabilities
- **Local Processing:** Runs entirely offline without external API calls
- **Neural TTS:** Uses ONNX-based neural voice models for natural-sounding speech
- **Multi-language Support:** Supports multiple languages through espeak-ng integration
- **Multiple Interfaces:** CLI, Python API, HTTP server, and C/C++ API
- **GPU Acceleration:** Optional CUDA support for faster inference
- **Voice Training:** Complete training pipeline for creating custom voices
- **Phoneme Alignment:** Experimental support for phoneme-to-audio alignment
- **Multi-speaker Voices:** Support for voices with multiple speakers

### Phonemization Options
1. **espeak-ng** (default): IPA phonemes via espeak-ng
2. **text**: Direct codepoint-based phonemization
3. **pinyin**: Chinese phonemization using g2pW
4. **Raw phonemes**: Manual phoneme injection with `[[ phonemes ]]` syntax

### Audio Features
- Configurable sample rate (typically 22050 Hz)
- 16-bit PCM audio output
- Volume adjustment
- Audio normalization
- Sentence silence control
- Streaming audio generation

## Technical Architecture

### Technology Stack
- **Language:** Python 3.9+ (with C/C++ components)
- **ML Framework:** ONNX Runtime for inference
- **Training:** PyTorch Lightning
- **Phonemization:** espeak-ng (embedded)
- **Build System:** CMake + scikit-build
- **Testing:** pytest

### Project Structure
```
piper1-gpl/
├── src/piper/              # Main Python package
│   ├── train/              # Training pipeline (VITS-based)
│   ├── tashkeel/           # Arabic diacritization
│   ├── voice.py            # Core synthesis engine
│   ├── config.py           # Configuration classes
│   ├── phonemize_*.py      # Phonemization modules
│   └── http_server.py      # Flask-based HTTP API
├── libpiper/               # C/C++ API library
│   ├── include/            # Header files
│   └── src/                # C++ implementation
├── tests/                  # Unit tests
├── docs/                   # Documentation
├── script/                 # Development scripts
└── docker/                 # Docker configuration
```

### Core Components

#### 1. Voice Synthesis (voice.py)
- `PiperVoice`: Main voice class for loading models and synthesis
- `AudioChunk`: Container for audio data with metadata
- `PhonemeAlignment`: Phoneme-to-audio timing information
- Thread-safe espeak-ng phonemizer singleton

#### 2. Configuration (config.py)
- `PiperConfig`: Voice model configuration
- `SynthesisConfig`: Runtime synthesis parameters
- Configurable noise scales, length scales, and audio normalization

#### 3. Training Pipeline (train/)
- VITS-based architecture (Variational Inference TTS)
- PyTorch Lightning integration
- Support for multi-speaker training
- ONNX export functionality
- Monotonic alignment search

#### 4. Phonemization
- **espeak-ng**: Embedded for IPA phoneme generation
- **Chinese**: g2pW-based with quantized models
- **Arabic**: Tashkeel diacritization support
- **Custom**: Raw phoneme injection

## Installation & Usage

### Installation
```bash
pip install piper-tts
```

### Voice Management
```bash
# List available voices
python3 -m piper.download_voices

# Download a specific voice
python3 -m piper.download_voices en_US-lessac-medium
```

### Command Line Usage
```bash
# Generate WAV file
python3 -m piper -m en_US-lessac-medium -f output.wav -- 'Hello world'

# Play directly (requires ffplay)
python3 -m piper -m en_US-lessac-medium -- 'Hello world'

# With GPU acceleration
python3 -m piper --cuda -m en_US-lessac-medium -f output.wav -- 'Hello world'
```

### Python API Usage
```python
import wave
from piper import PiperVoice, SynthesisConfig

# Load voice
voice = PiperVoice.load("/path/to/voice.onnx")

# Synthesize to WAV
with wave.open("output.wav", "wb") as wav_file:
    voice.synthesize_wav("Hello world", wav_file)

# Streaming synthesis
for chunk in voice.synthesize("Hello world"):
    # Process audio chunk
    audio_data = chunk.audio_int16_bytes
```

### HTTP Server
```bash
python3 -m piper.http_server -m en_US-lessac-medium
```

### C/C++ API
```c++
#include <piper.h>

piper_synthesizer *synth = piper_create(
    "/path/to/voice.onnx",
    "/path/to/voice.onnx.json",
    "/path/to/espeak-ng-data"
);

piper_synthesize_start(synth, "Hello world", NULL);
piper_audio_chunk chunk;
while (piper_synthesize_next(synth, &chunk) != PIPER_DONE) {
    // Process audio chunk
}
piper_free(synth);
```

## Dependencies

### Core Dependencies
- `onnxruntime>=1,<2` - Neural network inference
- Python 3.9+ - Runtime environment

### Training Dependencies
- `torch>=2,<3` - Deep learning framework
- `lightning>=2,<3` - Training framework
- `tensorboard>=2,<3` - Training visualization
- `librosa<1` - Audio processing
- `pysilero-vad>=2.1,<3` - Voice activity detection

### Optional Dependencies
- `flask>=3,<4` - HTTP server
- `onnxruntime-gpu` - GPU acceleration
- `g2pW>=0.1.1,<1` - Chinese phonemization

### Development Dependencies
- `black==24.8.0` - Code formatting
- `flake8==7.1.1` - Linting
- `mypy==1.14.0` - Type checking
- `pylint==3.2.7` - Code analysis
- `pytest==8.3.4` - Testing

## Use Cases & Adoption

### Notable Projects Using Piper
1. **Home Assistant** - Smart home voice integration
2. **NVDA** - Screen reader for visually impaired
3. **Open Voice Operating System** - Voice assistant platform
4. **LocalAI** - Local AI inference server
5. **JetsonGPT** - NVIDIA Jetson AI applications
6. **Lernstick EDU/EXAM** - Educational software with language detection
7. **Basic TTS** - Online text-to-speech converter

### Target Applications
- Accessibility tools for visually impaired users
- Voice assistants and smart home systems
- Educational software with multilingual support
- Embedded systems with limited resources
- Privacy-focused applications requiring offline TTS
- Content creation and narration tools

## Development & Maintenance

### Current Status
- **Active Development:** Looking for maintainers (contact: voice@openhomefoundation.org)
- **Latest Release:** v1.4.1 (December 2024)
- **Repository:** https://github.com/OHF-Voice/piper1-gpl

### Recent Changes (v1.4.x)
- Added Chinese phonemizer based on g2pW
- Support for direct IPA phoneme input
- Vocoder warmstart checkpoint support
- Pre-generated phoneme ID training
- Experimental alignment support
- Embedded espeak-ng (removed separate piper-phonemize library)
- Changed to GPLv3 license
- Python stable ABI support (single wheel per platform)

### Build System
- **CMake** for C/C++ components
- **scikit-build** for Python/C++ integration
- **GitHub Actions** for CI/CD
- **Docker** support for containerized deployment

### Testing
- Unit tests with pytest
- Test coverage for phonemizers
- Voice model testing
- Integration tests

## Configuration Options

### Synthesis Parameters
- `speaker_id`: Speaker selection for multi-speaker voices
- `length_scale`: Speech speed (< 1 faster, > 1 slower)
- `noise_scale`: Audio variation amount
- `noise_w_scale`: Phoneme width variation
- `normalize_audio`: Audio normalization toggle
- `volume`: Output volume multiplier

### Voice Model Configuration
- `num_symbols`: Number of phonemes
- `num_speakers`: Number of speakers
- `sample_rate`: Output audio sample rate
- `espeak_voice`: espeak-ng voice/alphabet
- `phoneme_id_map`: Phoneme to ID mapping
- `phoneme_type`: Phonemization method
- `hop_length`: Audio hop length (default: 256)

## Supported Languages

Piper supports multiple languages through espeak-ng, including:
- English (multiple variants)
- Spanish
- French
- German
- Italian
- Chinese (with g2pW)
- Arabic (with Tashkeel diacritization)
- And many more via espeak-ng

## Performance Characteristics

### Advantages
- **Fast inference:** Optimized ONNX models
- **Low latency:** Local processing without network calls
- **Small footprint:** Efficient model sizes
- **CPU-friendly:** Runs on modest hardware
- **GPU-ready:** Optional CUDA acceleration

### Considerations
- Model loading time on CLI (use HTTP server for repeated use)
- Memory usage scales with model size
- Quality depends on voice model training

## Security & Privacy

### Privacy Benefits
- **Fully offline:** No data sent to external servers
- **Local processing:** All synthesis happens on-device
- **No telemetry:** No usage tracking or analytics

### Security Considerations
- GPL-3.0 license requires source disclosure for modifications
- ONNX models should be obtained from trusted sources
- HTTP server should be secured if exposed to network

## Future Development

### Planned Features (from PLANS.md)
- Improved alignment support
- Additional language support
- Performance optimizations
- Enhanced training pipeline
- Better documentation

### Community Involvement
- Open to contributions
- Actively seeking maintainers
- Community-driven voice creation
- Integration with other open-source projects

## Documentation

### Available Documentation
- `CLI.md` - Command-line interface guide
- `API_PYTHON.md` - Python API reference
- `API_HTTP.md` - HTTP server documentation
- `TRAINING.md` - Voice training guide
- `BUILDING.md` - Build instructions
- `VOICES.md` - Voice catalog
- `ALIGNMENTS.md` - Alignment feature documentation

## Comparison with Alternatives

### Advantages over Cloud TTS
- No API costs
- Complete privacy
- No internet dependency
- Consistent availability
- Predictable latency

### Advantages over Other Local TTS
- High-quality neural voices
- Active community
- Multiple interface options
- Extensive language support
- Training pipeline included

## Conclusion

Piper is a mature, production-ready text-to-speech engine that prioritizes privacy, performance, and accessibility. Its modular architecture, comprehensive API options, and active community make it suitable for a wide range of applications from embedded systems to enterprise software. The project's commitment to open-source development and local processing aligns with modern privacy concerns while delivering high-quality neural voice synthesis.

### Strengths
✅ Fast and efficient local processing  
✅ Multiple API interfaces (CLI, Python, HTTP, C/C++)  
✅ Extensive language support  
✅ Active community and real-world adoption  
✅ Complete training pipeline  
✅ Privacy-focused design  
✅ GPU acceleration support  

### Areas for Improvement
⚠️ Seeking active maintainers  
⚠️ CLI model loading overhead  
⚠️ Documentation could be more comprehensive  
⚠️ Limited built-in voice customization options  

### Recommendation
Piper is highly recommended for projects requiring high-quality, privacy-preserving text-to-speech capabilities. It's particularly well-suited for accessibility applications, voice assistants, and any scenario where offline operation is essential.

---

**Generated:** 2024  
**Project Repository:** https://github.com/OHF-Voice/piper1-gpl  
**License:** GPL-3.0-or-later  
**Maintainer Contact:** voice@openhomefoundation.org
