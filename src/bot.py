import os
import asyncio
import joblib
import pandas as pd
import logging
from dotenv import load_dotenv  
from dotenv import load_dotenv   
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, URLInputFile
from aiogram.client.session.aiohttp import AiohttpSession


# подгружаем сохраненные "мозги" нашей модели и список фичей
model = joblib.load("data/models/rf_model.pkl")
features = joblib.load("data/models/features.pkl")

load_dotenv() 

BOT_TOKEN = os.getenv("BOT_TOKEN")


if os.environ.get('PYTHONANYWHERE_DOMAIN'):
    print("Запуск на сервере: включаю прокси")
    session = AiohttpSession(proxy="http://proxy.server:3128")
    bot = Bot(token=BOT_TOKEN, session=session)
else:
    print("Запуск локально: работаю без прокси")
    bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()



main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Сделать прогноз")],
        [KeyboardButton(text="ℹ️ Как это работает?")]
    ],
    resize_keyboard=True, # кнопки будут аккуратного размера
    input_field_placeholder="Выбери действие..."
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    image_url = "https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=1000&auto=format&fit=crop"
    photo = URLInputFile(image_url)
    
    text = (
        "👋 <b>Добро пожаловать в Steam Indie Predictor!</b>\n\n"
        "Этот бот прогнозирует коммерческий успех инди-игр на основе машинного обучения. "
        "Математическая модель проанализировала тысячи реальных релизов в Steam и оценивает "
        "перспективы вашей идеи по выбранным жанрам и тегам.\n\n"
        "Нажмите кнопку ниже, чтобы запустить расчет прогноза 👇"
    )
    await message.answer_photo(photo=photo, caption=text, parse_mode="HTML", reply_markup=main_kb)

@dp.message(F.text == "ℹ️ Как это работает?")
async def about_project(message: types.Message):
    text = (
        "🧠 <b>Под капотом:</b>\n\n"
        "Модель машинного обучения (Random Forest) обучена на исторических данных магазина Steam.\n"
        "Она учитывает жанр, цену и год релиза, находя скрытые паттерны успеха среди тысяч выпущенных проектов.\n\n"
        "<i>Отличный инструмент для проверки концепта перед началом разработки!</i>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "🚀 Сделать прогноз")
async def ask_for_data(message: types.Message):
    text = (
        "Отправь мне данные будущей игры через пробел в формате:\n"
        "<b>[Цена в $] [Год выхода] [Главный жанр]</b>\n\n"
        "📝 <i>Примеры:</i>\n"
        "<code>15 2026 Action</code>\n"
        "<code>20 2027 RPG</code>\n"
        "<code>0 2026 Casual</code>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message()
async def predict_game(message: types.Message):
    try:
        if " " not in message.text:
            return
            
        parts = message.text.strip().split()
        if len(parts) != 3:
            raise ValueError("нужно ровно 3 параметра")
            
        price = float(parts[0])
        year = int(parts[1])
        genre = parts[2]
        
        df = pd.DataFrame(0, index=[0], columns=features)
        df['price_clean'] = price
        df['release_year'] = year
        
        if genre in df.columns:
            df[genre] = 1
            
        pred = model.predict(df)[0]
        
        if pred == 1:
            result_text = (
                "✅ <b>ВЕРДИКТ: УСПЕХ (ХИТ)</b>\n\n"
                "📈 Алгоритм видит высокий потенциал. Аудитория Steam хорошо принимает такие проекты по этой цене. "
                "Можно смело питчить инвесторам!"
            )
        else:
            result_text = (
                "❌ <b>ВЕРДИКТ: ВЫСОКИЙ РИСК</b>\n\n"
                "📉 Исторически игры с такими параметрами часто проваливаются. "
                "Рекомендуется пересмотреть ценовую политику или сменить жанровый фокус."
            )
            
        await message.reply(result_text, parse_mode="HTML")
            
    except Exception as e:
        await message.reply("⚠️ Ошибка формата. Пожалуйста, нажми «🚀 Сделать прогноз» и следуй инструкции.")

async def main():
    print("Бот с новым UI запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
