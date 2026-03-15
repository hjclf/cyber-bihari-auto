import requests
from groq import Groq
from telegram import Bot
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
import os

# CONFIG
TELEGRAM_TOKEN = "8617544467:AAGMuVN7VWZZF9GFQ-DLExPue8NgdzK6Nvw"
CHANNEL_ID = -1003718617214
GROQ_API_KEY = "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"
WHATSAPP_LINK = "https://whatsapp.com/channel/0029VbCKP717T8bdCgnaPQ0S"

SEEN_FILE = "seen_pdfs.json"

client = Groq(api_key=GROQ_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

seen = load_seen()

def save_seen():
    with open(SEEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)

def get_ai_summary(title):
    prompt = f"""यह Purnea University या उसके कॉलेज का नोटिस है। हिंदी में 2-3 लाइन में बताओ कि ये PDF क्या सूचना देता है (students के लिए clear और urgent)। Title: {title}"""
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=120
        )
        return chat.choices[0].message.content.strip()
    except:
        return "नई महत्वपूर्ण सूचना जारी। PDF में पूरा डिटेल पढ़ें।"

def post_pdf(pdf_url, title, source):
    post_hash = str(hash(pdf_url))
    if post_hash in seen:
        print(f"[Duplicate / पुराना] {title} from {source} - skip")
        return

    summary = get_ai_summary(title)

    caption = f"""🔔 **नई आधिकारिक सूचना** (मार्च 2026 के बाद की)

📌 **{source}**

📝 **संक्षिप्त जानकारी (AI से):**
{summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
तुरंत अपडेट के लिए WhatsApp चैनल जॉइन करें:
{WHATSAPP_LINK}

#PurneaUniversity #BiharEducation #Notice"""

    try:
        bot.send_document(
            chat_id=CHANNEL_ID,
            document=pdf_url,
            caption=caption,
            parse_mode='Markdown'
        )
        seen[post_hash] = datetime.now().isoformat()
        save_seen()
        print(f"[SUCCESS - नया नोटिस] पोस्ट किया: {title} | {source}")
    except Exception as e:
        print(f"[FAILED] {title} | Error: {e}")

def scrape_site(url, name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        r = requests.get(url, timeout=20, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        count = 0
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.lower().endswith('.pdf'):
                title = a.text.strip() or f"{name} - नई नोटिस"
                full_url = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
                
                post_hash = str(hash(full_url))
                if post_hash in seen:
                    print(f"[पुराना PDF skip] {title} from {name}")
                    continue
                
                post_pdf(full_url, title, name)
                count += 1
        
        if count > 0:
            print(f"[{name}] {count} नया PDF मिला और पोस्ट किया")
        else:
            print(f"[{name}] इस बार कोई नया PDF नहीं मिला")
            
    except Exception as e:
        print(f"[{name}] स्क्रेप एरर: {e}")

# सभी साइट्स की लिस्ट (Purnea University + जितने कॉलेजेस की वेबसाइट मिलीं)
sources = [
    # Purnea University मुख्य (सभी कॉलेजेस पर लागू नोटिस यहीं से आते हैं)
    ("https://purneau.ac.in/", "Purnea University मुख्य"),
    ("https://purneau.ac.in/pages/news", "Purnea University Notices"),
    ("https://purneau.ac.in/news/examination", "Purnea University Exams & Results"),
    
    # Constituent Colleges
    ("https://purneacollege.ac.in/", "Purnea College"),
    ("https://www.purneamahilacollege.ac.in/", "Purnea Mahila College"),
    ("https://www.mlaryacollegekasba.ac.in/", "M.L. Arya College Kasba"),
    
    # Affiliated Colleges (एक्टिव वेबसाइट्स वाली)
    ("https://snsydegreecollegelib.org/", "S.N.S.Y. Degree College Rambagh"),
    ("http://www.ndcpurnea.org/", "N.D. College Rambagh"),
    ("https://bnccollegedhamdaha.in/", "B.N.C. College Dhamdaha"),
    ("https://www.dscollegekatihar.in/", "D.S. College Katihar"),
    ("https://forbesganjcollege.ac.in/", "Forbesganj College"),
    ("https://www.glmcollege.ac.in/", "G.L.M. College Banmankhi"),
    ("https://www.bmtlawcollege.org/", "B.M.T. Law College"),
    ("http://www.mfaabed.org.in/", "M.F.A.A. B.Ed College"),
    ("http://swadeshipurnia.in/", "Swadeshi B.Ed College"),
    ("https://srpttcollegepurnea.com/", "SRP T.T. College Purnea"),
    ("https://psdcollegeharda.in/", "P.S.D College Harda"),
    ("https://srcdcollege.in/", "S.R.C. Degree College Katihar"),
    ("http://www.rymaniharicollege.com/", "R.Y. Manihari College"),
    ("https://bmcollegebarari.ac.in/", "B.M. College Barari"),
    ("https://www.balrampurcollege.com/", "Balrampur Degree College"),
    ("https://kdcollegerng.in/", "K.D. College Raniganj"),
]

print("Bot शुरू हो गया...")
print("पहली बार कुछ भी पोस्ट नहीं होगा (पुराने नोटिस स्किप हो जाएंगे)")
print("उसके बाद से सिर्फ नए नोटिस ही आएंगे (मार्च 2026 के बाद वाले)")
print("हर 30 मिनट में चेक करेगा\n")

while True:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n=== नया चेक शुरू: {current_time} ===")
    
    for url, name in sources:
        scrape_site(url, name)
    
    print("=== चेक पूरा === अगला चेक 30 मिनट बाद\n")
    time.sleep(1800)  # 30 मिनट
