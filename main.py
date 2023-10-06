import asyncio
import base64
import hashlib
import json
import uuid

import aiohttp
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

import settings

dp = Dispatcher()


async def make_request(url: str, invoice_data: dict):
    encoded_data = base64.b64encode(
        json.dumps(invoice_data).encode("utf-8")
    ).decode("utf-8")
    signature = hashlib.md5(f"{encoded_data}{settings.CRYPTOMUS_API_KEY}".
                            encode("utf-8")).hexdigest()

    async with aiohttp.ClientSession(headers={
        "merchant": settings.CRYPTOMUS_MERCHANT_ID,
        "sign": signature,
    }) as session:
        async with session.post(url=url, json=invoice_data) as response:
            if not response.ok:
                raise ValueError(response.reason)

            return await response.json()


async def check_invoice_paid(id: str, message):
    while True:
        invoice_data = await make_request(
            url="https://api.cryptomus.com/v1/payment/info",
            invoice_data={"uuid": id},
        )

        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            await message.answer("The invoice is paid! Thank you!")
            return
        else:
            print("Invoice is not paid for yet")

        await asyncio.sleep(10)


@dp.message(CommandStart())
async def buy_handler(message: Message):
    invoice_data = await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": "0.5",
            "currency": "USD",
            "order_id": str(uuid.uuid4())
        },
    )

    asyncio.create_task(
        check_invoice_paid(invoice_data['result']['uuid'],
                           message=message))

    await message.answer(f"Ваш инвойс: {invoice_data['result']['url']}")


if __name__ == '__main__':
    bot = Bot(settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    asyncio.run(dp.start_polling(bot))
