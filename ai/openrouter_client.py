import aiohttp
import asyncio
import json
from typing import Optional, Dict, Any, List
from config import OPENROUTER_API_KEYS, FREE_MODELS, OPENROUTER_TIMEOUT, OPENROUTER_MAX_TOKENS, OPENROUTER_TEMPERATURE

class OpenRouterClient:
    def __init__(self):
        # Только непустые ключи
        self.api_keys = [k for k in OPENROUTER_API_KEYS if k]
        # Только рабочие модели
        self.models = FREE_MODELS
        self.current_key_index = 0
        self.current_model_index = 0
        self.timeout = aiohttp.ClientTimeout(total=OPENROUTER_TIMEOUT)
        self.max_tokens = OPENROUTER_MAX_TOKENS
        self.temperature = OPENROUTER_TEMPERATURE
        self._working_cache = {}  # Кэш: модель -> работает ли

    async def analyze(self, prompt: str, system_prompt: str = None) -> Optional[Dict[str, Any]]:
        """
        Отправляет запрос к OpenRouter с переключением между моделями и ключами.
        Сначала пробует модели, которые точно работали раньше (из кэша).
        Возвращает JSON-ответ или None, если все модели и ключи не сработали.
        """
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        # Сначала пробуем модели из кэша (которые точно работали)
        for model in self._get_cached_working_models():
            for key in self.api_keys:
                result = await self._try_request(model, key, messages)
                if result:
                    self._mark_model_working(model)
                    return result

        # Если кэш пустой или модели не сработали, пробуем все модели по очереди
        for model in self.models:
            for key in self.api_keys:
                result = await self._try_request(model, key, messages)
                if result:
                    self._mark_model_working(model)
                    return result

        return None

    def _get_cached_working_models(self) -> List[str]:
        """Возвращает модели из кэша, которые точно работали."""
        working = []
        for model, status in self._working_cache.items():
            if status and model in self.models:
                working.append(model)
        return working[:5]  # Берём первые 5 для скорости

    def _mark_model_working(self, model: str):
        """Помечает модель как рабочую."""
        self._working_cache[model] = True

    async def _try_request(self, model: str, api_key: str, messages: List[Dict]) -> Optional[Dict[str, Any]]:
        """Пробует отправить запрос к одной модели с одним ключом."""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    'https://openrouter.ai/api/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json',
                        'HTTP-Referer': 'https://t.me/lera_bot',
                        'X-Title': 'Lera Bot'
                    },
                    json={
                        'model': model,
                        'messages': messages,
                        'temperature': self.temperature,
                        'max_tokens': self.max_tokens
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        print(f"❌ Модель {model} вернула ошибку {response.status}: {error_text[:100]}")
                        return None
        except asyncio.TimeoutError:
            print(f"⏰ Таймаут: модель {model} не ответила за {OPENROUTER_TIMEOUT} секунд")
            return None
        except Exception as e:
            print(f"⚠️ Ошибка с моделью {model}: {e}")
            return None

    async def analyze_with_fallback(self, prompt: str, system_prompt: str = None, max_retries: int = 2) -> Optional[Dict[str, Any]]:
        """
        Пытается получить ответ с переключением моделей и ключей.
        При ошибке пробует до max_retries раз.
        """
        for attempt in range(max_retries):
            result = await self.analyze(prompt, system_prompt)
            if result:
                return result
            print(f"🔄 Попытка {attempt + 1}/{max_retries} не удалась, пробуем снова...")
            await asyncio.sleep(1)
        return None

    def extract_content(self, response: Dict[str, Any]) -> Optional[str]:
        """Извлекает текстовый ответ из ответа OpenRouter."""
        try:
            return response['choices'][0]['message']['content']
        except (KeyError, IndexError, TypeError):
            return None

    def extract_json(self, response: Dict[str, Any]) -> Optional[Dict]:
        """Извлекает и парсит JSON из ответа OpenRouter."""
        content = self.extract_content(response)
        if not content:
            return None
        try:
            # Пробуем найти JSON в тексте (если модель вернула с пояснениями)
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
            return json.loads(content)
        except json.JSONDecodeError:
            return None

# Создаём глобальный клиент
client = OpenRouterClient()

async def analyze_with_openrouter(prompt: str, system_prompt: str = None) -> Optional[Dict]:
    """
    Упрощённая функция для вызова из других частей бота.
    Возвращает распарсенный JSON или None.
    """
    result = await client.analyze_with_fallback(prompt, system_prompt)
    if result:
        return client.extract_json(result)
    return None

async def analyze_with_openrouter_text(prompt: str, system_prompt: str = None) -> Optional[str]:
    """
    Возвращает текстовый ответ от OpenRouter.
    """
    result = await client.analyze_with_fallback(prompt, system_prompt)
    if result:
        return client.extract_content(result)
    return None