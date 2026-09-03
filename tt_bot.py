import asyncio, logging, time, re, io
from gtts import gTTS
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

# 👇 APNA TOKEN YAHAN DAALEIN
BOT_TOKEN = "8312683277:AAG_xJ3TXbAi9y9xlYkNwa1rLghBoWiDSE4"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.callback_query.middleware(CallbackAnswerMiddleware())

user_last_used = {}
# User ki speed save karne ke liye dictionary
user_speed = {}  # Default: Normal

burmese_pattern = re.compile(r'[\u1000-\u109F\uAA60-\uAA7F\u102B-\u103F]+')

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Channel Join wala check hata diya hai, ab seedha menu aayega
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎙️ Generate TTS", callback_data="gen_tts")],
        [InlineKeyboardButton(text="⚙️ Settings & Speed", callback_data="open_settings")],
        [InlineKeyboardButton(text="📖 Help", callback_data="open_help")],
        [InlineKeyboardButton(text="ℹ️ About", callback_data="open_about")]
    ])
    await message.answer("<b>🌟 Premium TTS Bot 🌟</b>\n\nWelcome! I convert <b>Burmese text</b> into high-quality audio.\n\n<i>Select an option below:</i>", parse_mode=ParseMode.HTML, reply_markup=kb)

@router.callback_query(F.data == "gen_tts")
async def gen_tts(call: CallbackQuery):
    await call.message.answer("✅ <b>Ready!</b>\n\nPlease send me any <b>Burmese text</b>, and I will convert it to voice.", parse_mode=ParseMode.HTML)

@router.callback_query(F.data == "open_settings")
async def open_settings(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐢 Slow Speed", callback_data="speed_slow")],
        [InlineKeyboardButton(text="🚀 Normal Speed", callback_data="speed_normal")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])
    await call.message.answer("⚙️ <b>Choose your Voice Speed:</b>", parse_mode=ParseMode.HTML, reply_markup=kb)

@router.callback_query(F.data.in_(["speed_slow", "speed_normal", "back_main"]))
async def handle_speed(call: CallbackQuery):
    user_id = call.from_user.id
    
    if call.data == "speed_slow":
        user_speed[user_id] = True
        await call.message.answer("✅ <b>Speed set to Slow!</b>", parse_mode=ParseMode.HTML)
    elif call.data == "speed_normal":
        user_speed[user_id] = False
        await call.message.answer("✅ <b>Speed set to Normal!</b>", parse_mode=ParseMode.HTML)
    elif call.data == "back_main":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎙️ Generate TTS", callback_data="gen_tts")],
            [InlineKeyboardButton(text="⚙️ Settings & Speed", callback_data="open_settings")],
            [InlineKeyboardButton(text="📖 Help", callback_data="open_help")]
        ])
        await call.message.edit_text("<b>Main Menu</b>", parse_mode=ParseMode.HTML, reply_markup=kb)
    await call.answer()

@router.callback_query(F.data == "open_help")
async def help(call: CallbackQuery):
    await call.message.answer("📖 <b>Help Guide</b>\n\n1. Tap on <b>Generate TTS</b>.\n2. Send me <b>Burmese text</b>.\n3. I will instantly generate and send the audio file.\n4. Use <b>Settings & Speed</b> to change voice speed.\n\n<i>Example:</i> မင်္ဂလာပါ", parse_mode=ParseMode.HTML)

@router.callback_query(F.data == "open_about")
async def about(call: CallbackQuery):
    await call.message.answer("ℹ️ <b>About This Bot</b>\n\nPremium Burmese Text-to-Speech Engine.\nVersion: <b>3.0</b>\nPowered by <b>Google TTS (gTTS)</b> 🚀", parse_mode=ParseMode.HTML)

@router.message(F.text)
async def generate_tts(message: Message):
    text = message.text

    if not burmese_pattern.search(text):
        await message.answer("❌ <b>Error:</b> I only accept <b>Burmese text</b>. Please enter Myanmar script.", parse_mode=ParseMode.HTML)
        return

    # Anti-Spam Logic
    user_id = message.from_user.id
    current_time = time.time()
    if user_id in user_last_used and current_time - user_last_used[user_id] < 5:
        await message.answer("⏳ <b>Please wait 5 seconds before sending another request!</b>", parse_mode=ParseMode.HTML)
        return
    user_last_used[user_id] = current_time

    # Speed Check
    is_slow = user_speed.get(user_id, False) # Normal by default

    await message.answer("🎧 <b>Generating your Burmese audio...</b>", parse_mode=ParseMode.HTML)
    
    try:
        # Google TTS with speed option
        tts = gTTS(text=text, lang='my', slow=is_slow)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        input_file = BufferedInputFile(audio_buffer.read(), filename="burmese.mp3")
        await message.answer_audio(input_file, caption="✅ <b>Here is your audio!</b>", parse_mode=ParseMode.HTML)
            
    except Exception as e:
        await message.answer(f"❌ <b>Error:</b> {str(e)}", parse_mode=ParseMode.HTML)

dp.include_router(router)
async def main():
    print("Premium Burmese Bot with Speed Options is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
