from PIL import Image
import io
from aiogram import Bot
from aiogram.types import PhotoSize


async def convert_image_to_webp(bot: Bot, photo: PhotoSize):
    file_info = await bot.get_file(photo.file_id)
    file = await bot.download_file(file_path=file_info.file_path)

    photo_image = Image.open(io.BytesIO(file.read()))
    output_buffer = io.BytesIO()
    photo_image.save(output_buffer, format="WEBP")
    webp_image_bytes = output_buffer.getvalue()
    output_buffer.close()
    return webp_image_bytes
