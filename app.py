#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from enum import Enum
import os
import tempfile
import uvicorn
from downloader import WebpbnDownloader, NonogramsOrgDownloader

app = FastAPI(
    title="Nonogram Downloader API",
    description="API for downloading nonogram puzzles from webpbn.com and nonograms.org in NON or XML format",
    version="1.0.0"
)

# Define enums for puzzle sources and formats
class PuzzleSource(str, Enum):
    WEBPBN = "webpbn"
    NONOGRAMS_ORG = "nonograms_org"

class PuzzleFormat(str, Enum):
    NON = "non"
    XML = "xml"

# Use a temporary directory for downloads
TEMP_DIR = tempfile.mkdtemp()
webpbn_downloader = WebpbnDownloader(output_dir=TEMP_DIR)
nonograms_org_downloader = NonogramsOrgDownloader(output_dir=TEMP_DIR)

@app.get("/hello")
async def read_hello():
    return {"message": "Hello Test"}

@app.get("/")
def read_root():
    return {
        "message": "Nonogram Downloader API", 
        "endpoints": [
            "/download/{puzzle_id}",
            "/puzzle/{puzzle_id}/content"
        ],
        "sources": [
            "webpbn",
            "nonograms_org"
        ],
        "formats": [
            "non",
            "xml"
        ]
    }

@app.get("/download/{puzzle_id}")
def download_puzzle(
    puzzle_id: int,
    source: PuzzleSource = Query(PuzzleSource.WEBPBN, description="Source of the puzzle"),
    format: PuzzleFormat = Query(PuzzleFormat.NON, description="Format of the puzzle (NON or XML)"),
    include_solution: bool = Query(False, description="Whether to include the intended solution")
):
    """
    Download a nonogram puzzle in the specified format and return it as a file.
    """
    try:
        # Select the appropriate downloader based on source
        if source == PuzzleSource.WEBPBN:
            downloader = webpbn_downloader
            source_name = "webpbn.com"
        else:
            downloader = nonograms_org_downloader
            source_name = "nonograms.org"
            
        # Download in the specified format
        file_path = downloader.download(puzzle_id, include_solution, format=format.value)
        if not file_path:
            raise HTTPException(status_code=404, detail=f"Failed to download puzzle {puzzle_id} from {source_name}")
        
        return FileResponse(
            path=file_path, 
            media_type='application/octet-stream',
            filename=f"nonogram-{source}-{puzzle_id}.{format.value}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/puzzle/{puzzle_id}/content")
def get_puzzle_content(
    puzzle_id: int,
    source: PuzzleSource = Query(PuzzleSource.WEBPBN, description="Source of the puzzle"),
    format: PuzzleFormat = Query(PuzzleFormat.NON, description="Format of the puzzle (NON or XML)"),
    include_solution: bool = Query(False, description="Whether to include the intended solution")
):
    """
    Download a nonogram puzzle in the specified format and return it as text content.
    """
    try:
        # Select the appropriate downloader based on source
        if source == PuzzleSource.WEBPBN:
            downloader = webpbn_downloader
            source_name = "webpbn.com"
        else:
            downloader = nonograms_org_downloader
            source_name = "nonograms.org"
            
        # Download in the specified format
        file_path = downloader.download(puzzle_id, include_solution, format=format.value)
        if not file_path:
            raise HTTPException(status_code=404, detail=f"Failed to download puzzle {puzzle_id} from {source_name}")
          # Read file in correct mode based on format
        if format == PuzzleFormat.NON:
            with open(file_path, 'rb') as f:
                content = f.read()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Set appropriate content type based on format
        media_type = "application/xml" if format == PuzzleFormat.XML else "application/octet-stream"
        return Response(content=content, media_type=media_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
