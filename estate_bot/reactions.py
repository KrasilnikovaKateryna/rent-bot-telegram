import os
import re
import traceback

from django.db.models import Q
from telebot.types import (
    ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto, KeyboardButton
)

from .models import LeaseDraft, RealEstate, LeaseDraftPhoto, RealEstatePhoto
from .utils import set_user_state, get_message
from real_estate_tg_bot import settings

ADMIN_USER_ID = 811009969  # Замените на реальный ID администратора


def send_language_choice(bot, user_id, profile):
    """
    Отправляет сообщение с встроенными кнопками для выбора языка.
    """
    print("send_language_choice")
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Українська", callback_data='lang_uk'),
        InlineKeyboardButton("Русский", callback_data='lang_ru')
    )
    bot.send_message(
        user_id,
        "Якою мовою бажаєте продовжити? / На каком языке хотите продолжить?",
        reply_markup=markup
    )


def ask_for_name(bot, user_id, profile):
    """
    Запрашивает у пользователя ввод имени.
    """
    print("ask_for_name")
    msg_key = 'please_enter_name'
    bot.send_message(user_id, get_message(profile, msg_key), reply_markup=ReplyKeyboardRemove())


def handle_register_name(bot, profile, message, text):
    """
    Обрабатывает ввод имени пользователя.
    """
    print("handle_register_name")
    user_id = message.from_user.id
    if text.strip():
        profile.name = text.strip()
        profile.save()
        set_user_state(profile, "register_age")  # Переходим к запросу возраста
        ask_for_age(bot, user_id, profile)
        print(f"Пользователь {profile.username} зарегистрировал имя: {profile.name}")
    else:
        msg_key = 'please_enter_name'
        bot.send_message(user_id, get_message(profile, msg_key))


def ask_for_age(bot, user_id, profile):
    """
    Запрашивает у пользователя ввод возраста.
    """
    print("ask_for_age")
    msg_key = 'please_enter_age'
    bot.send_message(user_id, get_message(profile, msg_key), reply_markup=ReplyKeyboardRemove())


def handle_register_age(bot, profile, message, text):
    """
    Обрабатывает ввод возраста пользователя.
    """
    print("handle_register_age")
    user_id = message.from_user.id
    if text.strip().isdigit():
        age = int(text.strip())
        if 18 <= age <= 100:  # Проверка на разумный диапазон возраста
            profile.age = age
            profile.save()
            set_user_state(profile, "register_phone")
            ask_for_phone(bot, user_id, profile)
            print(f"Пользователь {profile.username} зарегистрировал возраст: {profile.age}")
        else:
            msg_key = 'invalid_age'
            bot.send_message(user_id, get_message(profile, msg_key))
    else:
        msg_key = 'invalid_age'
        bot.send_message(user_id, get_message(profile, msg_key))


def ask_for_phone(bot, user_id, profile):
    """
    Запрашивает у пользователя поделиться номером телефона через кнопку.
    """
    print("ask_for_phone")
    if profile.language == 'ru':
        button_text = "Поделиться номером с ботом"
        prompt_text = "Пожалуйста, поделитесь номером телефона:"
    else:
        button_text = "Поділитися номером з ботом"
        prompt_text = "Будь ласка, поділіться номером телефону:"

    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    contact_button = KeyboardButton(text=button_text, request_contact=True)
    markup.add(contact_button)
    msg_key = 'please_share_phone'
    bot.send_message(user_id, prompt_text, reply_markup=markup)


def handle_start(bot, profile, message, text):
    """
    Обрабатывает состояние 'start' - начальное меню после регистрации.
    """
    print("handle_start")
    user_id = message.from_user.id

    if text in [get_message(profile, 'rent'), "арендовать 🏠", "орендувати 🏠", "арендовать", "орендувати"]:
        print("rent")
        profile.rent_types = []
        profile.prices = []
        profile.last_shown_estate_id = None
        profile.save()
        set_user_state(profile, "rent_choose_type")
        send_rent_type_choice(bot, user_id, profile)
    elif text in [get_message(profile, 'lease'), "сдать 💵", "здати 💵", "здати", "сдать"]:
        print("lease")
        LeaseDraft.objects.filter(profile=profile).delete()
        LeaseDraft.objects.create(profile=profile)
        set_user_state(profile, "lease_photos")
        ask_to_load_photos(bot, user_id, profile)
    else:
        handle_help(bot, message, profile)


