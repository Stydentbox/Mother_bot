import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import TELEGRAM_TOKEN, CHATGPT_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет! Я MotherBot. Я помогу вам создать собственного Telegram-бота. '
        'Введите /newbot для начала процесса.'
    )

async def new_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Введите тематику вашего бота или ключевые функции, которые вы хотите реализовать.'
    )
    context.user_data['step'] = 'get_theme'

async def resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_plan = context.user_data.get('bot_plan', 'Неопределенный бот')
    await update.message.reply_text(
        f'Для реализации бота "{bot_plan}" вам могут понадобиться следующие ресурсы:\n'
        '- Python и библиотека python-telegram-bot\n'
        '- Сервер для развертывания (например, Heroku, AWS, или Google Cloud)\n'
        '- Инструменты для мониторинга и логирования (например, Sentry, Loggly)\n'
        '- GitHub для управления кодом\n'
        'Введите /generate_code для генерации начального кода.'
    )
    context.user_data['step'] = 'generate_code'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    current_step = context.user_data.get('step')

    if current_step == 'get_theme':
        # Запросить название и план у ChatGPT
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {CHATGPT_API_KEY}'},
            json={
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': 'Вы помощник по созданию ботов.'},
                    {'role': 'user', 'content': f'Создай план для бота с тематикой: {user_input}'}
                ]
            }
        )

        if response.status_code == 200:
            data = response.json()
            bot_plan = data['choices'][0]['message']['content'].strip()
            context.user_data['bot_plan'] = bot_plan

            await update.message.reply_text(
                f'Вот предложенный план для вашего бота:\n\n{bot_plan}\n\n'
                'Введите /resources для получения списка необходимых ресурсов.'
            )
            context.user_data['step'] = 'get_resources'
        else:
            await update.message.reply_text('Извините, не удалось получить план. Попробуйте позже.')

    else:
        await update.message.reply_text('Я не уверен, что вы хотите. Попробуйте команду /newbot для начала.')

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('newbot', new_bot))
    application.add_handler(CommandHandler('resources', resources))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
