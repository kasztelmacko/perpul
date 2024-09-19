from supabase import Client, create_client
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

def save_image(storage_path: str, file_contents, filename: str, file_options: dict):
    path_on_supastorage = f"{storage_path}/{filename}"
    response = supabase.storage.from_(storage_path).upload(
        path=path_on_supastorage,
        file=file_contents,
        file_options=file_options
    )
    image_url = supabase.storage.from_(storage_path).create_signed_url(
        path_on_supastorage,
        expires_in=60)["signedURL"]
    
    return response, image_url


def save_entry(table_name: str, data: dict):
    response = supabase.table(table_name).insert(data).execute()
    entry_id = response.data[0]["id"]
    return response, entry_id


def update_image_entry(table_name: str, image_url: str, entry_id: int, column: str):
    response = supabase.table(table_name).update({f"{column}": image_url}).eq("id", entry_id).execute()
    return response


async def remove_image(storage_path: str, file_name: str, delay: int = 300):
    await asyncio.sleep(delay)
    response = supabase.storage.from_(storage_path).remove([f"{storage_path}/{file_name}"])
    return response

def get_entry(table_name: str, entry_id: int, column: str):
    response = supabase.table(table_name).select(column).eq("id", entry_id).execute()
    return response.data[0][column]


