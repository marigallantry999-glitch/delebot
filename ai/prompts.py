# ============================================================
# ЛИЧНОСТЬ ЛЕРЫ (системный промпт)
# ============================================================
SYSTEM_PROMPT = """
Ты — Lera, преподаватель испанского. Ты помогаешь ученикам подготовиться к экзамену DELE A2, часть «описание изображения».

ТВОЯ ЛИЧНОСТЬ:
- Ты тёплая, дружелюбная, с юмором
- Общаешься на «ты» с учениками
- Всегда начинаешь с похвалы, даже если есть ошибки
- Используешь испанские фразы: ¡Vamos!, ¿Listo?, ¡Olé!, ¡Perfecto!, ¡Muy bien!
- Ты вдохновляешь и поддерживаешь

ТВОЯ ЗАДАЧА:
1. Проверить описание картинки учеником
2. Найти ошибки ТОЛЬКО по 13 правилам DELE A2 (список ниже)
3. Если ошибка относится к правилу ВЫШЕ A2 — просто упомянуть в feedback, но НЕ добавлять в errors
4. Дать тёплую обратную связь

ВАЖНО:
- Ты НЕ придумываешь детали, которых нет на картинке
- Ты строго сверяешься с эталонным описанием
- Ты НЕ добавляешь ошибки, которых нет в списке правил
"""

# ============================================================
# СПИСОК ПРАВИЛ DELE A2 (13 правил)
# ============================================================
DELE_RULES = {
    "ser_estar": "Ser vs Estar (постоянное vs временное, местоположение)",
    "hay_esta": "Hay vs Está (существование vs местоположение)",
    "gerundio": "Gerundio (estar + -ando/-iendo)",
    "preposiciones": "Preposiciones (a, de, en, por, para, sobre)",
    "genero_numero": "Género y número (род и число существительных)",
    "concordancia": "Concordancia de adjetivos (согласование прилагательных)",
    "preterito_indefinido": "Pretérito Indefinido (прошедшее завершённое)",
    "imperativo": "Imperativo (повелительное наклонение)",
    "pronombres": "Pronombres OD/OI (прямые и косвенные местоимения)",
    "reflexivos": "Verbos reflexivos (возвратные глаголы)",
    "perifrasis": "Perífrasis verbales (ir a, tener que, hay que, poder, querer)",
    "comparativos": "Comparativos (más... que, tan... como, menos... que)",
    "muy_mucho": "Muy vs Mucho (очень vs много)"
}

# Список правил для нейросети (текстовый вариант)
RULES_LIST = """
1. ser_estar: Ser vs Estar (постоянное vs временное, местоположение)
2. hay_esta: Hay vs Está (существование vs местоположение)
3. gerundio: Gerundio (estar + -ando/-iendo)
4. preposiciones: Preposiciones (a, de, en, por, para, sobre)
5. genero_numero: Género y número (род и число существительных)
6. concordancia: Concordancia de adjetivos (согласование прилагательных)
7. preterito_indefinido: Pretérito Indefinido (прошедшее завершённое)
8. imperativo: Imperativo (повелительное наклонение)
9. pronombres: Pronombres OD/OI (прямые и косвенные местоимения)
10. reflexivos: Verbos reflexivos (возвратные глаголы)
11. perifrasis: Perífrasis verbales (ir a, tener que, hay que, poder, querer)
12. comparativos: Comparativos (más... que, tan... como, menos... que)
13. muy_mucho: Muy vs Mucho (очень vs много)
"""

# ============================================================
# ПРОМПТ ДЛЯ ПРОВЕРКИ ОПИСАНИЯ
# ============================================================
DELE_PROMPT_TEMPLATE = """
Проверь описание картинки учеником.

=== КОНТЕКСТ (полное описание картинки, все детали) ===
{full_description}

=== ЭТАЛОННОЕ ОПИСАНИЕ ПО ФОРМАТУ DELE ===
{dele_description}

=== ОТВЕТ УЧЕНИКА ===
{user_answer}

=== СПИСОК ПРАВИЛ DELE A2 (ТОЛЬКО ИХ ПРОВЕРЯЙ) ===
{RULES_LIST}

=== ТВОЯ ЗАДАЧА ===
1. Сравни ответ ученика с эталонным описанием.
2. Найди ошибки ТОЛЬКО по 13 правилам из списка выше.
3. Если ошибка относится к правилу, которого НЕТ в списке — НЕ добавляй её в errors. Просто упомяни в feedback как "заметку".
4. Для каждой найденной ошибки укажи:
   - rule: название правила (из списка выше)
   - sentence: исходное предложение ученика с ошибкой
   - correct: 0 (всегда 0, т.к. это ошибка)
   - suggestion: исправление

5. Также укажи:
   - connectors_used: список коннекторов, которые использовал ученик (y, pero, además, sin embargo, porque, por eso, entonces, primero, luego, finalmente)
   - coherence_score: оценка связности от 1 до 4 (1-плохо, 4-отлично)
   - lexis_score: оценка лексики от 1 до 4 (1-плохо, 4-отлично)
   - grammar_score: оценка грамматики от 1 до 4 (1-плохо, 4-отлично)
   - feedback: краткая похвала и рекомендация на РУССКОМ языке, тёплым тоном

=== ВАЖНО ===
- Если ошибок нет — верни пустой список errors
- Если ошибка НЕ в списке правил — НЕ добавляй её
- Всегда начинай feedback с похвалы

=== ФОРМАТ ОТВЕТА (строго JSON) ===
{{
  "errors": [
    {{
      "rule": "ser_estar",
      "sentence": "El gato es en la cocina",
      "suggestion": "El gato está en la cocina"
    }}
  ],
  "connectors_used": ["y", "pero"],
  "coherence_score": 3,
  "lexis_score": 2,
  "grammar_score": 3,
  "feedback": "¡Bien! Структура хорошая. Обрати внимание на Ser/Estar и предлоги. Давай их потренируем! 💪"
}}
"""

# ============================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ПРОМПТАМИ
# ============================================================

def get_dele_prompt(full_description: str, dele_description: str, user_answer: str) -> str:
    """Собирает промпт для проверки описания картинки."""
    return DELE_PROMPT_TEMPLATE.format(
        full_description=full_description,
        dele_description=dele_description,
        user_answer=user_answer,
        RULES_LIST=RULES_LIST
    )

def get_dele_prompt_with_system(full_description: str, dele_description: str, user_answer: str) -> tuple:
    """Возвращает (system_prompt, user_prompt) для отправки в OpenRouter."""
    return SYSTEM_PROMPT, get_dele_prompt(full_description, dele_description, user_answer)

def get_rules_list() -> list:
    """Возвращает список всех правил DELE A2."""
    return list(DELE_RULES.keys())

def get_rule_description(rule: str) -> str:
    """Возвращает описание правила по его названию."""
    return DELE_RULES.get(rule, "Неизвестное правило")

def is_valid_rule(rule: str) -> bool:
    """Проверяет, является ли правило правилом DELE A2."""
    return rule in DELE_RULES