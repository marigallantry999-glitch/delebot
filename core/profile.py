import json
import os
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from config import USERS_DIR

def get_user_path(user_id: int) -> str:
    """Возвращает путь к файлу профиля пользователя."""
    return f"{USERS_DIR}/user_{user_id}.json"

def load_profile(user_id: int) -> Dict:
    """Загружает профиль пользователя. Если нет — создаёт новый."""
    path = get_user_path(user_id)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return create_profile(user_id)

def create_profile(user_id: int, name: str = None) -> Dict:
    """Создаёт новый профиль пользователя."""
    now = datetime.now().isoformat()
    trial_until = (datetime.now() + timedelta(days=7)).isoformat()
    
    profile = {
        "user_id": user_id,
        "name": name or f"User_{user_id}",
        "address_form": "ты",
        "created_at": now,
        "subscription_status": "trial",
        "trial_until": trial_until,
        "subscription_until": None,
        "diamonds": 0,
        "streak": 0,
        "last_daily_date": None,
        "used_images": [],
        "card_errors": [],
        "card_connectors": [
            {"connector": "y", "count": 0},
            {"connector": "e", "count": 0},
            {"connector": "también", "count": 0},
            {"connector": "además", "count": 0},
            {"connector": "pero", "count": 0},
            {"connector": "sino", "count": 0},
            {"connector": "sin embargo", "count": 0},
            {"connector": "porque", "count": 0},
            {"connector": "ya que", "count": 0},
            {"connector": "entonces", "count": 0},
            {"connector": "por eso", "count": 0},
            {"connector": "primero", "count": 0},
            {"connector": "luego", "count": 0},
            {"connector": "después", "count": 0},
            {"connector": "finalmente", "count": 0},
            {"connector": "al final", "count": 0}
        ],
        "card_rules": [
            {"rule": "ser_estar", "status": "unused"},
            {"rule": "hay_esta", "status": "unused"},
            {"rule": "gerundio", "status": "unused"},
            {"rule": "preposiciones", "status": "unused"},
            {"rule": "genero_numero", "status": "unused"},
            {"rule": "concordancia", "status": "unused"},
            {"rule": "preterito_indefinido", "status": "unused"},
            {"rule": "imperativo", "status": "unused"},
            {"rule": "pronombres", "status": "unused"},
            {"rule": "reflexivos", "status": "unused"},
            {"rule": "perifrasis", "status": "unused"},
            {"rule": "comparativos", "status": "unused"},
            {"rule": "muy_mucho", "status": "unused"}
        ],
        "image_results": {},
        "stats": {
            "daily_attempts": 0,
            "total_descriptions": 0,
            "voice_count": 0,
            "text_count": 0,
            "exercises_done": 0
        },
        "last_active": now
    }
    save_profile(user_id, profile)
    return profile

def save_profile(user_id: int, profile: Dict) -> None:
    """Сохраняет профиль пользователя."""
    path = get_user_path(user_id)
    os.makedirs(USERS_DIR, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

def add_diamonds(user_id: int, amount: int) -> None:
    """Добавляет алмазы пользователю."""
    profile = load_profile(user_id)
    profile['diamonds'] = max(0, profile['diamonds'] + amount)
    save_profile(user_id, profile)

def spend_diamonds(user_id: int, amount: int) -> bool:
    """Списывает алмазы. Возвращает True, если достаточно."""
    profile = load_profile(user_id)
    if profile['diamonds'] >= amount:
        profile['diamonds'] -= amount
        save_profile(user_id, profile)
        return True
    return False

def update_streak(user_id: int) -> int:
    """Обновляет стрик пользователя. Возвращает текущий стрик."""
    profile = load_profile(user_id)
    today = datetime.now().date().isoformat()
    
    if profile['last_daily_date'] == today:
        return profile['streak']
    
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    if profile['last_daily_date'] == yesterday:
        profile['streak'] += 1
    else:
        profile['streak'] = 1
    
    profile['last_daily_date'] = today
    save_profile(user_id, profile)
    return profile['streak']

def check_subscription(user_id: int) -> bool:
    """Проверяет, активна ли подписка у пользователя."""
    profile = load_profile(user_id)
    
    # Проверяем триал
    if profile.get('subscription_status') == 'trial':
        trial_until = profile.get('trial_until')
        if trial_until and datetime.now() < datetime.fromisoformat(trial_until):
            return True
    
    # Проверяем платную подписку
    subscription_until = profile.get('subscription_until')
    if subscription_until and datetime.now() < datetime.fromisoformat(subscription_until):
        return True
    
    return False

# ---- SOPORTE ----

def save_support_request(user_id: int, name: str, question: str) -> None:
    """Guarda una solicitud de soporte."""
    requests_path = f"{USERS_DIR}/support_requests.json"
    
    if os.path.exists(requests_path):
        with open(requests_path, 'r', encoding='utf-8') as f:
            requests = json.load(f)
    else:
        requests = []
    
    requests.append({
        "user_id": user_id,
        "name": name,
        "question": question,
        "date": datetime.now().isoformat(),
        "answered": False
    })
    
    with open(requests_path, 'w', encoding='utf-8') as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)

def get_pending_requests() -> list:
    """Devuelve todas las solicitudes no respondidas."""
    requests_path = f"{USERS_DIR}/support_requests.json"
    if not os.path.exists(requests_path):
        return []
    
    with open(requests_path, 'r', encoding='utf-8') as f:
        requests = json.load(f)
    
    return [r for r in requests if not r.get('answered', False)]

def mark_request_answered(user_id: int) -> None:
    """Marca una solicitud como respondida."""
    requests_path = f"{USERS_DIR}/support_requests.json"
    if not os.path.exists(requests_path):
        return
    
    with open(requests_path, 'r', encoding='utf-8') as f:
        requests = json.load(f)
    
    for r in requests:
        if r['user_id'] == user_id and not r.get('answered', False):
            r['answered'] = True
            break
    
    with open(requests_path, 'w', encoding='utf-8') as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)

def cancel_user_request(user_id: int) -> bool:
    """Cancela la solicitud de un usuario. Devuelve True si se encontró."""
    requests_path = f"{USERS_DIR}/support_requests.json"
    if not os.path.exists(requests_path):
        return False
    
    with open(requests_path, 'r', encoding='utf-8') as f:
        requests = json.load(f)
    
    found = False
    for r in requests:
        if r['user_id'] == user_id and not r.get('answered', False):
            r['answered'] = True
            found = True
            break
    
    if found:
        with open(requests_path, 'w', encoding='utf-8') as f:
            json.dump(requests, f, ensure_ascii=False, indent=2)
    
    return found