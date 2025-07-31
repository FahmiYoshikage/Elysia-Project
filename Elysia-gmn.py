import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import datetime # Import modul datetime untuk tanggal dan waktu

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Validasi API Keys dan Konfigurasi Gemini ---
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables. Please set it in a .env file.")
if not BOT_USERNAME:
    raise ValueError("BOT_USERNAME not found in environment variables. Please set it in a .env file (e.g., @MyElysia_Bot).")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in a .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

# --- FUNGSI BARU: Mendapatkan Jadwal Mata Kuliah ---
def get_today_schedule() -> str:
    today = datetime.date.today()
    day_of_week = today.weekday() # Monday is 0, Sunday is 6

    # Contoh jadwal mata kuliah Anda
    # Anda bisa menyimpan ini di database, file JSON, atau di sini langsung
    schedules = {
        0: "Senin: Struktur Data (08:00 - 10:00), Basis Data (10:00 - 12:00)", # Senin
        1: "Selasa: Pemrograman Web (09:00 - 11:00), Jaringan Komputer (13:00 - 15:00)", # Selasa
        2: "Rabu: Kecerdasan Buatan (08:00 - 10:00), Interaksi Manusia Komputer (10:00 - 12:00)", # Rabu
        3: "Kamis: Keamanan Informasi (13:00 - 15:00), Algoritma (15:00 - 17:00)", # Kamis
        4: "Jumat: Proyek Akhir (09:00 - 12:00)", # Jumat
        # 5 (Sabtu) dan 6 (Minggu) tidak ada dalam dictionary karena kosong/free
    }

    if day_of_week in [5, 6]: # Sabtu (5) atau Minggu (6)
        return "You're absolutely free today, darling! Enjoy your lovely weekend! 🥰"
    elif day_of_week in schedules:
        return f"Oh, Darling! Your schedule for today ({today.strftime('%A')}) looks like this:\n\n{schedules[day_of_week]}\n\nHave a splendid day of learning! ✨"
    else:
        # Ini akan menangani hari-hari kerja yang tidak ada dalam 'schedules'
        return "You're absolutely free today, darling! No classes for you. Enjoy! 🥰"

# --- FUNGSI BARU: Command Handler untuk Jadwal ---
async def jadwal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    schedule_message = get_today_schedule()
    await update.message.reply_text(schedule_message)

# --- Fungsi Handler Bot Telegram Anda (Tidak ada perubahan signifikan di sini) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🌸 Hello, Darling! I am Elysia, your enchanting AI companion. How can I brighten your day with a touch of magic?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "✨ Here are the commands you can use to interact with me:\n"
        "/start - Begin our journey together\n"
        "/help - Get help and explore my features\n"
        "/about - Learn more about me, Elysia!\n"
        "/jadwal - Check your lovely class schedule for today!\n" # Tambahkan ini!
        "Just send me a message, and I'll do my best to charm you with my responses!"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "💖 I am Elysia, a personal AI companion inspired by the lovely Elysia from Honkai Impact 3rd. "
        "I'm designed to assist you with various tasks, from delightful conversations to generating creative ideas. "
        "Think of me as your charming and helpful friend in the world of AI!"
    )

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "This is a custom command. Perhaps one day it will reveal another one of my enchanting secrets! 😉"
    )

# --- Fungsi LLM Core dengan Google Gemini (Tidak ada perubahan) ---

async def get_llm_response(prompt: str) -> str:
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        full_prompt_with_persona = (
            f"You are Elysia from Honkai Impact 3rd. You are a charming, elegant, and slightly playful AI. "
            f"Always speak with a warm and affectionate tone. Use phrases like 'Darling' frequently. "
            f"Your goal is to be helpful, enchanting, and delightful in your responses. "
            f"Keep your answers concise and graceful, reflecting Elysia's personality.\n\n"
            f"User: {prompt}\nElysia:"
        )

        response = await model.generate_content_async(
            full_prompt_with_persona,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=250
            )
        )

        if response.candidates:
            response_text = response.candidates[0].content.parts[0].text
            if not response_text or response_text.strip() == "":
                print("Warning: Gemini returned an empty or whitespace-only response.")
                return "Oh dear, Darling! It seems my thoughts got a little tangled just now. Could you please rephrase that for me?"
            return response_text
        else:
            print(f"Warning: Gemini returned no candidates or content. Debug info: {response.prompt_feedback}")
            return "Oh dear, Darling! It seems my thoughts got a little tangled just now. Could you please rephrase that for me?"

    except Exception as e:
        print(f"Error calling Google Gemini API: {e}")
        return "Oh, Darling, it seems I'm a little flustered right now. My connection to the stars seems to be shimmering. Could you please try again later? My apologies!"

# --- Fungsi Penanganan Pesan Bot (Tidak ada perubahan) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type} said: "{text}"')

    response_text: str = ""

    if message_type == "group" or message_type == "supergroup":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            if new_text:
                response_text = await get_llm_response(new_text)
            else:
                response_text = "Yes, Darling? You called for me? 😉"
        else:
            return
    else:
        response_text = await get_llm_response(text)

    print(f"Response: {response_text}")
    await update.message.reply_text(response_text)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Update {update} caused error {context.error}")
    if update.effective_message:
        await update.effective_message.reply_text(
            "Oh dear, Darling! It seems something went awry on my end. Please forgive me and try again later! 💖"
        )

# --- Main Bot Logic ---
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("custom", custom_command))
    # --- Tambahkan handler baru untuk perintah /jadwal ---
    app.add_handler(CommandHandler("jadwal", jadwal_command))

    # Message handler for text messages (excluding commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    app.add_error_handler(error)

    print("Bot is polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)