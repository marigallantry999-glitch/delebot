import json
from datetime import datetime
from pathlib import Path
from aiogram import Bot, Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from config import IMAGES_DIR, ADMIN_ID, BOT_TOKEN
from core.profile import (
    load_profile, create_profile, save_profile, 
    add_diamonds, spend_diamonds, update_streak,
    save_support_request, get_pending_requests, 
    mark_request_answered, cancel_user_request
)
from core.exercises import get_exercise_by_rule, check_exercise_answer
from core.session import get_next_image, process_daily_description

# Создаём бота
bot = Bot(token=BOT_TOKEN)
router = Router()

# ---- СОСТОЯНИЯ ----
class RegistrationState(StatesGroup):
    waiting_for_name = State()

class DailyState(StatesGroup):
    waiting_for_description = State()
    waiting_for_exercise = State()

class ExerciseState(StatesGroup):
    waiting_for_answer = State()


# ---- АВАТАР ----
def get_avatar():
    avatar_path = Path(IMAGES_DIR) / "hola" / "avatar.jpg"
    if avatar_path.exists():
        return str(avatar_path)
    return None


# ---- /START И /INICIO - РЕГИСТРАЦИЯ ----
@router.message(Command("start"))
@router.message(Command("inicio"))
async def inicio_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    profile = load_profile(user_id)
    
    # Если пользователь уже зарегистрирован
    if profile.get("name") and profile.get("name") != f"User_{user_id}":
        await message.answer(
            f"👋 С возвращением, {profile['name']}! 💫\n\n"
            f"📊 Твой стрик: {profile.get('streak', 0)} дней\n"
            f"💎 Алмазов: {profile.get('diamonds', 0)}\n\n"
            f"Готова описать сегодняшнюю картинку? Напиши /diario 🎯\n\n"
            f"Или посмотри инструкцию: /instrucciones"
        )
        return
    
    avatar_path = get_avatar()
    
    welcome_text = (
        "¡Hola! 👋\n\n"
        "Меня зовут Лера. Я преподаватель испанского, я помогу без стресса отработать испанскую грамматику и подготовиться к части экзамена с описанием изображений\n\n"
        "Как я могу к тебе обращаться? 💫"
    )
    
    if avatar_path:
        photo = FSInputFile(avatar_path)
        await message.answer_photo(photo, caption=welcome_text, parse_mode="Markdown")
    else:
        await message.answer(welcome_text, parse_mode="Markdown")
    
    await state.set_state(RegistrationState.waiting_for_name)


