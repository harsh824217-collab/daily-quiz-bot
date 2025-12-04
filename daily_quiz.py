import asyncio
import os
import feedparser
import requests
import json
from telegram import Bot

# Load secrets
BOT_TOKEN = os.environ.get("8590363689:AAHpCG0g-Dvw7oShRzmVfsJoJR753kNxO7A")
GEMINI_API_KEY = "AIzaSyAueWAidi_vY-5JhegkBjk22N0-v1eWq7g"
TARGET_CHAT_ID = os.environ.get("1087968824") 

async def get_gemini_response(prompt):
    # DIRECT API CALL (No Library)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

async def main():
    print("--- Fetching News ---")
    rss_url = "https://news.google.com/rss/search?q=India+Current+Affairs+when:1d&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        print("No news found.")
        return

    headlines = [entry.title for entry in feed.entries[:15]]
    news_text = "\n".join(headlines)

    print("--- Generating Quiz (Direct Mode) ---")
    
    prompt = f"""
    Act as a strict exam setter for Indian Competitive Exams.
    Based on the headlines, generate **20 Current Affairs MCQs in HINDI (Devanagari Script)**.
    
    HEADLINES:
    {news_text}
    
    STRICT FORMAT:
    Q1. [प्रश्न हिंदी में]
    A) [विकल्प A]
    B) [विकल्प B]
    C) [विकल्प C]
    D) [विकल्प D]
    Answer: [सही विकल्प]
    
    Q2. ...
    """
    
    quiz_text = await get_gemini_response(prompt)
    
    if quiz_text:
        print("--- Sending to Telegram ---")
        bot = Bot(token=BOT_TOKEN)
        
        # Header
        import datetime
        date_str = datetime.date.today().strftime("%d %B %Y")
        header_msg = f"🇮🇳 **दैनिक करेंट अफेयर्स प्रश्नोत्तरी** ({date_str})\n\n🔥 _आज के मुख्य समाचारों पर आधारित प्रश्न तैयार हैं..._"
        
        try:
            await bot.send_message(chat_id=TARGET_CHAT_ID, text=header_msg, parse_mode='Markdown')
            
            questions = quiz_text.split("Q")
            for q in questions:
                if len(q.strip()) > 10:
                    final_q = "Q" + q
                    await bot.send_message(chat_id=TARGET_CHAT_ID, text=final_q)
                    await asyncio.sleep(1.5)

            await bot.send_message(chat_id=TARGET_CHAT_ID, text="✅ **आज का क्विज़ समाप्त!**")
        except Exception as e:
            print(f"Telegram Error: {e}")
            # Agar ID galat hui to yahan error dikhega
    else:
        print("Failed to get response from Gemini.")

if __name__ == "__main__":
    asyncio.run(main())
