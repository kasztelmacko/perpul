from fastapi import FastAPI, Request, UploadFile, File, HTTPException, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import  JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from PIL import Image
import io
import os
import asyncio
import uuid
from aioredis import Redis, from_url
from app.database import supabase, save_image, save_entry, remove_image
from app.pokolorach.process_image import process_image

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = from_url("redis://localhost", encoding="utf-8", decode_responses=True)

@app.get("/")
async def main():
    img_url = await redis.get("image_url")
    return {"img_url": img_url}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        file_contents = await file.read()
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        response, image_url = save_image(
            storage_path="input_image", 
            file_contents=file_contents, 
            filename=unique_filename,
            file_options={"content-type": file.content_type}
        )

        new_image_data = {
            "img_name": unique_filename,
            "img_url": image_url,
            "img_cluster_url": None,
            "img_outline_url": None,
            "img_type": None
        }

        response, entry_id = save_entry(table_name="Entries", data=new_image_data)

        await redis.set("image_url", image_url)
        await redis.set("filename", unique_filename)
        await redis.set("entry_id", entry_id)
        await redis.set("content_type", file.content_type)

        return JSONResponse(content={
            "status": "complete",
            "image_url": image_url
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        await file.close()

@app.post("/process")
async def process():
    try:
        image_url = await redis.get("image_url")
        filename = await redis.get("filename")
        entry_id = await redis.get("entry_id")
        content_type = await redis.get("content_type")

        if not image_url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

        img_cluster_url, img_outline_url, label_color_mapping = process_image(
            file_name=filename,
            entry_id=entry_id,
            file_options={"content-type": content_type},
            image_url=image_url,
            n_clusters=20,
            blur_radius=1
        )

        await redis.set("label_color_mapping", str(label_color_mapping))

        asyncio.create_task(remove_image("cluster_image", filename))
        asyncio.create_task(remove_image("outline_image", filename))

        return JSONResponse(content={
            "status": "complete",
            "img_cluster_url": img_cluster_url,
            "img_outline_url": img_outline_url
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/get-featured-image")
async def get_featured_image(url: str = Query(..., description="URL of the image")):
    return {"url": url}

@app.get("/generate_palette")
async def generate_palette():
    try:
        label_color_mapping_str = await redis.get("label_color_mapping")
        if not label_color_mapping_str:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Palette not found")

        label_color_mapping = eval(label_color_mapping_str)

        return label_color_mapping
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
