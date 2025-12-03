import asyncio
import os
import feedparser
import google.generativeai as genai
from telegram import Bot

# Load secrets safely
BOT_TOKEN = os.environ.get("8590363689:AAHpCG0g-Dvw7oShRzmVfsJoJR753kNxO7A")
GEMINI_API_KEY = os.environ.get("AIzaSyByHQSobwbh6GjOlZoE2D_MfcN0EqLR2CI")
CHANNEL_ID = os.environ.get("1087968824")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def main():
    print("--- Fetching News ---")
    # Fetch Top News from India (English headlines are fine, Gemini will translate)
    rss_url = "https://news.google.com/rss/search?q=India+Current+Affairs+when:1d&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        print("No news found.")
        return

    # Get top 15 headlines for better context
    headlines = [entry.title for entry in feed.entries[:15]]
    news_text = "\n".join(headlines)

    print("--- Generating Quiz in Hindi ---")
    
    # --- HERE IS THE MAIN CHANGE FOR HINDI ---
    prompt = f"""
    Act as a strict exam setter for Indian Competitive Exams (UPSC, SSC, Railways).
    Based on the provided news headlines, generate **20 Current Affairs Multiple Choice Questions (MCQs) in HINDI (Devanagari Script)**.
    
    HEADLINES:
    {news_text}
    
    STRICT FORMAT (Do not use Markdown bold like ** in the question/options):
    Q1. [प्रश्न हिंदी में]
    A) [विकल्प A]
    B) [विकल्प B]
    C) [विकल्प C]
    D) [विकल्प D]
    Answer: [सही विकल्प का टेक्स्ट]
    
    Q2. ...
    """
    
    try:
        response = model.generate_content(prompt)
        quiz_text = response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return

    print("--- Sending to Telegram ---")
    bot = Bot(token=BOT_TOKEN)
    
    # Hindi Header Message
    import datetime
    date_str = datetime.date.today().strftime("%d %B %Y")
    header_msg = f"🇮🇳 **दैनिक करेंट अफेयर्स प्रश्नोत्तरी** ({date_str})\n\n🔥 _आज के मुख्य समाचारों पर आधारित प्रश्न तैयार हैं..._"
    
    await bot.send_message(chat_id=CHANNEL_ID, text=header_msg, parse_mode='Markdown')
    
    # Split and send
    questions = quiz_text.split("Q")
    for q in questions:
        if len(q.strip()) > 10:
            final_q = "Q" + q
            # Send to Telegram
            await bot.send_message(chat_id=CHANNEL_ID, text=final_q)
            await asyncio.sleep(1.5) # Anti-spam delay

    # Hindi Footer Message
    await bot.send_message(chat_id=CHANNEL_ID, text="✅ **आज का क्विज़ समाप्त!** कल सुबह फिर मिलेंगे।")

if __name__ == "__main__":
    asyncio.run(main())