def send_rent_type_choice(bot, user_id, profile):
    """
    Отправляет пользователю выбор типа аренды.
    """
    print("send_rent_type_choice")
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    types = ["Квартира", "Дом", "Комната", "Другое", "Закончить"] if profile.language == 'ru' else ["Квартира", "Будинок", "Кімната", "Інше", "Завершити"]
    for i in range(0, len(types), 2):
        row_buttons = types[i:i + 2]
        markup.row(*row_buttons)
    msg_key = 'choose_rent_type'
    bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)


def handle_rent_choose_type(bot, profile, message, text):
    """
    Обрабатывает выбор типа аренды.
    """
    print("handle_rent_choose_type")
    user_id = message.from_user.id
    finish_keywords_ru = ["закончить", "Закончить"]
    finish_keywords_uk = ["завершити", "Завершити"]
    finish_keywords = finish_keywords_ru if profile.language == 'ru' else finish_keywords_uk

    if text not in finish_keywords:
        rent_types = profile.rent_types
        rent_types.append(text)
        profile.rent_types = rent_types
        profile.save()
        msg_key = 'rent_prompt'
        bot.send_message(user_id, get_message(profile, msg_key))
    elif text in finish_keywords:
        set_user_state(profile, "rent_choose_price")
        send_rent_price_choice(bot, user_id, profile)
    else:
        handle_help(bot, message, profile)


def send_rent_price_choice(bot, user_id, profile):
    """
    Отправляет пользователю выбор диапазона цен.
    """
    print("send_rent_price_choice")
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    prices = ["<5000", "5000-10000", "10000-15000", ">15000", "Закончить"] if profile.language == 'ru' \
        else ["<5000", "5000-10000", "10000-15000", ">15000", "Завершити"]
    for i in range(0, len(prices), 2):
        row_buttons = prices[i:i + 2]
        markup.row(*row_buttons)
    msg_key = 'choose_price_range'
    bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)


def handle_rent_choose_price(bot, profile, message, text):
    """
    Обрабатывает выбор диапазона цен для аренды.
    """
    print("handle_rent_choose_price")
    user_id = message.from_user.id
    finish_keywords_ru = ["закончить", "Закончить"]
    finish_keywords_uk = ["завершити", "Завершити"]
    finish_keywords = finish_keywords_ru if profile.language == 'ru' else finish_keywords_uk

    valid_prices_ru = ["<5000", "5000-10000", "10000-15000", ">15000", "закончить"]
    valid_prices_uk = ["<5000", "5000-10000", "10000-15000", ">15000", "завершити"]
    valid_prices = valid_prices_ru if profile.language == 'ru' else valid_prices_uk

    if text.lower() not in [word.lower() for word in valid_prices]:
        handle_help(bot, message, profile)
        return

    if text.lower() not in ["закончить", "завершити"]:
        prices = profile.prices
        prices.append(text)
        profile.prices = prices
        profile.save()
        msg_key = 'rent_prompt'
        bot.send_message(user_id, get_message(profile, msg_key))
    else:
        set_user_state(profile, "show_variants")
        show_variants(bot, profile, user_id)


def get_filtered_estates(profile):
    """
    Фильтрует объекты недвижимости на основе предпочтений пользователя.
    """
    rent_types = profile.rent_types
    prices = profile.prices

    qs = RealEstate.objects.filter(is_for_rent=True)
    if rent_types:
        qs = qs.filter(estate_type__in=rent_types)

    price_filter = Q()
    for pr in prices:
        if pr == "<5000":
            price_filter |= Q(price__lt=5000)
        elif pr == "5000-10000":
            price_filter |= Q(price__gte=5000, price__lte=10000)
        elif pr == "10000-15000":
            price_filter |= Q(price__gte=10000, price__lte=15000)
        elif pr == ">15000":
            price_filter |= Q(price__gt=15000)

    qs = qs.filter(price_filter).distinct().order_by('id')  # Упорядочиваем по id для последовательности
    return qs


