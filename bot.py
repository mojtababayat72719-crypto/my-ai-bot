import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from google import genai

# توکن ربات تلگرام که از BotFather گرفتی
TELEGRAM_TOKEN = "8897289456:AAEWIWBwlJl3kr-Xo-gFQ5ojf16mRGn3cxw"
# کلید API که از Google AI Studio گرفتی
GEMINI_API_KEY = "AQ.Ab8RN6I7khBFgy3RpI7tJCl2icTv1lCyp4xYD8RZvX9XmpqdaA"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

user_credits = {}

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_credits:
        user_credits[user_id] = 5
        
    await message.answer(
        f"سلام! ربات هوش مصنوعی شما روشن و آماده است.\n"
        f"شما {user_credits[user_id]} سکه رایگان دارید.\n\n"
        f"برای سوال پرسیدن بفرستید:\n/ai [متن شما]"
    )

@dp.message(Command("ai"))
async def ask_gemini(message: types.Message):
    user_id = message.from_user.id
    
    if user_credits.get(user_id, 0) <= 0:
        await message.answer("⚠️ سکه‌های شما تمام شده است!")
        return

    prompt = message.text.replace("/ai", "", 1).strip()
    if not prompt:
        await message.answer("لطفاً متنی بعد از /ai بنویسید.")
        return

    waiting_msg = await message.answer("⏳ در حال پردازش...")

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        user_credits[user_id] -= 1
        final_text = f"{response.text}\n\n─────────────\n🪙 سکه باقیمانده: {user_credits[user_id]}"
        await bot.edit_message_text(final_text, chat_id=message.chat.id, message_id=waiting_msg.message_id)
    except Exception as e:
        await bot.edit_message_text("❌ خطایی رخ داد.", chat_id=message.chat.id, message_id=waiting_msg.message_id)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
