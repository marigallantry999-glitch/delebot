import os
from dotenv import load_dotenv

load_dotenv()

# Токены и ключи
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

# API ключи OpenRouter (3 аккаунта)
OPENROUTER_API_KEYS = [
    os.getenv('OPENROUTER_API_KEY_1'),
    os.getenv('OPENROUTER_API_KEY_2'),
    os.getenv('OPENROUTER_API_KEY_3')
]

# ТОЛЬКО РАБОТАЮЩИЕ МОДЕЛИ (по результатам теста)
FREE_MODELS = [
    "cohere/north-mini-code:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "openai/gpt-oss-20b:free",
    "openrouter/free",
    "openrouter/owl-alpha",
    "poolside/laguna-m.1:free"
]

# Папки
DATA_DIR = "data"
IMAGES_DIR = f"{DATA_DIR}/images"
USERS_DIR = f"{DATA_DIR}/users"
EXERCISES_DIR = f"{DATA_DIR}/exercises"

# Настройки OpenRouter
OPENROUTER_TIMEOUT = 10
OPENROUTER_MAX_TOKENS = 1000
OPENROUTER_TEMPERATURE = 0.3