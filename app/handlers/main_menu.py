import asyncio
from dataclasses import dataclass

from aiogram import types
from aiogram.types import ParseMode

from app.create_bot import dp
from app.utils.checker import Checker, Capsolver


@dataclass
class Data:
    SITE_KEY = '6Lcx3V0oAAAAAJAXMNNDvwhIZI0wnZuM7-YjIIRx'
    SITE_URL = 'https://genesis.celestia.org/'
    API_KEY = 'CAI-7699A545ACF1F18264C9F1BAE7E102FB'


@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    await message.answer("<b> Enter a wallet or list of wallets each with a new line (20 max at a time)</b>", parse_mode=types.ParseMode.HTML)


@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_wallets(message: types.Message):
    max_wallet = 10
    wallets = message.text.split("\n")[:max_wallet]
    results = []

    for wallet in wallets:
        await asyncio.sleep(1)
        if len(wallet) != 42:
            results.append(f"<b> {wallet} </b> <u> Invalid wallet address </u>\n")
            continue
        captcha_solver = Capsolver(Data.API_KEY, Data.SITE_URL, Data.SITE_KEY, page_action='submit')
        checker = Checker(captcha_solver)
        result = await checker.check(wallet=wallet)

        results.append(f"<b> {wallet} </b> {result}\n")

    await message.answer("\n".join(results), parse_mode=ParseMode.HTML)