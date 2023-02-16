import asyncio 
import logging

from aiogram import Bot, types, Dispatcher, executor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


API_TOKEN = '1002924058:AAFEvNjkO57Iv4KpD7cnovTsiRcSorG6b_s'
CHAT_ID = '352251491'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start_watchdog'])
async def start_cmd(message: types.Message):
    await message.reply("Start watchdog")


async def on_startup(_):
    w = Watcher()
    loop = asyncio.get_running_loop()
    loop.create_task(w.run(loop))


async def some_async_handler(event):
    if event.is_directory:
        return None

    elif event.event_type == 'created':
        message = f"Файл {event.src_path} был создан!"
        await bot.send_message(chat_id=CHAT_ID, text=message)
        print(f"Файл {event.src_path} был создан!")
    elif event.event_type == "deleted":
        message = f"Файл {event.src_path} был удалён!"
        await bot.send_message(chat_id=CHAT_ID, text=message)
        print(f"Файл {event.src_path} был удален!")


class Watcher:
    DIRECTORY_TO_WATCH = './test/'

    def __init__(self):
        self.observer = Observer()

    async def run(self, loop):
        event_handler = Handler(loop)

        self.observer.schedule(event_handler=event_handler, path=self.DIRECTORY_TO_WATCH, 
                               recursive=True)
        self.observer.start()
        try:
            while True:
                await asyncio.sleep(5)
        except Exception as e:
            self.observer.stop()
            logging.critical("STOP LOOP!", exc_info=e)

        self.observer.join()

    async def stop(self):
        return self.observer.stop()


class Handler(FileSystemEventHandler):
    def __init__(self, loop, *args, **kwargs):
        self._loop = loop
        super().__init__(*args, **kwargs)

    def on_any_event(self, event):
        asyncio.run_coroutine_threadsafe(some_async_handler(event), self._loop)


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    except Exception as e:
        logging.critical("Ошибка стоп 0000000x0", exc_info=e)

