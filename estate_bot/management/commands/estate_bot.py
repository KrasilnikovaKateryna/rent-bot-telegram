import traceback

from django.core.management.base import BaseCommand
import telebot
from telebot import types
import os
import django

from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from estate_bot.utils import get_user_state, get_or_create_profile, set_user_state, get_message
from estate_bot.reactions import (
    handle_start, handle_rent_choose_type, handle_rent_choose_price, handle_show_variants,
    handle_lease_photos, handle_lease_type, handle_lease_type_custom, handle_lease_price, handle_lease_rooms,
    handle_lease_description, handle_lease_confirm, handle_contact_moderator, want_to_rent_callback, handle_help,
    ask_for_phone, ask_for_name, send_language_choice, handle_register_name, handle_register_age
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

TOKEN = "7675092570:AAHCTUauv0W9w2dl55ymiNh0tuQSKdb3kIo"  # замените на ваш реальный токен


def main():
    print('Запуск бота...')
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start_handler(message):
        try:
            user_id = message.from_user.id
            username = message.from_user.username
            profile = get_or_create_profile(username)

            # Проверяем, выбран ли уже язык
            if not profile.language:
                set_user_state(profile, "choose_language")
                send_language_choice(bot, user_id, profile)
                return

            # Если язык выбран, но пользователь не зарегистрирован
            if not profile.name and not profile.phone_number:
                set_user_state(profile, "register_name")
                ask_for_name(bot, user_id, profile)
                return

            # Пользователь зарегистрирован, показываем главное меню
            set_user_state(profile, "start")
            markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            markup.add(get_message(profile, 'rent'), get_message(profile, 'lease'))
            msg_key = 'welcome'
            bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)
        except Exception as e:
            print(f"Ошибка в start_handler: {e}")
            traceback.print_exc()

    # Обработчик callback-запросов для выбора языка
    @bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
    def callback_language_handler(call):
        try:
            user_id = call.from_user.id
            username = call.from_user.username
            profile = get_or_create_profile(username)
            data = call.data

            if data == 'lang_ru':
                profile.language = 'ru'
                profile.save()
                set_user_state(profile, "register_name")
                ask_for_name(bot, user_id, profile)
                print(f"Пользователь {username} выбрал Русский язык.")
            elif data == 'lang_uk':
                profile.language = 'uk'
                profile.save()
                set_user_state(profile, "register_name")
                ask_for_name(bot, user_id, profile)
                print(f"Пользователь {username} выбрал Украинский язык.")
            else:
                # Если получен неожиданный callback_data
                handle_help(bot, call.message, profile)
                print(f"Неизвестный выбор языка: {data} от пользователя {username}")

            # Удаляем inline клавиатуру после выбора
            bot.delete_message(chat_id=call.message.chat.id,
                message_id=call.message.message_id)

        except Exception as e:
            print(f"Ошибка в callback_language_handler: {e}")
            traceback.print_exc()
            bot.send_message(call.message.chat.id, "Произошла ошибка при выборе языка. Пожалуйста, попробуйте снова.")

    # Обработчик сообщений с контактной информацией
    @bot.message_handler(content_types=['contact'])
    def contact_handler(message):
        try:
            user_id = message.from_user.id
            username = message.from_user.username
            profile = get_or_create_profile(username)
            state = get_user_state(profile)

            if state == "register_phone":
                if message.contact is not None and message.contact.user_id == user_id:
                    phone_number = message.contact.phone_number
                    profile.phone_number = phone_number
                    profile.save()
                    set_user_state(profile, "start")
                    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                    markup.add(get_message(profile, 'rent'), get_message(profile, 'lease'))
                    msg_key = 'welcome'
                    bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)
                    print(f"Пользователь {username} зарегистрировал номер телефона: {phone_number}")
                else:
                    ask_for_phone(bot, user_id, profile)
            else:
                # Обработка других состояний, если требуется
                print(f"Получен контакт от пользователя {username}, но состояние: {state}")
        except Exception as e:
            print(f"Ошибка в contact_handler: {e}")
            traceback.print_exc()

    # Основной обработчик сообщений
    @bot.message_handler(func=lambda m: True, content_types=['photo', 'text'])
    def main_handler(message):
        try:
            user_id = message.from_user.id
            username = message.from_user.username
            profile = get_or_create_profile(username)
            state = get_user_state(profile)
            text = message.text.lower() if message.text else ""

            if message.content_type == 'text':
                print(f"Получено текстовое сообщение от {username}: {text}")
            elif message.content_type == 'photo':
                print(f"Получено фото от {username}")

            if state == "start":
                handle_start(bot, profile, message, text)
            elif state == "register_name":
                handle_register_name(bot, profile, message, text)
            elif state == "register_age":
                handle_register_age(bot, profile, message, text)
            elif state == "rent_choose_type":
                handle_rent_choose_type(bot, profile, message, text)
            elif state == "rent_choose_price":
                handle_rent_choose_price(bot, profile, message, text)
            elif state == "show_variants":
                handle_show_variants(bot, profile, message, text)
            elif state == "lease_photos":
                handle_lease_photos(bot, profile, message)
            elif state == "lease_type":
                handle_lease_type(bot, profile, message, text)
            elif state == "lease_type_custom":
                handle_lease_type_custom(bot, profile, message)
            elif state == "lease_price":
                handle_lease_price(bot, profile, message, text)
            elif state == "lease_rooms":
                handle_lease_rooms(bot, profile, message, text)
            elif state == "lease_description":
                handle_lease_description(bot, profile, message)
            elif state == "lease_confirm":
                handle_lease_confirm(bot, profile, message, text)
            elif state == "contact_moderator":
                handle_contact_moderator(bot, profile, message, text)
            else:
                handle_help(bot, message, profile)
        except Exception as e:
            print(f"Ошибка в main_handler: {e}")
            traceback.print_exc()

    # Обработчик callback-запросов для аренды недвижимости
    @bot.callback_query_handler(func=lambda call: call.data.startswith("rent_"))
    def callback_want_to_rent(call):
        try:
            user_id = call.from_user.id
            username = call.from_user.username
            profile = get_or_create_profile(username)
            want_to_rent_callback(bot, profile, call)
        except Exception as e:
            print(f"Ошибка в callback_want_to_rent: {e}")
            traceback.print_exc()

    # Запуск бота
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        traceback.print_exc()


class Command(BaseCommand):
    help = "Run the Telegram Bot"

    def handle(self, *args, **options):
        try:
            main()
        except Exception as e:
            traceback.print_exc()