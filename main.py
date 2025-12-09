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


async def unknown_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "❌ Команда не розпізнана!\n"
        "Доступні команди:\n"
        "/start - зареєструватися\n"
        "/add_category - додати категорію\n"
        "/categories - список категорій\n"
        "/add_transaction - додати транзакцію\n"
        "/delete_transaction - видалити транзакцію\n"
        "/stats - подивитися статистику"
    )


#старт додати юзера
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

#додати категорію
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

#додати категорію
async def categories(update: Update, context: CallbackContext):
    session = SessionLocal()
    try:
        telegram_id = update.effective_user.id

        user = session.execute(
            text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        ).fetchone()

        if not user:
            await update.message.reply_text("Register firstly")
            return

        user_id = user[0]

        rows = session.execute(
            text("SELECT name FROM categories WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchall()

        if not rows:
            await update.message.reply_text("You don’t have categories yet. Add one: /add_category food")
            return

        cats = "\n".join(f"- {row[0]}" for row in rows)
        await update.message.reply_text(f"Categories:\n{cats}")

    finally:
        session.close()

async def add_transaction(update: Update, context: CallbackContext):
    session = SessionLocal()
    try:
        telegram_id = update.effective_user.id

        if len(context.args) < 2:
            await update.message.reply_text("Format: /add <amount> <category> <description optional>")
            return

        amount = context.args[0]
        category = context.args[1]
        description = " ".join(context.args[2:]) if len(context.args) > 2 else ""

        # validation
        try:
            amount = float(amount)
        except:
            await update.message.reply_text("Amount must be a number")
            return

        # знайти юзера
        user = session.execute(
            text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        ).fetchone()
        if not user:
            await update.message.reply_text("Register firstly")
            return
        user_id = user[0]

        # знайти категорію
        cat = session.execute(
            text("SELECT id FROM categories WHERE user_id = :user_id AND name = :name"),
            {"user_id": user_id, "name": category}
        ).fetchone()
        if not cat:
            await update.message.reply_text(f"Category '{category}' does not exist. Create using /add_category")
            return
        category_id = cat[0]

        # **тут додаємо транзакцію**
        session.execute(
            text("""
                INSERT INTO transactions (user_id, category_id, amount, created_at)
                VALUES (:user_id, :category_id, :amount, NOW())
            """),
            {"user_id": user_id, "category_id": category_id, "amount": amount}
        )
        session.commit()

        await update.message.reply_text(f"Added {amount} to '{category}'")

    except Exception as e:
        session.rollback()
        await update.message.reply_text(f"Error: {e}")
    finally:
        session.close()

async def stats(update: Update, context: CallbackContext):
    session = SessionLocal()
    try:
        telegram_id = update.effective_user.id

        # Перевірка юзера
        user = session.execute(
            text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        ).fetchone()

        if not user:
            await update.message.reply_text("Register firstly using /start")
            return

        user_id = user[0]

        # Підсумки по категоріях
        result = session.execute(
            text("""
                SELECT c.name, SUM(t.amount)
                FROM transactions t
                JOIN categories c ON c.id = t.category_id
                WHERE t.user_id = :user_id
                GROUP BY c.name
            """),
            {"user_id": user_id}
        ).fetchall()

        if not result:
            await update.message.reply_text("No transactions yet.")
            return

        # Формуємо текст для Telegram
        text_msg = "Your stats:\n\n"
        for row in result:
            category_name = row[0]
            total_amount = row[1] if row[1] else 0
            text_msg += f"• {category_name}: {total_amount}\n"

        await update.message.reply_text(text_msg)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
    finally:
        session.close()

async def delete_transaction(update: Update, context: CallbackContext):
    session = SessionLocal()
    try:
        telegram_id = update.effective_user.id

        if len(context.args) == 0:
            await update.message.reply_text("Usage: /delete_transaction <transaction_id>")
            return

        try:
            transaction_id = int(context.args[0])
        except:
            await update.message.reply_text("Transaction ID must be a number")
            return

        # знайти юзера
        user = session.execute(
            text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        ).fetchone()

        if not user:
            await update.message.reply_text("Register first using /start")
            return

        user_id = user[0]

        # перевірити, чи транзакція належить юзеру
        transaction = session.execute(
            text("SELECT id FROM transactions WHERE id = :transaction_id AND user_id = :user_id"),
            {"transaction_id": transaction_id, "user_id": user_id}
        ).fetchone()

        if not transaction:
            await update.message.reply_text("Transaction not found or does not belong to you")
            return

        # видалити транзакцію
        session.execute(
            text("DELETE FROM transactions WHERE id = :transaction_id"),
            {"transaction_id": transaction_id}
        )
        session.commit()

        await update.message.reply_text(f"Transaction {transaction_id} deleted successfully")

    except Exception as e:
        session.rollback()
        await update.message.reply_text(f"Error: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    app = ApplicationBuilder().token(telegram_key).build()
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_category", add_category))
    app.add_handler(CommandHandler("categories", categories))
    app.add_handler(CommandHandler("add_transaction", add_transaction))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("delete_transaction", delete_transaction))
    app.run_polling()