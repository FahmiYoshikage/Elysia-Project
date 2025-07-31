import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import re # Import modul regex
import datetime # Import modul datetime untuk tanggal dan waktu



# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Amankan BOT_USERNAME dengan mengambilnya dari .env juga, bukan hardcode
BOT_USERNAME = os.getenv("BOT_USERNAME") # Tambahkan ini ke .env Anda: BOT_USERNAME="@MyElysia_Bot"
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

# --- Fungsi Handler Bot Telegram Anda ---
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
        # 1. Coba beritahu model untuk tidak menyertakan tag di system prompt (sudah ditambahkan di atas)
        # 2. Hapus tag secara manual jika model tetap mengembalikannya
        
        # Menggunakan regex untuk menghapus tag <answer> dan </answer>
        # re.sub() akan mengganti semua kemunculan pola dengan string kosong
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

    # Start polling the bot
    print("Bot is polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)