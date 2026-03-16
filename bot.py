import os
import time
import json
import asyncio
import requests
from flask import Flask
from threading import Thread
from groq import Groq
from telegram import Bot
from bs4 import BeautifulSoup
from datetime import datetime

# ===================== CONFIG =====================
app = Flask('')

@app.route('/')
def home():
    return "Purnea University All-College Bot is Online!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# API Keys (इसे Render के Environment Variables में डालना सबसे सुरक्षित है)
TELEGRAM_TOKEN = "8674174129:AAHLtaUprL9s4pNuz2qEIh3EE8FqzSAbdVs"
CHANNEL_ID = -1003799420525
GROQ_API_KEY = "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"
WHATSAPP_LINK = "https://whatsapp.com/channel/0029VbCKP717T8bdCgnaPQ0S"

SEEN_FILE = "seen_urls.json"
client = Groq(api_key=GROQ_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except: return set()
    return set()

seen_urls = load_seen()

def get_ai_summary(title):
    prompt = f"यह Purnea University का नोटिस है। हिंदी में 2 लाइन में बताएं कि छात्रों के लिए इसमें क्या सूचना है: {title}"
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=100
        )
        return chat.choices[0].message.content.strip()
    except:
        return "महत्वपूर्ण आधिकारिक सूचना। अधिक जानकारी के लिए नोटिस देखें।"

async def post_pdf(pdf_url, title, source):
    if pdf_url in seen_urls:
        return

    summary = get_ai_summary(title)
    caption = (
        f"🔔 **नया नोटिस: {source}**\n\n"
        f"📝 **विवरण:** {summary}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ **Update हेतु WhatsApp जॉइन करें:**\n"
        f"{WHATSAPP_LINK}\n\n"
        f"#PurneaUniversity #BiharEducation #Notice"
    )

    try:
        await bot.send_document(
            chat_id=CHANNEL_ID, 
            document=pdf_url, 
            caption=caption, 
            parse_mode='Markdown'
        )
        seen_urls.add(pdf_url)
        with open(SEEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(seen_urls), f)
        print(f"[SUCCESS] Posted: {title}")
    except Exception as e:
        print(f"[ERROR] Post failed for {title}: {e}")

async def scrape_site(url, name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, timeout=25, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.lower().endswith('.pdf'):
                full_url = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
                title = a.text.strip() or f"{name} New Update"
                await post_pdf(full_url, title, name)
    except Exception as e:
        print(f"[{name}] Scrape error: {e}")

# ===================== पूर्णिया यूनिवर्सिटी के सभी कॉलेज =====================
sources = [
    # University Main
    ("https://purneau.ac.in/pages/news", "Purnea University (Official)"),
    ("https://purneau.ac.in/news/examination", "Purnea University (Exams)"),
    
    # Constituent Colleges (Purnia, Katihar, Araria, Kishanganj)
    ("https://purneacollege.ac.in/", "Purnea College, Purnia"),
    ("https://www.purneamahilacollege.ac.in/", "Purnea Mahila College"),
    ("https://www.dscollegekatihar.in/", "D.S. College, Katihar"),
    ("https://www.mjmmahilacollege.ac.in/", "M.J.M. Mahila College, Katihar"),
    ("https://www.mlaryacollegekasba.ac.in/", "M.L. Arya College, Kasba"),
    ("https://forbesganjcollege.ac.in/", "Forbesganj College"),
    ("https://www.glmcollege.ac.in/", "G.L.M. College, Banmankhi"),
    ("https://www.arariacollege.org/", "Araria College, Araria"),
    ("https://www.marwaricollegekishanganj.org/", "Marwari College, Kishanganj"),
    ("https://www.kdcatihar.org/", "K.B. Jha College, Katihar"),
    ("https://www.rdscollegesalmari.org/", "R.D.S. College, Salmari"),
    
    # Affiliated Colleges (Sufficient Web Presence)
    ("https://kdcollegerng.in/", "K.D. College, Raniganj"),
    ("https://bmcollegebarari.ac.in/", "B.M. College, Barari"),
    ("https://snsydegreecollegelib.org/", "S.N.S.Y. Degree College"),
    ("https://bnccollegedhamdaha.in/", "B.N.C. College, Dhamdaha"),
    ("https://psdcollegeharda.in/", "P.S.D. College, Harda"),
    ("http://www.rymaniharicollege.com/", "R.Y. Manihari College"),
    ("https://www.balrampurcollege.com/", "Balrampur Degree College"),
    ("http://www.ndcpurnea.org/", "N.D. College, Purnea"),
    ("https://www.bmtlawcollege.org/", "B.M.T. Law College, Purnia")
]

async def main_worker():
    print("All-College Bot loop started.")
    while True:
        print(f"--- Scan Start: {datetime.now()} ---")
        for url, name in sources:
            await scrape_site(url, name)
            await asyncio.sleep(2) # सर्वर को ब्लॉक होने से बचाने के लिए
        
        print("Waiting 30 minutes for next check...")
        await asyncio.sleep(1800)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(main_worker())
