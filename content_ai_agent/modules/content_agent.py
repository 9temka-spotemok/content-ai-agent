"""
Модуль AI Content Agent - генерация контента
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ContentFormat(Enum):
    """Форматы контента"""
    POST = "post"
    ARTICLE = "article"
    THREAD = "thread"
    VIDEO_SCRIPT = "video_script"
    EMAIL = "email"
    AD = "ad"

class ContentStatus(Enum):
    """Статусы контента"""
    DRAFT = "draft"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"

@dataclass
class ContentPiece:
    """Единица контента"""
    id: str
    title: str
    content: str
    format: ContentFormat
    pillar: str
    funnel_stage: str
    channel: str
    tone_of_voice: str
    key_messages: List[str]
    status: ContentStatus
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    metrics: Optional[Dict[str, Any]] = None

class AIContentAgent:
    """
    AI агент для генерации контента
    
    Функции:
    - Генерация постов
    - Адаптация под стиль
    - Контент под каналы
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.content_history: List[ContentPiece] = []
        self.style_guide: Dict[str, Any] = {}
    
    def generate_content(self, 
                        topic: str,
                        content_strategy: Dict[str, Any],
                        product_profile: Dict[str, Any],
                        audience_insights: Dict[str, Any],
                        format: ContentFormat = ContentFormat.POST,
                        channel: str = "linkedin") -> ContentPiece:
        """
        Генерация контента на основе стратегии и инсайтов
        
        Args:
            topic: тема контента
            content_strategy: контент-стратегия
            product_profile: профиль продукта
            audience_insights: инсайты аудитории из DEEP IMPACT
            format: формат контента
            channel: канал публикации
        """
        # Формирование промпта для генерации
        prompt = self._build_generation_prompt(
            topic, content_strategy, product_profile, 
            audience_insights, format, channel
        )
        
        # Генерация контента через LLM
        generated_content = self._call_llm(prompt)
        
        # Создание объекта контента с уникальным ID
        import uuid
        unique_id = f"content_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        content_piece = ContentPiece(
            id=unique_id,
            title=self._extract_title(generated_content, topic),
            content=generated_content,
            format=format,
            pillar=content_strategy.get('pillar', ''),
            funnel_stage=content_strategy.get('funnel_stage', ''),
            channel=channel,
            tone_of_voice=content_strategy.get('tone_of_voice', 'professional'),
            key_messages=content_strategy.get('key_messages', []),
            status=ContentStatus.DRAFT,
            created_at=datetime.now()
        )
        
        self.content_history.append(content_piece)
        return content_piece
    
    def _build_generation_prompt(self,
                                 topic: str,
                                 content_strategy: Dict[str, Any],
                                 product_profile: Dict[str, Any],
                                 audience_insights: Dict[str, Any],
                                 format: ContentFormat,
                                 channel: str) -> str:
        """
        Построение промпта для генерации контента на основе DEEP IMPACT
        """
        # Использование инсайтов из DEEP IMPACT
        main_pain = audience_insights.get('main_pain', '')
        main_task = audience_insights.get('main_task', '')
        motivations_raw = audience_insights.get('motivations', [])
        language_patterns = audience_insights.get('language_patterns', {})
        triggers = audience_insights.get('triggers', [])

        # Приводим мотивации к списку строк (учёт новой структуры из DEEP IMPACT)
        motivations_list: List[str] = []
        if isinstance(motivations_raw, dict):
            # Ожидаем структуру {"core": "...", "rational": "...", "emotional": "..."}
            for key in ["core", "emotional", "rational"]:
                value = motivations_raw.get(key)
                if isinstance(value, str) and value.strip():
                    motivations_list.append(value.strip())
        elif isinstance(motivations_raw, (list, tuple, set)):
            motivations_list = [str(m).strip() for m in motivations_raw if str(m).strip()]
        elif isinstance(motivations_raw, str) and motivations_raw.strip():
            motivations_list = [motivations_raw.strip()]

        motivations_text = ', '.join(motivations_list[:3]) if motivations_list else 'Не указано'
        
        prompt = f"""
Ты - эксперт по контент-маркетингу, создающий контент для {channel}.

КОНТЕКСТ ПРОДУКТА:
Название: {product_profile.get('name', '')}
Value Proposition: {product_profile.get('value_proposition', '')}
Ключевые функции: {', '.join(product_profile.get('key_features', []))}

ИНСАЙТЫ ЦЕЛЕВОЙ АУДИТОРИИ (из фреймворка DEEP IMPACT):
- Главная боль: {main_pain}
- Главная задача (JTBD): {main_task}
- Мотивации: {motivations_text}
- Язык аудитории: {language_patterns.get('common_phrases', 'Профессиональный')}
- Триггеры боли: {', '.join(triggers[:3]) if triggers else 'Не указано'}

СТРАТЕГИЯ КОНТЕНТА:
- Контентный столп: {content_strategy.get('pillar', '')}
- Стадия воронки: {content_strategy.get('funnel_stage', '')}
- Tone of Voice: {content_strategy.get('tone_of_voice', 'professional')}
- Ключевые сообщения: {', '.join(content_strategy.get('key_messages', []))}

ЗАДАНИЕ:
Создай {format.value} на тему: "{topic}"

ТРЕБОВАНИЯ:
1. Используй язык целевой аудитории из инсайтов
2. Обращайся к главной боли и задаче
3. Используй эмоциональные триггеры
4. Соответствуй tone of voice
5. Адаптируй под формат {format.value} для канала {channel}
6. Включи призыв к действию, если уместно

ФОРМАТ ДЛЯ {channel.upper()}:
"""
        
        # Добавление специфики канала
        if channel == "linkedin":
            prompt += """
- Длина: 1300-3000 символов
- Структура: Заголовок, основной текст, призыв к действию
- Стиль: Профессиональный, но живой
- Используй хештеги (3-5)
- Добавь вопрос для вовлечения
"""
        elif channel == "twitter":
            prompt += """
- Длина: до 280 символов (или тред из 3-5 твитов)
- Стиль: Краткий, цепляющий
- Используй хештеги (1-2)
- Эмодзи уместны
"""
        elif channel == "telegram":
            prompt += """
- Длина: 500-1500 символов
- Стиль: Неформальный, дружелюбный
- Можно использовать эмодзи
- Призыв к обсуждению
"""
        
        prompt += "\n\nСоздай контент:"
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """
        Вызов LLM для генерации контента
        
        В реальной реализации здесь будет вызов OpenAI API или другого LLM
        """
        # Реальная генерация через LLM
        if self.llm_client:
            try:
                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Ты - эксперт по контент-маркетингу. Создавай качественный, вовлекающий контент на русском языке."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=2000
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                # Если ошибка, возвращаем базовый контент
                error_msg = str(e)
                topic = prompt.split('тему: ')[1].split('"')[0] if 'тему: ' in prompt else 'Не указана'
                return f"Ошибка генерации контента: {error_msg}\n\nТема: {topic}"
        
        # Если LLM недоступен, возвращаем информативное сообщение
        topic = prompt.split('тему: ')[1].split('"')[0] if 'тему: ' in prompt else 'контент'
        return f"""Привет! 

Это демо-контент на тему "{topic}". 

Для полноценной генерации контента необходимо настроить API ключ OpenAI.

Тем не менее, вот структура контента, который был бы создан:
- Вступление, привлекающее внимание
- Основная часть с полезной информацией
- Призыв к действию

Настройте API ключ в настройках для получения реального контента."""
    
    def _extract_title(self, content: str, topic: str) -> str:
        """Извлечение заголовка из контента"""
        import re
        
        # Убираем лишние пробелы и переносы строк
        content_clean = content.strip()
        
        # Пытаемся найти заголовок в формате "**Заголовок:**" "текст"
        pattern1 = r'\*\*Заголовок:\*\*\s*["\']?([^"\'\n]+)["\']?'
        match1 = re.search(pattern1, content_clean, re.IGNORECASE)
        if match1:
            title = match1.group(1).strip()
            if title and len(title) < 150:
                return title
        
        # Пытаемся найти заголовок в кавычках в первой строке
        pattern2 = r'["\']([^"\'\n]{10,150})["\']'
        match2 = re.search(pattern2, content_clean[:500])
        if match2:
            title = match2.group(1).strip()
            if title and not title.startswith('Заголовок'):
                return title
        
        # Ищем первую строку без маркдаун-форматирования
        lines = content_clean.split('\n')
        for line in lines[:5]:
            line_clean = line.strip()
            # Убираем markdown форматирование
            line_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', line_clean)
            line_clean = re.sub(r'#+\s*', '', line_clean)
            line_clean = re.sub(r'["\']', '', line_clean)
            
            # Пропускаем строки с метками типа "Заголовок:", "Тема:" и т.д.
            if line_clean and len(line_clean) > 10 and len(line_clean) < 150:
                if not any(marker in line_clean.lower() for marker in ['заголовок:', 'тема:', '**заголовок', 'title:']):
                    return line_clean
        
        # Если ничего не нашли, возвращаем topic
        return topic if topic else "Без заголовка"
    
    def adapt_to_style(self, content: ContentPiece, 
                       new_style: Dict[str, Any]) -> ContentPiece:
        """
        Адаптация контента под новый стиль
        
        Args:
            content: исходный контент
            new_style: новый стиль (tone, format, channel)
        """
        adaptation_prompt = f"""
Адаптируй следующий контент под новый стиль:

ИСХОДНЫЙ КОНТЕНТ:
{content.content}

НОВЫЙ СТИЛЬ:
- Tone of Voice: {new_style.get('tone_of_voice', content.tone_of_voice)}
- Формат: {new_style.get('format', content.format.value)}
- Канал: {new_style.get('channel', content.channel)}

Сохрани ключевые сообщения, но адаптируй под новый стиль.
"""
        
        adapted_content = self._call_llm(adaptation_prompt)
        
        # Создаем новую версию контента
        adapted_piece = ContentPiece(
            id=f"{content.id}_adapted",
            title=content.title,
            content=adapted_content,
            format=ContentFormat(new_style.get('format', content.format.value)),
            pillar=content.pillar,
            funnel_stage=content.funnel_stage,
            channel=new_style.get('channel', content.channel),
            tone_of_voice=new_style.get('tone_of_voice', content.tone_of_voice),
            key_messages=content.key_messages,
            status=ContentStatus.DRAFT,
            created_at=datetime.now()
        )
        
        return adapted_piece
    
    def generate_for_channel(self, content: ContentPiece, 
                            target_channel: str) -> ContentPiece:
        """
        Адаптация контента под конкретный канал
        
        Args:
            content: исходный контент
            target_channel: целевой канал
        """
        channel_adaptations = {
            "linkedin": {
                "format": "article",
                "tone_of_voice": "professional_engaging",
                "length": "long"
            },
            "twitter": {
                "format": "thread",
                "tone_of_voice": "concise_engaging",
                "length": "short"
            },
            "telegram": {
                "format": "post",
                "tone_of_voice": "friendly_casual",
                "length": "medium"
            }
        }
        
        style = channel_adaptations.get(target_channel, {})
        style['channel'] = target_channel
        
        return self.adapt_to_style(content, style)
    
    def get_content_history(self) -> List[ContentPiece]:
        """Получить историю сгенерированного контента"""
        return self.content_history
    
    def get_content_by_id(self, content_id: str) -> Optional[ContentPiece]:
        """Получить контент по ID"""
        for content in self.content_history:
            if content.id == content_id:
                return content
        return None

