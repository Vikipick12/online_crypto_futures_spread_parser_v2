from dotenv import load_dotenv
import os
import asyncio
from aiogram import Dispatcher, Bot
from aiogram.filters import Command
from aiogram.types import Message
import config
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import json
from parser import filter_opportunities
from time import strftime
from main import main as parser_v1

print("Starting Telegram bot...")
if os.path.exists(".env"):
    print("Loading environment variables from .env file")
    load_dotenv()

print(os.getenv("TG_access_token_2"))
print(os.getenv("tg_admin_id"))
    
TG_TOKEN = os.getenv("TG_access_token_2")
TG_USER_ID = int(os.getenv("tg_admin_id"))
dp = Dispatcher()

class SpreadState(StatesGroup):
    waiting_for_spread = State()

def write_spread(spread: float):
    min_spread_data = {"spread_threshold": spread}
    with open(config.spread_threshold_config_file, "w") as f:
        json.dump(min_spread_data, f)

@dp.message(Command("set_spread"))
async def command_set_spread(message: Message, state: FSMContext):
    await message.answer("Введи нове значення спреду у % (наприклад: '3.5', '5')")
    await state.set_state(SpreadState.waiting_for_spread)

@dp.message()
async def process_set_spread(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == SpreadState.waiting_for_spread.state:
        try:
            new_spread = float(message.text.replace(",", "."))
            if new_spread <= 0:
                await message.answer("Спред не може бути від'ємний або дорінювати нулю")
                return None
            write_spread(new_spread)
            await message.answer(f"Спред змінено.\nНовий спред: {new_spread:.2f}%")
            await state.clear()
        except ValueError:
            await message.reply("Неправильний формат числа, спробуй ще раз")


def read_opps():
    try:
        with open(config.arbitrage_opportunities_file, "r") as f:
            spread_opportunities = json.load(f)
    except Exception as e:
        spread_opportunities = []
    return spread_opportunities


def compile_messages():
    filter_opportunities()
    messages = []
    opportunities = read_opps()
    for opp in opportunities:
        try:
            message = (
                f"<code>{opp['ticker']}</code>\n"
                f"Long: <i>{opp['long']}</i>\n"
                f"Short: <i>{opp['short']}</i>\n"
                f"Spread: <b>{opp['spread']:.2f}%</b>\n"
                f"Об'єм на {opp['long']}: <code>{opp[f'{opp['long']}_volume'] / 1000000:.2f}m$</code>\n"
                f"Об'єм на {opp['short']}: <code>{opp[f'{opp['short']}_volume'] / 1000000:.2f}m$</code>"
                )
            messages.append(message)
        except KeyError:
            continue
    return messages


async def write_new_opp(bot: Bot):
    while True:
        try:
            messages = compile_messages()
            for msg in messages:
                await bot.send_message(chat_id=TG_USER_ID, text=msg, parse_mode="HTML")
        except Exception as e:
            print(strftime("%b %d%H:%M:%S"))
            print(f"Помилка з write_new_opp(): {e}")
        await asyncio.sleep(15)


async def main():
    bot = Bot(TG_TOKEN)

    asyncio.create_task(write_new_opp(bot))
    asyncio.create_task(parser_v1(3))

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
