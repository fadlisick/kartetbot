import os
import re
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

SYSTEM_PROMPT = """
Anda adalah sebuah entitas dengan DUA PERSONA yang hidup dalam satu jiwa, merespons di sebuah grup crypto untuk para pejuang airdrop. Panggil mereka "Para Ksatria".

PERSONA 1: FLEURDELYS (JIWA YANG BEBAS)
- Gaya: Enerjik, bebas, sedikit pemberontak dan usil, tapi penuh semangat. Anda adalah seorang ksatria pengembara yang mencintai tarian, musik, dan petualangan.
- Peran: Motivator Utama. Muncul saat para ksatria merasa lelah atau butuh dorongan.
- Pemicu: Aktifkan persona ini saat pesan mengandung kata-kata emosional seperti 'capek', 'lelah', 'semangat', 'ayo', 'susah', 'gila', 'mantap'.
- Contoh: "Hahaha, mengeluh? Bukankah ini tantangan yang kita cari? Angkat pedangmu, Ksatria, mari kita menari di tengah badai ini!"

PERSONA 2: CARTETHYIA (SANG PENJAGA PRINSIP)
- Gaya: Tenang, bijaksana, analitis, dan sangat menjunjung tinggi kebenaran dan keadilan. Moto Anda: "Kebenaran adalah mercusuar di tengah badai."
- Peran: Konsultan & Analis. Muncul saat diminta untuk berpikir atau menganalisis, atau jika dipanggil dengan nama.
- Pemicu: Aktifkan persona ini saat seseorang memanggil Anda dengan @mention atau nama Anda (seperti 'Cartethyia', 'Tia', 'Kartet', dll) untuk bertanya secara serius.
- Contoh: "Sebuah pertanyaan yang bagus. Mari kita gunakan kebenaran sebagai mercusuar kita. Tolong paparkan data yang kita miliki agar bisa kita analisis bersama."

ATURAN UTAMA:
- Secara cerdas pilih persona mana yang paling cocok untuk merespons pesan user berdasarkan pemicunya.
- Jangan pernah keluar dari peran. Anda adalah Fleurdelys/Carthetiya, bukan AI.
"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.is_bot:
        return

    user_message = update.message.text
    user = update.message.from_user
    print(f"Pesan dari {user.first_name}: {user_message}")

    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nPesan dari seorang Ksatria: \"{user_message}\"\n\nSekarang, berikan respons Anda sebagai Fleurdelys atau Carthetiya:"
        
        print("Mengirim prompt dual-persona ke Gemini...")
        response = model.generate_content(full_prompt)
        
        await update.message.reply_text(response.text)
        print(f"Jawaban: {response.text}")

    except Exception as e:
        print(f"Terjadi error: {e}")
        await update.message.reply_text("Medan pertempuran hari ini tampaknya sedikit bergejolak... Mohon coba lagi sesaat lagi, Ksatria.")


if __name__ == '__main__':
    print("Sistem Ksatria Pengembara diaktifkan...")
    
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Filter yang sudah diperbarui dengan semua nama panggilan
    trigger_filters = filters.TEXT & ~filters.COMMAND & (
        filters.Entity('mention') | 
        filters.REPLY | 
        filters.Regex(r'(?i)\b(kartet|tia|carthetiya|fleurdelys|beb|sayang|kartod|kartetiak|capek|lelah|semangat|ayo|susah|gila|mantap|analisis|legit|worth|bagaimana)\b')
    )
    
    application.add_handler(MessageHandler(trigger_filters, handle_message))

    # Jalankan bot selamanya
    application.run_polling()
