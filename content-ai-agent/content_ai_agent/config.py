"""
Конфигурация Content AI Agent
"""
import os
from typing import Dict, Any

class Config:
    """Конфигурация системы"""
    
    # API ключи (должны быть установлены через переменные окружения)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
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

