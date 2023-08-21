import os
import re
from aiogram import Bot, Dispatcher, types, executor
from pytube import YouTube
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage

Token = 'Ваш токен'

storage = MemoryStorage()
bot = Bot(token=Token)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

class DownloadState(StatesGroup):
    waiting_for_url = State()

@dp.message_handler(commands=["start"])
async def start_download(message: types.Message, state: FSMContext):
    await message.answer("Введите URL видео на YouTube для скачивания:")
    await DownloadState.waiting_for_url.set()


@dp.message_handler(state=DownloadState.waiting_for_url)
async def process_video_url(message: types.Message, state: FSMContext):
    video_url = message.text
    try:
        video_info = YouTube(video_url)
        video_title = re.sub(r'[/:"*?<>|]', '_', video_info.title)

        os.makedirs(os.path.join(os.path.dirname(__file__), "videos"), exist_ok=True)

        video_file_name = f"{video_title}.mp4"
        video_file_path = os.path.join(os.path.dirname(__file__), "videos", video_file_name)
        print("Скачивание видео...")
        video_stream = video_info.streams.get_highest_resolution()
        video_stream.download(output_path=os.path.join(os.path.dirname(__file__), "videos"), filename=video_file_name)
        print("Скачивание завершено.")

        print("Отправка видео...")
        with open(video_file_path, 'rb') as video_file:
            await bot.send_video(message.chat.id, video=video_file)
        print("Отправка завершена.")

        await message.answer("Видео успешно отправлено!")

    except Exception as e:
        print("Ошибка при скачивании и отправке видео:", e)
        await message.answer("Ошибка при скачивании и отправке видео. Пожалуйста, убедитесь, что URL корректен.")

    await state.finish()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)