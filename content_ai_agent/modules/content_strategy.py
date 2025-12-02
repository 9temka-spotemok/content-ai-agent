"""
Модуль Content Strategy Generator - генерация контент-стратегии
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from content_ai_agent.frameworks.deep_impact import DeepImpactFramework

@dataclass
class ContentStrategy:
    """Контент-стратегия"""
    target_audience: Dict[str, Any]
    content_pillars: List[str]
    content_funnel: Dict[str, List[str]]
    content_calendar: Dict[str, List[Dict[str, Any]]]
    tone_of_voice: str
    key_messages: List[str]
    channels: List[str]
    posting_schedule: Dict[str, List[str]]

@dataclass
class ContentPillar:
    """Контентный столп"""
    name: str
    description: str
    content_types: List[str]
    frequency: int  # постов в неделю

class ContentStrategyGenerator:
    """
    Генератор контент-стратегии на основе фреймворка DEEP IMPACT
    
    Функции:
    - Авто-стратегия
    - Контент-воронка
    - Рубрикатор
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.deep_impact = DeepImpactFramework()
        self.strategy: Optional[ContentStrategy] = None
    
    def generate_strategy(self, product_profile: Dict[str, Any],
                         audience_insights: Dict[str, Any],
                         business_goals: List[str]) -> ContentStrategy:
        """
        Генерация полной контент-стратегии
        
        Args:
            product_profile: профиль продукта
            audience_insights: инсайты о аудитории из DEEP IMPACT
            business_goals: бизнес-цели
        """
        # Генерация контентных столпов
        content_pillars = self._generate_content_pillars(
            product_profile, audience_insights
        )
        
        # Создание контент-воронки
        content_funnel = self._create_content_funnel(
            audience_insights, product_profile
        )
        
        # Генерация рубрикатора
        content_calendar = self._generate_content_calendar(
            content_pillars, content_funnel
        )
        
        # Определение tone of voice
        tone_of_voice = self._determine_tone_of_voice(
            product_profile, audience_insights
        )
        
        # Ключевые сообщения
        key_messages = self._generate_key_messages(
            product_profile, audience_insights
        )
        
        # Каналы публикации
        channels = self._select_channels(audience_insights)
        
        # Расписание публикаций
        posting_schedule = self._create_posting_schedule(channels)
        
        self.strategy = ContentStrategy(
            target_audience=audience_insights,
            content_pillars=content_pillars,
            content_funnel=content_funnel,
            content_calendar=content_calendar,
            tone_of_voice=tone_of_voice,
            key_messages=key_messages,
            channels=channels,
            posting_schedule=posting_schedule
        )
        
        return self.strategy
    
    def _generate_content_pillars(self, product_profile: Dict[str, Any],
                                  audience_insights: Dict[str, Any]) -> List[str]:
        """
        Генерация контентных столпов на основе DEEP IMPACT
        
        Столпы основаны на:
        - Болевых точках (Pain Points)
        - Задачах (Tasks/JTBD)
        - Мотивациях (Motivations)
        - Стремлениях (Aspirations)
        """
        pillars_prompt = f"""
На основе анализа целевой аудитории создай 4-6 контентных столпов.

Инсайты аудитории:
- Главная боль: {audience_insights.get('main_pain', '')}
- Главная задача: {audience_insights.get('main_task', '')}
- Мотивации: {', '.join(audience_insights.get('motivations', []))}
- Стремления: {', '.join(audience_insights.get('aspirations', []))}

Продукт: {product_profile.get('name', '')}
Value Proposition: {product_profile.get('value_proposition', '')}

Создай контентные столпы, которые:
1. Решают разные аспекты боли аудитории
2. Соответствуют разным стадиям воронки
3. Используют разные форматы контента
4. Обращаются к эмоциональным триггерам

Верни результат в формате JSON:
{{
  "pillars": [
    {{
      "name": "Название столпа",
      "description": "Краткое описание (2-3 предложения)",
      "content_types": ["формат 1", "формат 2", "..."],
      "frequency_per_week": 1
    }}
  ]
}}
"""
        
        # Глубокая генерация столпов через LLM (если клиент доступен)
        if self.llm_client:
            try:
                import json
                import re
                
                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Ты — контент-стратег, работающий по DEEP IMPACT. "
                                "Фокусируйся на боли, задачах и мотивациях аудитории."
                            ),
                        },
                        {"role": "user", "content": pillars_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1600,
                )
                content = response.choices[0].message.content.strip()
                if not content.startswith("{"):
                    match = re.search(r"(\{.*\})", content, re.DOTALL)
                    if match:
                        content = match.group(1)
                
                data = json.loads(content)
                raw_pillars = data.get("pillars", [])
                pillars = [p.get("name") for p in raw_pillars if p.get("name")]
                
                # Если LLM вернул адекватный список, используем его
                if pillars:
                    return pillars
            except Exception:
                # Фолбэк на статический список
                pass
        
        # Фолбэк: примерные столпы на основе DEEP IMPACT
        pillars = [
            "Решение главной боли",
            "Достижение целей и стремлений",
            "Преодоление страхов и барьеров",
            "Образование и инсайты",
            "Социальное доказательство",
            "Трансформация и результаты"
        ]
        
        return pillars
    
    def _create_content_funnel(self, audience_insights: Dict[str, Any],
                               product_profile: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Создание контент-воронки на основе DEEP IMPACT
        
        Воронка основана на:
        - Триггерах (Triggers)
        - Ожиданиях (Expectations)
        - Трансформациях (Transformations)
        """
        funnel = {
            "awareness": [],  # Осведомленность
            "interest": [],   # Интерес
            "consideration": [],  # Рассмотрение
            "decision": [],   # Решение
            "action": []      # Действие
        }
        
        # Генерация контента для каждой стадии
        triggers = audience_insights.get('triggers', [])
        expectations = audience_insights.get('expectations', {})
        
        # Awareness - контент, который привлекает внимание
        funnel["awareness"] = [
            f"Как решить {audience_insights.get('main_pain', 'проблему')}",
            f"Триггеры, которые обостряют {audience_insights.get('main_pain', 'боль')}",
            "Почему текущие решения не работают"
        ]
        
        # Interest - контент, который вызывает интерес
        funnel["interest"] = [
            "Как продукт решает проблему",
            "Кейсы успешного решения",
            "Инсайты о проблеме"
        ]
        
        # Consideration - контент для рассмотрения
        funnel["consideration"] = [
            "Сравнение с альтернативами",
            "Детальное объяснение решения",
            "Ответы на возражения"
        ]
        
        # Decision - контент для принятия решения
        funnel["decision"] = [
            "Социальное доказательство",
            "Ограниченное предложение",
            "Гарантии и снижение рисков"
        ]
        
        # Action - контент для действия
        funnel["action"] = [
            "Призыв к действию",
            "Как начать",
            "Первые шаги"
        ]
        
        return funnel
    
    def _generate_content_calendar(self, content_pillars: List[str],
                                   content_funnel: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Генерация календаря контента на основе столпов и воронки
        """
        calendar = {}
        current_date = datetime.now()
        
        # Генерируем контент на 4 недели вперед
        for week in range(4):
            week_start = current_date + timedelta(weeks=week)
            week_key = week_start.strftime("%Y-%W")
            calendar[week_key] = []
            
            # Распределяем контент по дням недели
            for day in range(5):  # Пн-Пт
                post_date = week_start + timedelta(days=day)
                
                # Выбираем столп и стадию воронки
                pillar = content_pillars[day % len(content_pillars)]
                funnel_stage = list(content_funnel.keys())[week % len(content_funnel)]
                
                calendar[week_key].append({
                    "date": post_date.strftime("%Y-%m-%d"),
                    "pillar": pillar,
                    "funnel_stage": funnel_stage,
                    "topic": f"Тема из столпа '{pillar}' для стадии '{funnel_stage}'",
                    "format": "post",  # post, article, video, etc.
                    "status": "draft"
                })
        
        return calendar
    
    def _determine_tone_of_voice(self, product_profile: Dict[str, Any],
                                 audience_insights: Dict[str, Any]) -> str:
        """Определение tone of voice на основе аудитории"""
        # Анализ языка аудитории из DEEP IMPACT
        audience_language = audience_insights.get('language_patterns', {})
        
        # Определение тона на основе характеристик аудитории
        if audience_insights.get('segment_type') == 'technical':
            return "professional_expert"
        elif audience_insights.get('segment_type') == 'entrepreneur':
            return "confident_inspiring"
        else:
            return "friendly_professional"
    
    def _generate_key_messages(self, product_profile: Dict[str, Any],
                              audience_insights: Dict[str, Any]) -> List[str]:
        """Генерация ключевых сообщений"""
        # Глубокая генерация через LLM, если доступен клиент
        if self.llm_client:
            try:
                import json
                import re
                
                prompt = f"""
На основе продукта и инсайтов DEEP IMPACT создай 5-7 ключевых маркетинговых сообщений.

ПРОДУКТ:
- Название: {product_profile.get('name', '')}
- Описание: {product_profile.get('description', '')}
- Value Proposition: {product_profile.get('value_proposition', '')}

ИНСАЙТЫ АУДИТОРИИ:
- Главная боль: {audience_insights.get('main_pain', '')}
- Главная задача (JTBD): {audience_insights.get('main_task', '')}
- Мотивации: {', '.join(audience_insights.get('motivations', [])) if isinstance(audience_insights.get('motivations'), list) else audience_insights.get('motivations', '')}
- Страхи: {audience_insights.get('fears', '')}
- Ожидания: {audience_insights.get('expectations', '')}

Требования к сообщениям:
1. Каждое сообщение — 1-2 предложения.
2. Чётко связывай боль/задачу аудитории и ценность продукта.
3. Учитывай эмоциональные триггеры и барьеры.

Верни JSON:
{{"messages": ["сообщение 1", "сообщение 2", "..."]}}
"""
                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Ты — маркетолог-стратег. Пиши сообщения на русском, ясно и убедительно."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1200,
                )
                content = response.choices[0].message.content.strip()
                if not content.startswith("{"):
                    match = re.search(r"(\{.*\})", content, re.DOTALL)
                    if match:
                        content = match.group(1)
                
                data = json.loads(content)
                messages = data.get("messages", [])
                # Фильтруем пустые
                messages = [m for m in messages if isinstance(m, str) and m.strip()]
                if messages:
                    return messages
            except Exception:
                # Фолбэк на простую генерацию
                pass
        
        messages = [
            product_profile.get('value_proposition', ''),
            f"Решаем {audience_insights.get('main_pain', 'проблему')}",
            f"Помогаем достичь {audience_insights.get('main_task', 'цели')}"
        ]
        return messages
    
    def _select_channels(self, audience_insights: Dict[str, Any]) -> List[str]:
        """Выбор каналов публикации на основе аудитории"""
        # Определение каналов на основе цифрового следа аудитории
        digital_footprint = audience_insights.get('digital_footprint', {})
        
        channels = []
        if digital_footprint.get('linkedin_active'):
            channels.append("linkedin")
        if digital_footprint.get('twitter_active'):
            channels.append("twitter")
        if digital_footprint.get('telegram_active'):
            channels.append("telegram")
        
        # По умолчанию
        if not channels:
            channels = ["linkedin", "twitter"]
        
        return channels
    
    def _create_posting_schedule(self, channels: List[str]) -> Dict[str, List[str]]:
        """Создание расписания публикаций для каналов"""
        from content_ai_agent.config import Config
        
        schedule = {}
        for channel in channels:
            schedule[channel] = Config.OPTIMAL_POSTING_TIMES.get(
                channel, ["09:00", "13:00", "17:00"]
            )
        
        return schedule
    
    def get_strategy(self) -> Optional[ContentStrategy]:
        """Получить текущую стратегию"""
        return self.strategy