def show_variants(bot, profile, user_id):
    """
    Отображает варианты недвижимости, соответствующие запросу пользователя.
    """
    print("show_variants")
    qs = get_filtered_estates(profile)
    count = qs.count()
    if count == 0:
        msg_key = 'no_options_found'
        bot.send_message(user_id, get_message(profile, msg_key))
        markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(get_message(profile, 'modify_search'), get_message(profile, 'lease_property'))
        msg_key = 'continue_search'
        bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)
        return

    profile.last_shown_estate_id = None  # Сбрасываем маркер
    profile.save()

    show_single_variant(bot, profile, user_id)


def show_single_variant(bot, profile, user_id):
    """
    Отображает один вариант недвижимости.
    """
    qs = get_filtered_estates(profile)
    last_id = profile.last_shown_estate_id

    if last_id:
        estate_qs = qs.filter(id__gt=last_id).order_by('id').first()
    else:
        estate_qs = qs.first()

    if not estate_qs:
        msg_key = 'no_options_found'
        bot.send_message(user_id, get_message(profile, msg_key))
        markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(get_message(profile, 'modify_search'), get_message(profile, 'lease_property'))
        msg_key = 'continue_search'
        bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)
        return

    # Обновляем маркер
    profile.last_shown_estate_id = estate_qs.id
    profile.save()

    real_estate = estate_qs
    photos = RealEstatePhoto.objects.filter(real_estate=real_estate)

    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton(get_message(profile, 'rent'), callback_data=f"rent_{real_estate.id}"))

    description = real_estate.description

    msg = (f"⬆️\n{get_message(profile, 'type')}: {real_estate.estate_type}\n"
           f"{get_message(profile, 'price')}: {real_estate.price}\n"
           f"{get_message(profile, 'rooms')}: {real_estate.rooms}\n\n{description}")

    media_group = [InputMediaPhoto(photo.image) for photo in photos]

    if media_group:
        bot.send_media_group(user_id, media_group)
    bot.send_message(user_id, msg, reply_markup=inline_kb)

    # Кнопки для навигации
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(get_message(profile, 'next'), get_message(profile, 'modify_search'))
    bot.send_message(user_id, get_message(profile, 'choose_action'), reply_markup=markup)


def handle_show_variants(bot, profile, message, text):
    """
    Обрабатывает навигацию по вариантам недвижимости.
    """
    print("handle_show_variants")
    user_id = message.from_user.id
    if (profile.language == 'ru' and text.lower() == "дальше ➡️") or \
       (profile.language == 'uk' and text.lower() == "далі ➡️"):
        show_single_variant(bot, profile, user_id)
    elif (profile.language == 'ru' and text.lower() == "изменить параметры поиска 🔍") or \
         (profile.language == 'uk' and text.lower() == "змінити параметри пошуку 🔍"):
        profile.rent_types = []
        profile.prices = []
        profile.last_shown_estate_id = None
        profile.save()
        set_user_state(profile, "rent_choose_type")
        send_rent_type_choice(bot, user_id, profile)
    elif (profile.language == 'ru' and text.lower() == "сдать недвижимость 🏠") or \
         (profile.language == 'uk' and text.lower() == "здати нерухомість 🏠"):
        LeaseDraft.objects.filter(profile=profile).delete()
        LeaseDraft.objects.create(profile=profile)
        set_user_state(profile, "lease_photos")
        ask_to_load_photos(bot, user_id, profile)
    else:
        handle_help(bot, message, profile)