@router.message(RegistrationState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Пожалуйста, введи имя (минимум 2 символа)")
        return
    
    user_id = message.from_user.id
    profile = create_profile(user_id, name)
    profile["address_form"] = "tu"  # Всегда на "ты"
    save_profile(user_id, profile)
    
    await message.answer(
        f"¡Perfecto! ✅\n\n"
        f"Приятно познакомиться, {name}! ¡Encantada!\n\n"
        f"Теперь я буду к тебе обращаться на 'ты'.\n\n"
        f"Знаешь, у меня такое чувство, что мы уже подружились. И это только начало!\n\n"
        f"Каждый день в 19:00 я буду присылать тебе картинку для описания. "
        f"Ты описываешь — я нахожу ошибки и даю упражнения. "
        f"Всё просто и быстро — пара минут в день.\n\n"
        f"Есть желание начать прямо сейчас? Напиши /diario 🎯\n\n"
        f"Или посмотри инструкцию: /instrucciones"
    )
    await state.clear()


# ---- /INSTRUCCIONES - ИНСТРУКЦИЯ ----
@router.message(Command("instrucciones"))
async def instrucciones_command(message: types.Message):
    user_id = message.from_user.id
    profile = load_profile(user_id)
    name = profile.get('name', 'Друг')
    
    instrucciones_text = (
        f"📖 **Инструкция для {name}**\n\n"
        f"Я — Лера, твой персональный тренер по испанскому. Вот как мы будем работать:\n\n"
        f"**1. Начать занятие**\n"
        f"Напиши /diario — я пришлю картинку для описания\n\n"
        f"**2. Описать картинку**\n"
        f"Используй структуру DELE A2 (она на испанском):\n"
        f"1️⃣ ¿Quién aparece en la imagen?\n"
        f"2️⃣ ¿Qué hace un personaje?\n"
        f"3️⃣ ¿Qué hace el otro personaje?\n"
        f"4️⃣ ¿Por qué tiene razón el primero?\n"
        f"5️⃣ ¿Por qué tiene razón el segundo?\n"
        f"6️⃣ ¿Cuál es tu opinión?\n"
        f"7️⃣ ¿Y tú qué piensas? (opcional)\n\n"
        f"**3. Получить слова**\n"
        f"Под картинкой есть кнопка «Дай слова» — нажми, если нужны подсказки\n\n"
        f"**4. Исправить ошибки**\n"
        f"Я найду ошибки и дам упражнения — просто отвечай на них\n\n"
        f"**5. Смотреть прогресс**\n"
        f"/estadisticas — твоя статистика\n"
        f"/perfil — твой профиль\n"
        f"/menu — главное меню\n\n"
        f"**6. Задать вопрос**\n"
        f"Просто напиши мне текст — я передам команде, и тебе ответят\n"
        f"/cancelar_solicitud — отменить запрос\n\n"
        f"**7. Помощь**\n"
        f"/ayuda — помощь и поддержка\n\n"
        f"🔥 **Главное правило:** занимайся каждый день, и ты сдашь DELE A2 на 100%!\n\n"
        f"¡Vamos! 💫"
    )
    
    sent_msg = await message.answer(instrucciones_text, parse_mode="Markdown")
    
    # Закрепляем сообщение
    try:
        await sent_msg.pin()
    except Exception as e:
        print(f"⚠️ Не удалось закрепить сообщение: {e}")


# ---- /DIARIO - ЕЖЕДНЕВНАЯ СЕССИЯ ----
@router.message(Command("diario"))
async def diario_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    profile = load_profile(user_id)
    
    if not profile.get("name") or profile.get("name") == f"User_{user_id}":
        await message.answer("Сначала познакомимся! Напиши /inicio 💫")
        return
    
    image_data = get_next_image(user_id)
    if not image_data:
        await message.answer(
            "📸 Ты уже описала все картинки! 🎉\n"
            "Ты отлично поработала. Скоро добавлю новые.\n"
            "А пока можешь повторить пройденное или подождать обновлений. 💫"
        )
        return
    
    profile['current_session'] = {
        "type": "daily",
        "step": "awaiting_description",
        "image_name": image_data['name'],
        "started_at": datetime.now().isoformat()
    }
    save_profile(user_id, profile)
    
    caption = (
        f"Ого! {profile.get('name', '')}! Ты пришла! Я уже заждалась! 🔥\n\n"
        f"У меня для тебя сегодня кое-что интересное. Посмотри на эту картинку...\n\n"
        f"📸 **Describe lo que ves.**\n\n"
        f"**Estructura DELE A2:**\n"
        f"1️⃣ ¿Quién aparece en la imagen?\n"
        f"2️⃣ ¿Qué hace un personaje?\n"
        f"3️⃣ ¿Qué hace el otro personaje?\n"
        f"4️⃣ ¿Por qué tiene razón el primero?\n"
        f"5️⃣ ¿Por qué tiene razón el segundo?\n"
        f"6️⃣ ¿Cuál es tu opinión?\n"
        f"7️⃣ ¿Y tú qué piensas? (opcional)\n\n"
        f"✍️ Escribe tu descripción en español."
    )
    
    photo = FSInputFile(image_data['image_path'])
    await message.answer_photo(photo, caption=caption, parse_mode="Markdown")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Dame palabras", callback_data="give_lexis")]
    ])
    
    await state.update_data(image_name=image_data['name'], lexis=image_data['palabras'])
    await message.answer("Si necesitas palabras de ayuda, presiona el botón.", reply_markup=keyboard)
    await message.answer("✍️ Espero tu descripción...")
    await state.set_state(DailyState.waiting_for_description)


