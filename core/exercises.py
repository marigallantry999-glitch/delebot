import json
import random
import os
from pathlib import Path
from typing import Optional, Dict, List
from config import EXERCISES_DIR

def get_exercise_by_rule(rule_name: str) -> Optional[Dict]:
    """
    Возвращает случайное упражнение из JSON-файла по правилу.
    Возвращает None, если файл не существует или пуст.
    """
    file_path = Path(f"{EXERCISES_DIR}/{rule_name}.json")
    
    if not file_path.exists():
        print(f"⚠️ Файл упражнений не найден: {rule_name}.json")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            exercises = json.load(f)
        
        if not exercises:
            print(f"⚠️ Файл {rule_name}.json пуст")
            return None
        
        return random.choice(exercises)
    except json.JSONDecodeError:
        print(f"⚠️ Ошибка парсинга JSON в {rule_name}.json")
        return None

def get_exercises_by_rules(rules: List[str], count: int = 3) -> List[Dict]:
    """
    Возвращает список упражнений для списка правил.
    Если упражнений меньше count — возвращает сколько есть.
    """
    exercises = []
    for rule in rules[:count]:
        ex = get_exercise_by_rule(rule)
        if ex:
            exercises.append(ex)
    return exercises

def get_all_exercises() -> Dict[str, List[Dict]]:
    """Загружает все упражнения из всех JSON-файлов."""
    all_exercises = {}
    for file_path in Path(EXERCISES_DIR).glob("*.json"):
        rule_name = file_path.stem
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_exercises[rule_name] = json.load(f)
        except:
            all_exercises[rule_name] = []
    return all_exercises

def create_exercise_file(rule_name: str, exercises: List[Dict]) -> bool:
    """
    Создаёт или обновляет файл с упражнениями для правила.
    exercises: список словарей с полями type, question, answer, rule
    """
    file_path = Path(f"{EXERCISES_DIR}/{rule_name}.json")
    os.makedirs(EXERCISES_DIR, exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(exercises, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"⚠️ Ошибка сохранения {rule_name}.json: {e}")
        return False

def check_exercise_answer(exercise: Dict, user_answer: str) -> bool:
    """
    Проверяет ответ пользователя на упражнение.
    Сравнивает с ответом из JSON (регистронезависимо, убирает пробелы).
    """
    if not exercise or not user_answer:
        return False
    
    correct = exercise.get('answer', '').strip().lower()
    user = user_answer.strip().lower()
    
    # Убираем лишние пробелы и знаки препинания для сравнения
    import re
    correct = re.sub(r'[^\w\s]', '', correct)
    user = re.sub(r'[^\w\s]', '', user)
    
    return user == correct