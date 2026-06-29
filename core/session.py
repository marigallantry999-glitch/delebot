import json
import random
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
from config import IMAGES_DIR
from core.profile import load_profile, save_profile, update_streak, add_diamonds
from core.exercises import get_exercise_by_rule
from ai.openrouter_client import analyze_with_openrouter
from ai.prompts import get_dele_prompt_with_system


def get_available_images(profile: Dict) -> list:
    """Возвращает список доступных для описания картинок."""
    used = profile.get('used_images', [])
    all_images = []
    
    print(f"🔍 Ищем картинки в: {IMAGES_DIR}")
    print(f"📋 Уже использованные: {used}")
    
    # Сканируем папку с картинками
    for folder in Path(IMAGES_DIR).iterdir():
        print(f"📁 Проверяем: {folder.name}")
        
        if not folder.is_dir():
            print(f"   ⏭️ Не папка, пропускаем")
            continue
            
        if folder.name == "hola":
            print(f"   ⏭️ Это аватар, пропускаем")
            continue
            
        if folder.name in used:
            print(f"   ⏭️ Уже использована, пропускаем")
            continue
        
        # Проверяем наличие всех файлов
        image_path = folder / "image.jpg"
        full_desc_path = folder / "descripcion_detallada.txt"
        dele_desc_path = folder / "dele_descripcion.txt"
        lexis_path = folder / "palabras.txt"
        
        print(f"   📄 image.jpg: {image_path.exists()}")
        print(f"   📄 descripcion_detallada.txt: {full_desc_path.exists()}")
        print(f"   📄 dele_descripcion.txt: {dele_desc_path.exists()}")
        print(f"   📄 palabras.txt: {lexis_path.exists()}")
        
        if all(p.exists() for p in [image_path, full_desc_path, dele_desc_path, lexis_path]):
            all_images.append(folder.name)
            print(f"   ✅ Добавлена в список!")
        else:
            print(f"   ❌ Не хватает файлов!")
    
    print(f"📸 Найдено картинок: {len(all_images)}")
    return all_images


def load_image_data(image_name: str) -> Optional[Dict]:
    """Загружает данные картинки из папки."""
    folder = Path(IMAGES_DIR) / image_name
    
    if not folder.exists():
        return None
    
    try:
        with open(folder / "descripcion_detallada.txt", 'r', encoding='utf-8') as f:
            descripcion_detallada = f.read()
        with open(folder / "dele_descripcion.txt", 'r', encoding='utf-8') as f:
            dele_descripcion = f.read()
        with open(folder / "palabras.txt", 'r', encoding='utf-8') as f:
            palabras = f.read()
        
        return {
            "name": image_name,
            "image_path": str(folder / "image.jpg"),
            "descripcion_detallada": descripcion_detallada,
            "dele_descripcion": dele_descripcion,
            "palabras": palabras
        }
    except Exception as e:
        print(f"⚠️ Ошибка загрузки картинки {image_name}: {e}")
        return None


def get_next_image(user_id: int) -> Optional[Dict]:
    """Выбирает следующую картинку для пользователя."""
    profile = load_profile(user_id)
    available = get_available_images(profile)
    
    if not available:
        used = profile.get('used_images', [])
        if used:
            return load_image_data(used[0])
        return None
    
    image_name = random.choice(available)
    return load_image_data(image_name)


async def process_daily_description(user_id: int, user_answer: str, image_name: str) -> Dict:
    """Обрабатывает описание картинки пользователем."""
    profile = load_profile(user_id)
    image_data = load_image_data(image_name)
    
    if not image_data:
        return {"error": "Картинка не найдена"}
    
    profile['stats']['total_descriptions'] += 1
    if user_answer.startswith('/'):
        profile['stats']['voice_count'] += 1
    else:
        profile['stats']['text_count'] += 1
    
    # 👇 ИСПРАВЛЕННЫЙ ВЫЗОВ
    system_prompt, user_prompt = get_dele_prompt_with_system(
        image_data['descripcion_detallada'],  
        image_data['dele_descripcion'],       
        user_answer
    )
    
    result = await analyze_with_openrouter(user_prompt, system_prompt)
    
    if not result:
        return {"error": "Не удалось обработать ответ. Попробуй позже."}
    
    errors = result.get('errors', [])
    for error in errors:
        update_error_card(profile, error)
    
    if image_name not in profile.get('used_images', []):
        profile.setdefault('used_images', []).append(image_name)
    
    streak = update_streak(user_id)
    add_diamonds(user_id, 1)
    
    if streak >= 3:
        add_diamonds(user_id, 1)
    
    profile.setdefault('image_results', {})[image_name] = {
        "date": datetime.now().isoformat(),
        "coherence_score": result.get('coherence_score', 0),
        "lexis_score": result.get('lexis_score', 0),
        "grammar_score": result.get('grammar_score', 0),
        "errors": errors
    }
    
    save_profile(user_id, profile)
    
    return result


def update_error_card(profile: Dict, error: Dict):
    """Обновляет карту ошибок пользователя."""
    rule = error.get('rule')
    if not rule:
        return
    
    for card in profile.get('card_errors', []):
        if card['rule'] == rule:
            card['percent'] = min(100, card.get('percent', 0) + 20)
            card['last_wrong'] = error.get('sentence', '')
            if card.get('percent', 0) >= 100:
                card['status'] = 'closed'
            return
    
    profile.setdefault('card_errors', []).append({
        "rule": rule,
        "percent": 20,
        "last_wrong": error.get('sentence', ''),
        "status": "active",
        "packs_done": 1,
        "packs_total": 5
    })