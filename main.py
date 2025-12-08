from config import telegram_key
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, \
    Application
from db import SessionLocal
from sqlalchemy import text


async def start(update: Update, context: CallbackContext):
    telegram_id = update.effective_user.id
    username = update.effective_user.username

    session = SessionLocal()
    try:
        result = session.execute(
            text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        ).fetchone()

        if result:
            await update.message.reply_text(f"hi {username} your account have been crated earlier")
        else:
            session.execute(
                text("INSERT INTO users (telegram_id, username, created_at) VALUES (:telegram_id, :username, NOW())"),
                {"telegram_id": telegram_id, "username": username}
            )
            session.commit()
            await update.message.reply_text(f"Hello {username}your account has been created")
    except Exception as e:
        session.rollback()
        await update.message.reply_text(f"Error: {e}")
    finally:
        session.close()

from config import telegram_key
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, \
    Application
from db import SessionLocal
from sqlalchemy import text


async def start(update: Update, context: CallbackContext):
    telegram_id = update.effective_user.id
    username = update.effective_user.username

    session = SessionLocal()
    try:
        result = session.execute(
            text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        ).fetchone()

        if result:
            await update.message.reply_text(f"hi {username} your account have been crated earlier")
        else:
            session.execute(
                text("INSERT INTO users (telegram_id, username, created_at) VALUES (:telegram_id, :username, NOW())"),
                {"telegram_id": telegram_id, "username": username}
            )
            session.commit()
            await update.message.reply_text(f"Hello {username}your account has been created")
    except Exception as e:
        session.rollback()
        await update.message.reply_text(f"Error: {e}")
    finally:
        session.close()

async def add_category(update: Update, context: CallbackContext):
    session = SessionLocal()
    try:
        telegram_id = update.effective_user.id

        if len(context.args) == 0:
            await update.message.reply_text("Please enter a category name /add_category cafe")
            return

        category_name = " ".join(context.args).strip()

        user = session.execute(
            text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        ).fetchone()

        if not user:
            await update.message.reply_text("Register firstly")
            return

        user_id = user[0]
        existing = session.execute(
            text("SELECT id FROM categories WHERE user_id = :user_id AND name = :name"),
            {"user_id": user_id, "name": category_name}).fetchone()

        if existing:
            await update.message.reply_text(f"The category '{category_name}' already exists")
            return

        session.execute(
            text("INSERT INTO categories (user_id, name) VALUES (:user_id, :name)"),
            {"user_id": user_id, "name": category_name}
        )

        session.commit()
        await update.message.reply_text(f"Category '{category_name}' has been added")


    except Exception as e:
        session.rollback()
        await update.message.reply_text(f"Error: {e}")
    finally:
        session.close()



if __name__ == '__main__':
    app = ApplicationBuilder().token(telegram_key).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_category", add_category))
    app.run_polling()


if __name__ == '__main__':
    app = ApplicationBuilder().token(telegram_key).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_category", add_category))
    app.run_polling()