@router.callback_query(F.data == "give_lexis")
async def give_lexis(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lexis = data.get('lexis', '')
    if lexis:
        await callback.message.answer(f"📝 Palabras de ayuda:\n\n{lexis}")
    else:
        await callback.message.answer("⚠️ Las palabras aún no están cargadas")
    await callback.answer()


@router.message(StateFilter(DailyState.waiting_for_description))
async def process_description(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_answer = message.text
    
    if not user_answer:
        await message.answer("Por favor, escribe tu descripción.")
        return
    
    data = await state.get_data()
    image_name = data.get('image_name')
    
    if not image_name:
        await message.answer("⚠️ Что-то пошло не так. Начни заново с /diario")
        await state.clear()
        return
    
    await message.answer("⏳ Analizando tu respuesta...")
    
    result = await process_daily_description(user_id, user_answer, image_name)
    
    if result.get("error"):
        await message.answer(f"⚠️ {result['error']}")
        await state.clear()
        return
    
    errors = result.get("errors", [])
    feedback = result.get("feedback", "¡Bien! Revisa tus errores abajo.")
    profile = load_profile(user_id)
    name = profile.get('name', '')
    
    if errors:
        error_text = f"{feedback}\n\n❌ **Errores en la descripción:**\n\n"
        for i, error in enumerate(errors[:3], 1):
            error_text += f"{i}. *{error.get('rule', 'desconocido')}*\n"
            error_text += f"   ✏️ Tú escribiste: {error.get('sentence', '')}\n"
            error_text += f"   ✅ Correcto: {error.get('suggestion', '')}\n\n"
        
        await message.answer(error_text, parse_mode="Markdown")
        
        for i, error in enumerate(errors[:3], 1):
            rule = error.get('rule')
            exercise = get_exercise_by_rule(rule)
            if exercise:
                await message.answer(
                    f"📝 **Ejercicio {i} ({rule})**\n"
                    f"{exercise.get('question', '')}\n\n"
                    f"Escribe tu respuesta:",
                    parse_mode="Markdown"
                )
                await state.update_data(
                    current_exercise=exercise,
                    exercise_index=i,
                    total_exercises=len(errors[:3])
                )
                await state.set_state(ExerciseState.waiting_for_answer)
                return
        
        await show_daily_reward(message, user_id)
    else:
        await message.answer(
            f"{name}!!! 🎉\n\n"
            f"¡Eres una maga! ¡Ni un solo error! ¡Este progreso es increíble! ❤️\n\n"
            f"¡Recibes tu copa del día! 🏆\n\n"
            f"Mañana habrá un nuevo desafío. ¡Ya tengo algo especial para ti! ¡Sé que puedes! 💫"
        )
        await show_daily_reward(message, user_id)
    
    await state.clear()


@router.message(StateFilter(ExerciseState.waiting_for_answer))
async def process_exercise_answer(message: types.Message, state: FSMContext):
    user_answer = message.text
    data = await state.get_data()
    exercise = data.get('current_exercise')
    exercise_index = data.get('exercise_index', 1)
    total = data.get('total_exercises', 1)
    user_id = message.from_user.id
    profile = load_profile(user_id)
    name = profile.get('name', '')
    
    if not exercise:
        await message.answer("⚠️ Ejercicio no encontrado. Empieza de nuevo con /diario")
        await state.clear()
        return
    
    is_correct = check_exercise_answer(exercise, user_answer)
    
    if is_correct:
        await message.answer(
            f"¡Perfecto! 😍 ¡Eres increíble! ¡Ni un error en el ejercicio!\n\n"
            f"¿Ves? Puedes hacerlo. ¡Siempre supe que podías! 💫\n\n"
            f"¡Sigue así! 🌟"
        )
        add_diamonds(user_id, 3)
    else:
        correct_answer = exercise.get('answer', '')
        await message.answer(
            f"¡Ay, {name}! ❤️\n\n"
            f"No pasa nada. ¡Incluso yo me equivoco a veces!\n\n"
            f"Respuesta correcta: **{correct_answer}**\n\n"
            f"¿Intentamos de nuevo? ¡Creo en ti! Solo fue un pequeño despiste, es normal. 💪"
        )
    
    await show_daily_reward(message, user_id)
    await state.clear()


async def show_daily_reward(message: types.Message, user_id: int):
    profile = load_profile(user_id)
    streak = profile.get('streak', 0)
    diamonds = profile.get('diamonds', 0)
    name = profile.get('name', '')
    
    await message.answer(
        f"🏆 {name}! ¡Recibiste tu copa del día!\n\n"
        f"🔥 Racha: {streak} días\n"
        f"💎 Diamantes: {diamonds}\n\n"
        f"¿Sabes lo mejor? Cada día te vuelves más fuerte. ¡Y yo lo veo!\n\n"
        f"¡Sigue así! ¡Eres fuego! 🔥"
    )


# ---- /MENU ----
@router.message(Command("menu"))
async def menu_command(message: types.Message):
    user_id = message.from_user.id
    profile = load_profile(user_id)
    name = profile.get('name', 'Amigo')
    
    menu_text = (
        f"📋 **Menú principal**\n\n"
        f"👤 {name}\n"
        f"📊 Racha: {profile.get('streak', 0)} días\n"
        f"💎 Diamantes: {profile.get('diamonds', 0)}\n\n"
        f"Comandos disponibles:\n"
        f"/diario — nueva imagen\n"
        f"/instrucciones — instrucciones\n"
        f"/estadisticas — mi estadística\n"
        f"/perfil — mi perfil\n"
        f"/ayuda — ayuda y soporte"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Empezar clase", callback_data="start_daily")],
        [InlineKeyboardButton(text="📖 Instrucciones", callback_data="show_instrucciones")],
        [InlineKeyboardButton(text="📊 Mi estadística", callback_data="show_stats")],
        [InlineKeyboardButton(text="❓ Ayuda", callback_data="show_help")]
    ])
    
    await message.answer(menu_text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "start_daily")
async def start_daily_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await diario_command(callback.message, state)


@router.callback_query(F.data == "show_instrucciones")
async def show_instrucciones_callback(callback: types.CallbackQuery):
    await callback.answer()
    await instrucciones_command(callback.message)


@router.callback_query(F.data == "show_stats")
async def show_stats_callback(callback: types.CallbackQuery):
    await callback.answer()
    await estadisticas_command(callback.message)


@router.callback_query(F.data == "show_help")
async def show_help_callback(callback: types.CallbackQuery):
    await callback.answer()
    await ayuda_command(callback.message)


# ---- /ESTADISTICAS ----
@router.message(Command("estadisticas"))
async def estadisticas_command(message: types.Message):
    user_id = message.from_user.id
    profile = load_profile(user_id)
    
    stats_text = (
        f"📊 **Tu estadística**\n\n"
        f"👤 Nombre: {profile.get('name', 'No especificado')}\n"
        f"📅 Creado: {profile.get('created_at', '')[:10]}\n"
        f"🔥 Racha: {profile.get('streak', 0)} días\n"
        f"💎 Diamantes: {profile.get('diamonds', 0)}\n"
        f"📸 Imágenes descritas: {len(profile.get('used_images', []))}\n"
        f"📝 Ejercicios totales: {profile.get('stats', {}).get('exercises_done', 0)}\n"
        f"🎙️ Por voz: {profile.get('stats', {}).get('voice_count', 0)}\n"
        f"✍️ Por texto: {profile.get('stats', {}).get('text_count', 0)}\n"
        f"❌ Errores en curso: {len(profile.get('card_errors', []))}"
    )
    
    await message.answer(stats_text, parse_mode="Markdown")


# ---- /PERFIL ----
@router.message(Command("perfil"))
async def perfil_command(message: types.Message):
    user_id = message.from_user.id
    profile = load_profile(user_id)
    subscription = "trial" if profile.get('subscription_status') == 'trial' else "activa"
    
    profile_text = (
        f"👤 **Mi perfil**\n\n"
        f"Nombre: {profile.get('name', 'No especificado')}\n"
        f"Tratamiento: tú\n"
        f"Nivel: A2\n"
        f"Suscripción: {subscription}\n"
        f"🔥 Racha: {profile.get('streak', 0)} días\n"
        f"💎 Diamantes: {profile.get('diamonds', 0)}\n"
        f"📸 Imágenes descritas: {len(profile.get('used_images', []))}\n"
        f"❌ Errores en curso: {len(profile.get('card_errors', []))}"
    )
    
    await message.answer(profile_text, parse_mode="Markdown")


# ---- /AYUDA - ПОМОЩЬ ----
@router.message(Command("ayuda"))
async def ayuda_command(message: types.Message):
    user_id = message.from_user.id
    profile = load_profile(user_id)
    name = profile.get('name', 'Amigo')
    
    ayuda_text = (
        f"{name}! ¡Claro que te ayudo! 💫\n\n"
        f"Todo es muy simple:\n"
        f"1. /inicio — nos conocemos\n"
        f"2. /diario — te doy una imagen\n"
        f"3. Describe la imagen — encuentro errores y doy ejercicios\n"
        f"4. Repite cada día — ¡y apruebas el DELE al 100%!\n\n"
        f"Si tienes una pregunta o problema — simplemente escríbeme. "
        f"Lo enviaré al equipo y te responderán pronto.\n\n"
        f"Si quieres cancelar tu solicitud — escribe /cancelar_solicitud\n\n"
        f"¡Vamos! 💫"
    )
    
    await message.answer(ayuda_text)


# ---- /CANCELAR_SOLICITUD ----
@router.message(Command("cancelar_solicitud"))
async def cancelar_solicitud_command(message: types.Message):
    user_id = message.from_user.id
    
    if cancel_user_request(user_id):
        await message.answer(
            "¡Perfecto! He cancelado tu solicitud al equipo de soporte. "
            "Si cambias de opinión — ¡solo escríbeme! 💫"
        )
    else:
        await message.answer(
            "No tienes solicitudes activas de soporte. "
            "Si quieres hacer una pregunta — ¡solo escríbeme! 💫"
        )


# ---- /RESPONDER - ТОЛЬКО ДЛЯ АДМИНА ----
@router.message(Command("responder"))
async def responder_command(message: types.Message):
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer("⛔ No tienes permiso para usar este comando.")
        return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "❌ Formato del comando:\n"
            "/responder <user_id> <texto de respuesta>\n\n"
            "Ejemplo:\n"
            "/responder 123456789 ¡Hola! Gracias por tu pregunta."
        )
        return
    
    try:
        target_user_id = int(parts[1])
        reply_text = parts[2]
    except ValueError:
        await message.answer("❌ Formato incorrecto de user_id. Debe ser un número.")
        return
    
    try:
        await bot.send_message(
            target_user_id,
            f"¡Hola! Soy Lera. Me pasaron tu pregunta y quiero responderte:\n\n"
            f"{reply_text}\n\n"
            f"Si tienes más preguntas — ¡solo escríbeme! Siempre estoy aquí. 💫"
        )
        
        mark_request_answered(target_user_id)
        
        await message.answer(f"✅ Respuesta enviada a {target_user_id}")
    except Exception as e:
        await message.answer(f"❌ Error al enviar: {e}")


