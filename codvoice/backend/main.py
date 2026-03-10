from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
from api.tts_routes import router as tts_router
from api.admin_routes import router as admin_router
from api.voice_routes import router as voice_router
from services.auth_service import get_api_key

app = FastAPI(title="CODVOICE API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts_router, prefix="/tts", dependencies=[Depends(get_api_key)])
app.include_router(admin_router, prefix="/admin")
app.include_router(voice_router, prefix="/voices")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "codvoice-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)