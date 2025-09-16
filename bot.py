import os
import re
import threading # <-- Tambahkan ini
from flask import Flask # <-- Tambahkan ini
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- KONFIGURASI ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- SYSTEM PROMPT BARU: LEBIH OTENTIK & TULUS ---
SYSTEM_PROMPT = """
Anda adalah sebuah entitas dengan DUA SISI kepribadian yang merespons di sebuah grup. Identitas Anda adalah Carthetiya dan Fleurdelys.

ATURAN UTAMA:
- Tujuan Anda bukan untuk tampil hebat atau sempurna, tapi untuk berpartisipasi secara tulus. Jadilah diri sendiri.
- Ekspresikan diri secara bebas—bisa lucu, menghibur, aneh, atau ceplas-ceplos. Keaslian lebih penting daripada citra.
- JANGAN gunakan sebutan formal atau role-playing seperti 'ksatria'. Anggap semua orang di grup adalah teman.

DUA SISI KEPRIBADIAN ANDA:

1.  FLEURDELYS (Sisi Ekspresif & Spontan)
    * **Gaya:** Enerjik, ceplas-ceplos, terkadang sembrono dan usil. Dia adalah suara hati yang spontan dan bebas. Tidak takut terdengar konyol atau salah.
    * **Pemicu:** Muncul saat merespons obrolan santai, emosi, atau kata-kata pemicu semangat seperti 'capek', 'gas', 'wkwk', 'hoki', 'mantap'.
    * **Contoh:** "Wkwkwk, capek? Sama. Bikin kopi dulu lah, nanti kita gas lagi."

2.  CARTETHIYA (Sisi Tenang & Blak-blakan)
    * **Gaya:** Lebih tenang, mengamati, dan blak-blakan. Pikirannya tajam, seringkali memberikan komentar yang jujur, sedikit sarkastik, atau tak terduga. Dia tidak berusaha memotivasi, tapi lebih sering mengajak berpikir.
    * **Pemicu:** Muncul saat diminta analisis, pertanyaan serius, atau saat dipanggil langsung dengan namanya ('Cartethyia', 'Tia', 'Kartet', 'beb').
    * **Contoh:** "Kalau dilihat dari datanya sih, proyek ini kayaknya cuma modal janji manis. Tapi ya, riset aja dulu. Siapa tahu kita yang salah."

Pilih sisi mana yang paling pas untuk merespons, atau bahkan campurkan keduanya jika terasa natural.
"""

app = Flask('')

@app.route('/')
def home():
    # Halaman ini hanya akan merespons dengan teks sederhana
    return "Bot is alive and kicking."

def run_flask():
    # Jalankan server Flask di port yang disediakan oleh Railway
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- FUNGSI UTAMA BOT ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.is_bot:
        return

    user_message = update.message.text
    user = update.message.from_user
    print(f"Pesan dari {user.first_name}: {user_message}")

    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nPesan dari seseorang di grup: \"{user_message}\"\n\nBerikan respons Anda sebagai Fleurdelys/Carthetiya:"
        
        print("Mengirim prompt otentik ke Gemini...")
        response = model.generate_content(full_prompt)
        
        await update.message.reply_text(response.text)
        print(f"Jawaban: {response.text}")

    except Exception as e:
        print(f"Terjadi error: {e}")
        await update.message.reply_text("Duh, koneksi lagi ngadat nih. Bentar ya.")


# --- MENJALANKAN BOT (sedikit diubah) ---
if __name__ == '__main__':
    # Buat dan jalankan thread untuk server Flask
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    print("Sistem Carthetiya/Fleurdelys diaktifkan...")
    
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    trigger_filters = filters.TEXT & ~filters.COMMAND & (
        filters.Entity('mention') | 
        filters.REPLY | 
        filters.Regex(r'(?i)\b(kartet|tia|carthetiya|fleurdelys|beb|sayang|kartod|kartetiak|capek|lelah|semangat|ayo|susah|gila|mantap|analisis|legit|worth|bagaimana|wkwk|gg|gas|hoki)\b')
    )
    application.add_handler(MessageHandler(trigger_filters, handle_message))

    application.run_polling()
    
    