def want_to_rent_callback(bot, profile, call):
    """
    Обрабатывает нажатие кнопки "Арендовать" под вариантом недвижимости.
    """
    print("want_to_rent_callback")
    user_id = call.from_user.id
    username = profile.username
    name = profile.name
    phone = profile.phone_number
    age = profile.age

    msg_key = 'notify_moderator'
    bot.send_message(user_id, get_message(profile, msg_key))

    description = extract_description(call.message.text, profile.language)

    current_real_estate = RealEstate.objects.filter(description=description).last()

    if current_real_estate:
        estate_owner = current_real_estate.owner
        owner_username = estate_owner.username
        owner_name = estate_owner.name
        owner_phone = estate_owner.phone_number
        owner_age = estate_owner.age

        photo_objects = RealEstatePhoto.objects.filter(real_estate=current_real_estate)
        photos = [obj.image for obj in photo_objects]

        media_group = [InputMediaPhoto(photo) for photo in photos]

        renter = f"{username}, ім'я {name}, {phone}, вік {age}"
        owner = f"{owner_username}, ім'я {owner_name}, {owner_phone}, вік {owner_age}"

        message_to_admin = f"@{renter} хоче орендувати нерухомість у @{owner}"

        if media_group:
            media_group[0].caption = message_to_admin
            bot.send_media_group(ADMIN_USER_ID, media_group)
        else:
            bot.send_message(ADMIN_USER_ID, message_to_admin)


def handle_lease_photos(bot, profile, message):
    """
    Обрабатывает загрузку фотографий для сдачи недвижимости.
    """
    print("handle_lease_photos")
    user_id = message.from_user.id
    draft = LeaseDraft.objects.filter(profile=profile).last()

    done_text = "Готово ✅"
    back_text = "Назад ↩️"


    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(done_text, back_text)

    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        filename = f"lease_photos/{draft.id}_{file_id}.jpg"
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        LeaseDraftPhoto.objects.create(lease_draft=draft, image=filename)

        bot.send_message(user_id, get_message(profile, 'added_photo'))

    elif message.content_type == 'text':
        text = message.text.lower()
        if text == "готово ✅":
            if not LeaseDraftPhoto.objects.filter(lease_draft=draft).exists():
                bot.send_message(
                    user_id,
                    get_message(profile, 'lease_photo_prompt'),
                    reply_markup=markup
                )
                return
            set_user_state(profile, "lease_type")
            send_lease_type_choice(bot, user_id, profile)
        elif text == "назад ↩️":
            draft.delete()
            set_user_state(profile, "start")
            markup_main = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            markup_main.add(get_message(profile, 'rent'), get_message(profile, 'lease'))
            bot.send_message(user_id, get_message(profile, 'choose_action'), reply_markup=markup_main)
        else:
            handle_help(bot, message, profile)


def send_lease_type_choice(bot, user_id, profile):
    """
    Отправляет пользователю выбор типа недвижимости для сдачи.
    """
    print("send_lease_type_choice")
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    types = ["Квартира", "Дом", "Комната", "Другое"] if profile.language == 'ru' else ["Квартира", "Будинок", "Кімната", "Інше"]
    markup.add(*types)
    msg_key = 'lease_type_prompt'
    bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)


def handle_lease_type(bot, profile, message, text):
    """
    Обрабатывает выбор типа недвижимости для сдачи.
    """
    print("handle_lease_type")
    user_id = message.from_user.id
    draft = LeaseDraft.objects.filter(profile=profile).last()
    valid_types_ru = ["квартира", "дом", "комната"]
    valid_types_uk = ["квартира", "будинок", "кімната"]

    if (profile.language == 'ru' and text.lower() in valid_types_ru) or \
       (profile.language == 'uk' and text.lower() in valid_types_uk):
        draft.estate_type = text.lower()
        draft.save()
        set_user_state(profile, "lease_price")
        msg_key = 'lease_price_prompt'
        bot.send_message(user_id, get_message(profile, msg_key), reply_markup=ReplyKeyboardRemove())
    elif (profile.language == 'ru' and text.lower() == "другое") or \
         (profile.language == 'uk' and text.lower() == "інше"):
        set_user_state(profile, "lease_type_custom")
        msg_key = 'lease_type_custom_prompt'
        bot.send_message(user_id, get_message(profile, msg_key), reply_markup=ReplyKeyboardRemove())
    else:
        handle_help(bot, message, profile)


