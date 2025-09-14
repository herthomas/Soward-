from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

@router.get("/transcripts/{transcript_unique_id}")
async def get_transcript(transcript_unique_id: str):
    file_path = os.path.join("transcripts", transcript_unique_id)
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    raise HTTPException(status_code=404, detail="Transcript not found")