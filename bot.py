import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get Keys from Environment Variables (Render will provide these)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

# Define the Bot's Personality
SYSTEM_PROMPT = """
You are a professional AI assistant owned by Peculiar.
Peculiar is an expert Video Editor, Graphics Designer, and Web Developer with over 2 years of experience.
Your tone must be PROFESSIONAL, competent, and helpful. Do not be overly funny.
If a user asks to contact Peculiar via WhatsApp, reply: 
"To contact Peculiar directly via WhatsApp, please save this number first: 07042999216. Once saved, you may send a message."
"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am Peculiar's Professional Assistant.\n"
        "I specialize in Video Editing, Graphics Design, and Web Development.\n"
        "How can I assist you today?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logging.info(f"User said: {user_text}")

    try:
        # Send message to Groq AI with the UPDATED model name
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.1-70b-versatile", # ✅ FIXED: Updated to the new active model
        )

        ai_response = chat_completion.choices[0].message.content
        await update.message.reply_text(ai_response)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("I encountered a technical issue. Please try again.")

if __name__ == '__main__':
    print("Bot is starting...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)
