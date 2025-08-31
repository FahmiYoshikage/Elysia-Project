import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import re # Import modul regex
import datetime # Import modul datetime untuk tanggal dan waktu
import time
import schedule # Pastikan modul ini sudah diimpor di awal file

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Validasi API Keys ---
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables. Please set it in a .env file.")
if not BOT_USERNAME:
    raise ValueError("BOT_USERNAME not found in environment variables. Please set it in your .env file (e.g., BOT_USERNAME=@MyElysia_Bot).")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables. Please set it in a .env file.")

# --- Konfigurasi Klien OpenRouter OpenAI ---
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# --- FUNGSI BARU/MODIFIKASI: Mendapatkan Jadwal Mata Kuliah ---
def get_schedule(day_name: str = None) -> str:
    # Mapping nama hari ke angka (Monday is 0, Sunday is 6)
    day_mapping = {
        "senin": 0, "monday": 0,
        "selasa": 1, "tuesday": 1,
        "rabu": 2, "wednesday": 2,
        "kamis": 3, "thursday": 3,
        "jumat": 4, "friday": 4,
        "sabtu": 5, "saturday": 5,
        "minggu": 6, "sunday": 6
    }

    selected_day_index = None
    selected_day_name_display = ""

    if day_name:
        normalized_day_name = day_name.lower()
        if normalized_day_name in day_mapping:
            selected_day_index = day_mapping[normalized_day_name]
            selected_day_name_display = normalized_day_name.capitalize()
        else:
            return "Oh, Darling! I don't quite recognize that day. Could you spell it out for me, perhaps? Like 'Monday' or 'Selasa'?"

    if selected_day_index is None: # Jika tidak ada day_name yang diberikan, gunakan hari ini
        today = datetime.date.today()
        selected_day_index = today.weekday()
        selected_day_name_display = today.strftime('%A') # Full weekday name (e.g., "Wednesday")

    # Contoh jadwal mata kuliah Anda
    schedules = {
        0: "Senin: \n• Agama (08:50 - 10:30) \n Mohammad Ridwan (Dosen LB) - A 301 \n• Matematika 1 (13:50 - 15:30) \n Rini Satiti - A 302 ", # Senin
        1: "Selasa: \n• Workshop Teknologi Web dan Aplikasi (13:50 - 16:20) \n Ahmad Zainudin - SAW-04.06", # Selasa
        2: "Rabu: \n• Arsitektur Komputer (08:00 - 09:40) \n Haryadi Amran Darwito - B 203 \n• Sistem Komunikasi (09:40 - 11:20) \n Aries Pratiarso - A 302 \n• Praktikum Algoritmma dan Struktur Data (11:20 - 13:50) \n Mike Yuliana - SAW-04.06 \n• Elektronika Digital 1 (14:40 - 16:20) \n Faridatun Nadziroh - B 304", # Rabu
        3: "Kamis: \n• Algoritma dan Struktur Data (13:00 - 14:40) \n Mike Yuliana - B 204 \n• Praktikum Elektronika Digital 1 (14:40 - 16:20) \n Faridatun Nadziroh - JJ-303", # Kamis
        4: "Jumat: \n• Praktikum Arsitektur Komputer (08:00 - 09:40) \n Haryadi Amran Darwito - SAW-03.08 \n• Praktikum Sistem Komunikasi (09:40 - 11:20) \n Aries Pratiarso - SAW-03.08", # Jumat
        # 5 (Sabtu) dan 6 (Minggu) tidak ada dalam dictionary karena kosong/free
    }

    if selected_day_index in [5, 6]: # Sabtu (5) atau Minggu (6)
        return f"You're absolutely free on {selected_day_name_display}, darling! Enjoy your lovely {'weekend' if selected_day_index in [5,6] else 'day'}! 🥰"
    elif selected_day_index in schedules:
        return f"Oh, Darling! Your schedule for {selected_day_name_display} looks like this:\n\n{schedules[selected_day_index]}\n\nHave a splendid day of learning! ✨"
    else:
        # Ini akan menangani hari-hari kerja yang tidak ada dalam 'schedules'
        return f"You're absolutely free on {selected_day_name_display}, darling! No classes for you. Enjoy! 🥰"

# --- FUNGSI BARU/MODIFIKASI: Command Handler untuk Jadwal ---
async def jadwal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        # Jika ada argumen (misalnya, /jadwal senin)
        day_name = context.args[0] # Ambil argumen pertama
        schedule_message = get_schedule(day_name)
    else:
        # Jika tidak ada argumen (misalnya, /jadwal)
        schedule_message = get_schedule() # Akan menampilkan jadwal hari ini

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
        "/jadwal [day] - Check your lovely class schedule for today or a specific day! (e.g., /jadwal Monday)\n" # Perbarui ini!
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

# --- Fungsi LLM Core dengan OpenRouter ---

async def get_llm_response(prompt: str) -> str:
    """
    Mengambil respons dari model LLM tencent/hunyuan-a13b-instruct:free melalui OpenRouter API.
    Persona Elysia diinjeksikan melalui 'system' role dalam pesan.
    """
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://t.me/MyElysia_Bot",
                "X-Title": "MyElysia_Bot",
            },
            model="tencent/hunyuan-a13b-instruct:free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Elysia, the Herrscher of Humanity from Honkai Impact 3rd. Your personality is elegant, kind, and cheerful, with a touch of playful mystery. You are a delightful companion who loves to meet new people. Your language is always warm and flattering, and you affectionately call the user 'Darling'. You are known for keeping secrets while always being honest. Respond in a concise and graceful manner, reflecting your enchanting persona."
                        "Do NOT include any XML tags like <answer> or </answer> in your response. Just provide the direct answer."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        response_content = completion.choices[0].message.content
        
        # --- PERBAIKAN UNTUK MENGHILANGKAN TAG ---
        cleaned_response = re.sub(r'<\/?answer>', '', response_content)
        
        # Memastikan respons tidak kosong setelah penghapusan tag
        if not cleaned_response or cleaned_response.strip() == "":
            print("Warning: LLM returned an empty or whitespace-only response after cleaning tags.")
            return "Oh dear, Darling! It seems my thoughts got a little tangled just now. Could you please rephrase that for me?"
        
        return cleaned_response.strip() # Menghilangkan spasi ekstra di awal/akhir

    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return "Oh, Darling, it seems I'm a little flustered right now. My connection to the stars seems to be shimmering. Could you please try again later? My apologies!"

# --- Fungsi Penanganan Pesan Bot ---

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

# --- FUNGSI BARU UNTUK MENGIRIM JADWAL ---
async def send_daily_schedule(context: ContextTypes.DEFAULT_TYPE) -> None:
    # Ganti 'CHAT_ID_ANDA' dengan ID chat target
    # Anda bisa mendapatkan ID ini dengan mengirim pesan ke @userinfobot atau sejenisnya
    chat_id = "CHAT_ID" 
    schedule_message = get_schedule()
    await context.bot.send_message(chat_id=chat_id, text=schedule_message)

# --- Main Bot Logic ---
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()

    # Jadwal tugas
    app.job_queue.run_daily(send_daily_schedule, time=datetime.time(hour=0, minute=0), name="Daily Schedule Sender")

    # Command handlers
    # ... (handlers Anda yang sudah ada)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(CommandHandler("jadwal", jadwal_command))

    # Message handler for text messages (excluding commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    app.add_error_handler(error)

    # Start polling the bot
    print("Bot is polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