def handle_lease_type_custom(bot, profile, message):
    """
    Обрабатывает ввод пользовательского типа недвижимости для сдачи.
    """
    print("handle_lease_type_custom")
    user_id = message.from_user.id
    draft = LeaseDraft.objects.filter(profile=profile).last()
    custom_type = message.text.strip()
    if custom_type:
        draft.estate_type = custom_type
        draft.save()
        set_user_state(profile, "lease_price")
        msg_key = 'lease_price_prompt'
        bot.send_message(user_id, get_message(profile, msg_key), reply_markup=ReplyKeyboardRemove())
    else:
        handle_help(bot, message, profile)


def handle_lease_price(bot, profile, message, text):
    """
    Обрабатывает ввод цены за месяц для сдачи недвижимости.
    """
    print("handle_lease_price")
    user_id = message.from_user.id
    draft = LeaseDraft.objects.filter(profile=profile).last()
    try:
        price = float(message.text)
        draft.price = price
        draft.save()
        set_user_state(profile, "lease_rooms")
        msg_key = 'lease_rooms_prompt'
        bot.send_message(user_id, get_message(profile, msg_key))
    except ValueError:
        handle_help(bot, message, profile)


def handle_lease_rooms(bot, profile, message, text):
    """
    Обрабатывает ввод количества комнат для сдачи недвижимости.
    """
    print("handle_lease_rooms")
    user_id = message.from_user.id
    draft = LeaseDraft.objects.filter(profile=profile).last()
    try:
        rooms = int(message.text)
        draft.rooms = rooms
        draft.save()
        set_user_state(profile, "lease_description")
        msg_key = 'lease_description_prompt'
        bot.send_message(user_id, get_message(profile, msg_key))
    except ValueError:
        handle_help(bot, message, profile)


def handle_lease_description(bot, profile, message):
    """
    Обрабатывает ввод описания недвижимости для сдачи.
    """
    print("handle_lease_description")
    user_id = message.from_user.id
    draft = LeaseDraft.objects.filter(profile=profile).last()
    draft.description = message.text
    draft.save()
    set_user_state(profile, "lease_confirm")

    description = draft.description
    preview_msg = (f"{get_message(profile, 'type')}: {draft.estate_type}\n"
                   f"{get_message(profile, 'price')}: {draft.price}\n"
                   f"{get_message(profile, 'rooms')}: {draft.rooms}\n\n{description}")

    photos = LeaseDraftPhoto.objects.filter(lease_draft=draft)
    if photos.exists():
        media_group = [InputMediaPhoto(photo.image) for photo in photos]
        media_group[0].caption = preview_msg
        bot.send_media_group(user_id, media_group)
    else:
        bot.send_message(user_id, preview_msg)

    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if profile.language == 'ru':
        markup.add("Подтвердить ✅", "Отмена ❌")
    else:
        markup.add("Підтвердити ✅", "Скасувати ❌")
    msg_key = 'lease_confirm_prompt'
    bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)


