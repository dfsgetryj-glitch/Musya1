import os
import tempfile

import telebot
from docx import Document
from dotenv import load_dotenv
from telebot import types


load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

# Определяем список пользователей, которые ожидают текста
users_waiting_for_intro_text = []


# Определяем состояние ввода текста
class States:
    WAITING_FOR_INTRO_TEXT = 1


@bot.message_handler(commands=['start'])
def start_command_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет! Я готов к работе.")

    # Создаем кнопку с вводом текста
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text="Отправить текст")
    keyboard.add(button)

    # Отправляем кнопку пользователю
    msg = bot.send_message(
        chat_id,
        "Нажмите на кнопку, чтобы отправить текст",
        reply_markup=keyboard
        )
    bot.register_next_step_handler(msg, send_intro_text_command_handler)


@bot.message_handler(commands=['send_intro_text'])
def send_intro_text_command_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите текст:")
    users_waiting_for_intro_text.append(chat_id)


@bot.message_handler(
        func=lambda message: message.chat.id in users_waiting_for_intro_text
        )
def intro_text_handler(message):
    """Обработчик текста"""
    chat_id = message.chat.id
    intro_text = message.text

    # Удаляем пользователя из списка ожидающих ввода текста
    users_waiting_for_intro_text.remove(chat_id)

    # Генерируем документ и отправляем его пользователю
    try:
        document = generate_document(intro_text)
        msg = bot.send_document(chat_id, document)
        bot.register_next_step_handler(msg, send_intro_text_command_handler)
    except Exception as e:
        bot.send_message(chat_id, "Ошибка генерации документа: " + str(e))


def generate_document(intro_text):
    """Генератор Word документа"""
    try:
        doc = Document()
        doc.add_paragraph(intro_text)
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            document_name = f.name
            doc.save(document_name)
            return open(document_name, 'rb')
    except Exception as e:
        raise Exception("Ошибка генерации документа: " + str(e))


@bot.message_handler(func=lambda message: True)
def unknown_command_handler(message):
    """Обработчик неизвестных команд"""
    chat_id = message.chat.id
    bot.send_message(chat_id, "Я не понимаю, о чем вы.")


if __name__ == '__main__':
    bot.polling()
