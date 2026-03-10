import os
import json
from pathlib import Path

class VoiceManager:
    def __init__(self):
        self.models_dir = Path("/app/models")
        self.models_dir.mkdir(exist_ok=True)
    
    def list_voices(self):
        voices = []
        for onnx_file in self.models_dir.glob("*.onnx"):
            config_file = onnx_file.with_suffix(".onnx.json")
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
                voices.append({
                    "name": onnx_file.stem,
                    "language": config.get("language", {}).get("code", "unknown"),
                    "model_path": str(onnx_file),
                    "config_path": str(config_file)
                })
        return voices
    
    def upload_voice(self, name: str, model_data: bytes, config_data: bytes):
        model_path = self.models_dir / f"{name}.onnx"
        config_path = self.models_dir / f"{name}.onnx.json"
        
        with open(model_path, "wb") as f:
            f.write(model_data)
        
        with open(config_path, "wb") as f:
            f.write(config_data)
        
        return str(model_path)
    
    def delete_voice(self, name: str):
        model_path = self.models_dir / f"{name}.onnx"
        config_path = self.models_dir / f"{name}.onnx.json"
        
        if model_path.exists():
            model_path.unlink()
        if config_path.exists():
            config_path.unlink()