from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from downloader import parse_deck
from pathlib import Path
import shutil
import uuid
import os

from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/create_session/")
def create_session() -> str:
    session_id = uuid.uuid4()
    os.makedirs(f"data/{session_id}", exist_ok=True)
    return str(session_id)


class DeckSubmission(BaseModel):
    deck: str
    session_id: str


@app.post("/submit_deck/")
async def submit_deck(sub: DeckSubmission) -> list[str]:
    return parse_deck(sub.deck, sub.session_id)


@app.get("/images/{session_id}")
async def get_session_images(session_id: str) -> list[str]:
    session_dir = Path(f"data/{session_id}")
    if not session_dir.exists():
        return []
    
    image_files = []
    for root, dirs, files in os.walk(session_dir):
        for file in files:
            if file.endswith("_small.jpg"):
                # Get relative path from session_dir
                rel_path = os.path.relpath(os.path.join(root, file), session_dir)
                image_files.append(rel_path)
    
    return sorted(image_files)


@app.get("/image/{session_id}/{set_name}/{filename}")
async def get_image(session_id: str, set_name: str, filename: str):
    image_path = Path(f"data/{session_id}/{set_name}/{filename}")
    if not image_path.exists():
        return {"error": "Image not found"}
    
    return FileResponse(path=image_path, media_type="image/jpeg")


@app.get("/download/{session_id}")
async def download_images(session_id: str):
    session_dir = Path(f"data/{session_id}")
    if not session_dir.exists():
        return {"error": "Session not found"}

    # Create a temporary directory for the zip contents
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Copy card images
        for item in session_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, temp_path / item.name)
        
        # Copy the install script
        script_path = Path("copy-to-optcgsim.sh")
        if script_path.exists():
            shutil.copy(script_path, temp_path / "copy-to-optcgsim.sh")
        
        # Create zip archive
        zip_path = shutil.make_archive(f"data/{session_id}", "zip", temp_path)
    
    return FileResponse(
        path=zip_path, filename=f"{session_id}.zip", media_type="application/zip"
    )
