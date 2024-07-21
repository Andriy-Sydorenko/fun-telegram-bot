from PIL import Image
import io
from aiogram import Bot
from aiogram import types


async def convert_image_to_webp(bot: Bot, photo: types.PhotoSize) -> bytes:
    file_info = await bot.get_file(photo.file_id)
    file = await bot.download_file(file_path=file_info.file_path)

    photo_image = Image.open(io.BytesIO(file.read()))
    output_buffer = io.BytesIO()
    photo_image.save(output_buffer, format="WEBP")
    webp_image_bytes = output_buffer.getvalue()
    output_buffer.close()
    return webp_image_bytes


def escape_markdown_v2(text: str) -> str:
    escape_chars = "_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


def mention_user_without_username(user: types.user.User) -> str:
    return f"[{user.first_name}](tg://user?id={user.id})"
