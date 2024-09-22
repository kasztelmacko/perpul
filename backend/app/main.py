from fastapi import FastAPI, Request, UploadFile, File, HTTPException, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import  JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from PIL import Image
import numpy as np
import io
import os
import json
import asyncio
import uuid
import logging
import traceback
from aioredis import Redis, from_url
from app.database import supabase, save_image, save_entry, remove_image
from app.pokolorach.process_image import process_image

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.56.1:3000"],
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
            "image_url": image_url,
            "unique_filename": unique_filename
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

        def serialize_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

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

        asyncio.create_task(remove_image("cluster_image", filename))
        asyncio.create_task(remove_image("outline_image", filename))

        serializable_mapping = {str(k): [serialize_numpy(i) for i in v] for k, v in label_color_mapping.items()}


        response_data = {
            "status": "complete",
            "img_cluster_url": img_cluster_url,
            "img_outline_url": img_outline_url,
            "label_color_mapping": serializable_mapping
        }

        json_data = json.dumps(response_data)

        return JSONResponse(content=json.loads(json_data))
    except json.JSONDecodeError as json_error:
        logging.error(f"JSON serialization error: {str(json_error)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"JSON serialization error: {str(json_error)}")
    except Exception as e:
        logging.error(f"Error in /process: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    

@app.get("/painting/{unique_filename}")
async def get_painting(unique_filename: str):
    try:
        image_url = await redis.get("image_url")
        filename = await redis.get("filename")

        if not image_url or not filename:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Painting data not found in Redis")

        stored_filename_without_ext = filename.rsplit('.', 1)[0]

        if stored_filename_without_ext != unique_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Filename mismatch. Stored: {stored_filename_without_ext}, Requested: {unique_filename}"
            )

        painting_data = {
            "img_url": image_url,
            "img_name": filename,
        }
        return painting_data
    except HTTPException as he:
        print(f"HTTPException in get_painting: {he.detail}")
        raise he
    except Exception as e:
        print(f"Unexpected error in get_painting: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