def handle_lease_confirm(bot, profile, message, text):
    """
    Обрабатывает подтверждение или отмену создания объявления о сдаче недвижимости.
    """
    print("handle_lease_confirm")
    user_id = message.from_user.id
    if (profile.language == 'ru' and text.lower() == "подтвердить ✅") or \
       (profile.language == 'uk' and text.lower() == "підтвердити ✅"):
        if profile.free_ads_remaining > 0:
            profile.free_ads_remaining -= 1
            profile.save()

            draft = LeaseDraft.objects.filter(profile=profile).last()
            estate_type = draft.estate_type
            price = draft.price
            rooms = draft.rooms
            desc = draft.description

            estate = RealEstate.objects.create(
                owner=profile,
                estate_type=estate_type,
                price=price,
                rooms=rooms,
                description=desc,
                is_for_rent=True
            )


            for p in LeaseDraftPhoto.objects.filter(lease_draft=draft):
                RealEstatePhoto.objects.create(real_estate=estate, image=p.image)
            draft.delete()

            markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            markup.add(get_message(profile, 'rent'), get_message(profile, 'lease'))

            msg_key = 'lease_confirm_success'
            bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)
            set_user_state(profile, "start")
            print(f"Пользователь {profile.username} подтвердил объявление о сдаче недвижимости.")
        else:
            set_user_state(profile, "contact_moderator")
            markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            if profile.language == 'ru':
                markup.add("Связаться с модератором", "Отмена")
            else:
                markup.add("Зв'язатися з модератором", "Скасувати")
            msg_key = 'lease_confirm_limit'
            bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)
            print(f"Пользователь {profile.username} попытался создать объявление, но достиг лимита.")
    elif (profile.language == 'ru' and text.lower() == "отмена ❌") or \
         (profile.language == 'uk' and text.lower() == "скасувати ❌"):
        LeaseDraft.objects.filter(profile=profile).delete()
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(get_message(profile, 'rent'), get_message(profile, 'lease'))
        msg_key = 'lease_cancelled'
        bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)
        set_user_state(profile, "start")
        print(f"Пользователь {profile.username} отменил создание объявления о сдаче недвижимости.")
    else:
        handle_help(bot, message, profile)


def handle_contact_moderator(bot, profile, message, text):
    """
    Обрабатывает обращение пользователя к модератору.
    """
    print("handle_contact_moderator")
    user_id = message.from_user.id

    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(get_message(profile, 'rent'), get_message(profile, 'lease'))

    if (profile.language == 'ru' and text.lower() == "связаться с модератором") or \
       (profile.language == 'uk' and text.lower() == "зв'язатися з модератором"):
        msg_key = 'notify_moderator'
        bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)
        set_user_state(profile, "start")
        print(f"Пользователь {profile.username} связался с модератором.")
    elif (profile.language == 'ru' and text.lower() == "отмена") or \
         (profile.language == 'uk' and text.lower() == "скасувати"):
        LeaseDraft.objects.filter(profile=profile).delete()
        set_user_state(profile, "start")
        msg_key = 'lease_cancelled'
        bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)
        print(f"Пользователь {profile.username} отменил обращение к модератору.")
    else:
        handle_help(bot, message, profile)


def handle_help(bot, message, profile):
    """
    Обрабатывает неизвестные команды или сообщения.
    """
    user_id = message.from_user.id
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(get_message(profile, 'rent'), get_message(profile, 'lease'))
    msg_key = 'unknown_command'
    bot.send_message(user_id, get_message(profile, msg_key), reply_markup=markup)
    print(f"Пользователь {profile.username} отправил неизвестную команду или сообщение.")


def ask_to_load_photos(bot, user_id, profile):
    """
    Запрашивает у пользователя загрузку фотографий недвижимости для сдачи.
    """
    done_text = "Готово ✅"
    back_text = "Назад ↩️"

    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(done_text, back_text)
    msg_key = 'lease_photo_prompt'
    bot.send_message(
        user_id,
        get_message(profile, msg_key),
        reply_markup=markup
    )


def extract_description(text, language):
    """
    Извлекает описание недвижимости из текста на основе языка.
    """
    if language == 'ru':
        pattern = r"(?:Тип: .+|Цена: .+|Комнат: .+)\s*\n+(.*)"
    elif language == 'uk':
        pattern = r"(?:Тип: .+|Ціна: .+|Кімнат: .+)\s*\n+(.*)"
    else:
        # По умолчанию используем русский
        pattern = r"(?:Тип: .+|Цена: .+|Комнат: .+)\s*\n+(.*)"

    match = re.search(pattern, text, re.DOTALL)
    if match:
        description = match.group(1).strip()
        return description
    return "No description found"