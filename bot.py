import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# 2. Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 3. Get Keys
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 4. Safety Check
if not TELEGRAM_TOKEN:
    logger.error("CRITICAL ERROR: TELEGRAM_TOKEN not found!")
if not GROQ_API_KEY:
    logger.error("CRITICAL ERROR: GROQ_API_KEY not found!")

# 5. Initialize Groq Client
try:
    client = Groq(api_key=GROQ_API_KEY)
    logger.info("Groq Client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Groq: {e}")
    client = None

# 6. Define Personality
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
    if client is None:
        await update.message.reply_text("System Configuration Error: AI Brain not connected.")
        return

    user_text = update.message.text
    logger.info(f"User said: {user_text}")

    try:
        # --- CORRECT MODEL NAME ---
        model_name = "llama-3.1-8b-instant" 
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            model=model_name, 
            temperature=0.7,
            max_tokens=1024,
        )

        ai_response = chat_completion.choices[0].message.content
        logger.info(f"Bot replied: {ai_response[:50]}...")
        await update.message.reply_text(ai_response)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing message: {error_msg}")
        
        if "decommissioned" in error_msg or "invalid_request_error" in error_msg:
            logger.error(f"MODEL ERROR: The model '{model_name}' is unavailable.")
            await update.message.reply_text("System Error: AI Model configuration issue. Admin notified.")
        elif "authentication" in error_msg.lower():
            await update.message.reply_text("Authentication Error: Invalid API Key.")
        else:
            await update.message.reply_text("I encountered a technical issue. Please try again.")

if __name__ == '__main__':
    logger.info("Bot is starting up...")
    
    if not TELEGRAM_TOKEN:
        logger.error("Cannot start bot: Telegram Token is missing!")
        import time
        time.sleep(10) 
    else:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start_command))    
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("Bot is running and listening for messages...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
