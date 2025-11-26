"""
Модуль Product Intelligence - анализ продукта и создание профиля
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ProductProfile:
    """Профиль продукта"""
    name: str
    description: str
    category: str
    target_audience: str
    value_proposition: str
    key_features: List[str]
    pain_points_solved: List[str]
    competitive_advantages: List[str]
    tone_of_voice: str
    key_messages: List[str]

class ProductIntelligence:
    """
    Модуль для анализа продукта и создания профиля
    
    Функции:
    - Анализ продукта
    - Создание профиля продукта
    - Формирование value proposition
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.product_profile: Optional[ProductProfile] = None
    
    def analyze_product(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ продукта на основе предоставленной информации
        
        Args:
            product_info: словарь с информацией о продукте:
                - name: название продукта
                - description: описание
                - category: категория
                - features: список функций
                - target_audience: целевая аудитория
                - competitors: конкуренты
        """
        analysis_prompt = f"""
Проанализируй следующий продукт и создай детальный профиль:

Название: {product_info.get('name', 'Не указано')}
Описание: {product_info.get('description', 'Не указано')}
Категория: {product_info.get('category', 'Не указано')}
Функции: {', '.join(product_info.get('features', []))}
Целевая аудитория: {product_info.get('target_audience', 'Не указано')}

Проведи анализ по следующим аспектам:
1. Ключевые функции и возможности
2. Решаемые болевые точки
3. Конкурентные преимущества
4. Целевая аудитория и её потребности
5. Уникальное ценностное предложение
6. Рекомендуемый tone of voice
7. Ключевые сообщения для маркетинга

Верни структурированный анализ в формате JSON.
"""
        
        # Здесь будет вызов LLM
        # Для примера возвращаем структуру
        return {
            "key_features": product_info.get('features', []),
            "pain_points_solved": [],
            "competitive_advantages": [],
            "value_proposition": "",
            "tone_of_voice": "professional",
            "key_messages": []
        }
    
    def create_product_profile(self, analysis: Dict[str, Any]) -> ProductProfile:
        """
        Создание профиля продукта на основе анализа
        
        Args:
            analysis: результат анализа продукта
        """
        self.product_profile = ProductProfile(
            name=analysis.get('name', ''),
            description=analysis.get('description', ''),
            category=analysis.get('category', ''),
            target_audience=analysis.get('target_audience', ''),
            value_proposition=analysis.get('value_proposition', ''),
            key_features=analysis.get('key_features', []),
            pain_points_solved=analysis.get('pain_points_solved', []),
            competitive_advantages=analysis.get('competitive_advantages', []),
            tone_of_voice=analysis.get('tone_of_voice', 'professional'),
            key_messages=analysis.get('key_messages', [])
        )
        
        return self.product_profile
    
    def generate_value_proposition(self, product_info: Dict[str, Any], 
                                   audience_insights: Dict[str, Any]) -> str:
        """
        Генерация value proposition на основе продукта и инсайтов аудитории
        
        Args:
            product_info: информация о продукте
            audience_insights: инсайты о целевой аудитории из DEEP IMPACT
        """
        vp_prompt = f"""
Создай убедительное ценностное предложение для продукта:

Продукт: {product_info.get('name', '')}
Описание: {product_info.get('description', '')}

Инсайты о целевой аудитории:
- Главная боль: {audience_insights.get('main_pain', 'Не указано')}
- Главная задача (JTBD): {audience_insights.get('main_task', 'Не указано')}
- Мотивации: {', '.join(audience_insights.get('motivations', []))}
- Ожидания: {audience_insights.get('expectations', 'Не указано')}

Создай value proposition, который:
1. Четко формулирует, какую проблему решает продукт
2. Обращается к эмоциональным триггерам аудитории
3. Выделяет уникальные преимущества
4. Использует язык целевой аудитории
5. Создает желание действовать

Формат: [Продукт] помогает [целевая аудитория] [главная выгода], 
чтобы [желаемый результат], без [главная боль/проблема].
"""
        
        # Здесь будет вызов LLM
        return f"{product_info.get('name', 'Продукт')} помогает {audience_insights.get('target_segment', 'клиентам')} достигать результатов без лишних усилий."
    
    def get_product_profile(self) -> Optional[ProductProfile]:
        """Получить текущий профиль продукта"""
        return self.product_profile