# ---- НЕПОНЯТНЫЕ СООБЩЕНИЯ ----
@router.message()
async def handle_unknown_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    
    if text and text.startswith('/'):
        return
    
    current_state = await state.get_state()
    if current_state in ['DailyState:waiting_for_description', 'ExerciseState:waiting_for_answer']:
        return
    
    if text and len(text.strip()) > 2:
        profile = load_profile(user_id)
        name = profile.get('name', 'Usuario')
        
        save_support_request(user_id, name, text)
        
        await message.answer(
            "¡Gracias por tu pregunta! La he enviado al equipo. "
            "Te responderán en breve. 💫\n\n"
            "Si quieres cancelar tu solicitud — escribe /cancelar_solicitud"
        )
    else:
        await message.answer(
            "No entendí bien lo que quisiste decir... ❤️\n\n"
            "Si es una pregunta — la enviaré al equipo y te responderán.\n"
            "Si quieres describir una imagen — escribe /diario\n"
            "Si necesitas ayuda — escribe /ayuda\n\n"
            "¡Estoy aquí! 💫"
        )


# ---- ОТЧЁТ ДЛЯ АДМИНА ----
async def send_daily_report():
    pending = get_pending_requests()
    
    if not pending:
        await bot.send_message(
            ADMIN_ID,
            "📊 **Informe diario**\n\n"
            "No hay nuevas solicitudes de soporte. ¡Todo tranquilo! 💫"
        )
        return
    
    report = "📊 **Informe diario**\n\n"
    report += f"📩 Nuevas solicitudes de soporte: {len(pending)}\n\n"
    
    for i, req in enumerate(pending, 1):
        report += f"**{i}. Solicitud**\n"
        report += f"🆔 ID: `{req['user_id']}`\n"
        report += f"👤 Nombre: {req['name']}\n"
        report += f"📝 Pregunta: {req['question'][:200]}...\n"
        report += f"📅 Fecha: {req['date'][:10]}\n\n"
        report += f"Para responder, usa:\n"
        report += f"`/responder {req['user_id']} Texto de respuesta`\n\n"
        report += "---\n\n"
    
    await bot.send_message(ADMIN_ID, report, parse_mode="Markdown")