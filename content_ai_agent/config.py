"""
Конфигурация Content AI Agent
"""
import os
from typing import Dict, Any

# Пытаемся загрузить переменные окружения из .env файла
try:
    from dotenv import load_dotenv
    import pathlib
    # Ищем .env файл в корне проекта (на уровень выше от content_ai_agent)
    env_path = pathlib.Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        # Пробуем загрузить из текущей директории
        load_dotenv()
except ImportError:
    # Если python-dotenv не установлен, просто пропускаем загрузку .env
    # Переменные окружения все равно можно установить вручную
    pass

class Config:
    """Конфигурация системы"""
    
    # API ключи (должны быть установлены через переменные окружения)
    # Статическое значение читается при импорте модуля
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    
    @staticmethod
    def get_openai_api_key():
        """Динамически получает API ключ из переменных окружения (всегда актуальное значение)"""
        return os.getenv("OPENAI_API_KEY", "").strip()
    
    # Модели по умолчанию
    DEFAULT_MODEL = "gpt-4"
    DEFAULT_TEMPERATURE = 0.7
    
    # Пути к базам знаний
    BASE_KNOWLEDGE_PATH = "knowledge_base"
    DEEP_IMPACT_FRAMEWORK_PATH = "frameworks/deep_impact"
    PRODAYUCHIE_SMYSLY_PATH = "frameworks/prodayuchie_smysly"
    
    # Настройки генерации контента
    MAX_CONTENT_LENGTH = 2000
    MIN_CONTENT_LENGTH = 300
    
    # Настройки планировщика
    DEFAULT_POSTS_PER_WEEK = 5
    OPTIMAL_POSTING_TIMES = {
        "linkedin": ["09:00", "13:00", "17:00"],
        "twitter": ["08:00", "12:00", "16:00", "20:00"],
        "telegram": ["08:00", "13:00", "18:00"]
    }
    
    # Типы промптов из фреймворка DEEP IMPACT
    PROMPT_TYPES = {
        "interview": "интервью-промт",
        "generative": "генеративный промт",
        "direct": "прямой промт"
    }

