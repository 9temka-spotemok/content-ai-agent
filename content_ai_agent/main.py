"""
Главный модуль Content AI Agent - оркестратор всех компонентов
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from content_ai_agent.modules.product_intelligence import ProductIntelligence, ProductProfile
from content_ai_agent.modules.content_strategy import ContentStrategyGenerator, ContentStrategy
from content_ai_agent.modules.content_agent import AIContentAgent, ContentPiece, ContentFormat, ContentStatus
from datetime import datetime
from content_ai_agent.modules.scheduler import ContentScheduler, ScheduledPost
from content_ai_agent.modules.analytics import SimpleAnalytics, AnalyticsReport
from content_ai_agent.frameworks.deep_impact import DeepImpactFramework

class ContentAIAgent:
    """
    Главный класс Content AI Agent
    
    Реализует пользовательский путь:
    1. Стартап описывает продукт
    2. AI строит стратегию (используя DEEP IMPACT)
    3. Агент создаёт контент
    4. Пользователь подтверждает
    5. Контент публикуется
    6. Анализируется результат
    """
    
    def __init__(self, llm_client=None):
        """
        Инициализация Content AI Agent
        
        Args:
            llm_client: клиент для работы с LLM (OpenAI, etc.)
        """
        self.llm_client = llm_client
        
        # Инициализация модулей
        self.product_intelligence = ProductIntelligence(llm_client)
        self.deep_impact = DeepImpactFramework()
        self.content_strategy = ContentStrategyGenerator(llm_client)
        self.content_agent = AIContentAgent(llm_client)
        self.scheduler = ContentScheduler()
        self.analytics = SimpleAnalytics()
        
        # Состояние системы
        self.product_profile: Optional[ProductProfile] = None
        self.audience_insights: Dict[str, Any] = {}
        self.strategy: Optional[ContentStrategy] = None
        self.current_stage = "onboarding"
    
    def start_onboarding(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Начало онбординга - описание продукта
        
        Args:
            product_info: информация о продукте:
                - name: название
                - description: описание
                - category: категория
                - features: список функций
                - target_audience: целевая аудитория (предварительно)
        
        Returns:
            Следующие шаги для пользователя
        """
        # Шаг 1: Анализ продукта
        analysis = self.product_intelligence.analyze_product(product_info)
        self.product_profile = self.product_intelligence.create_product_profile({
            **product_info,
            **analysis
        })
        
        self.current_stage = "deep_impact_audit"
        
        return {
            "status": "product_analyzed",
            "product_profile": {
                "name": self.product_profile.name,
                "value_proposition": self.product_profile.value_proposition,
                "key_features": self.product_profile.key_features
            },
            "next_step": "deep_impact_audit",
            "message": "Продукт проанализирован. Теперь начнем глубокий анализ "
                      "целевой аудитории с помощью фреймворка DEEP IMPACT."
        }
    
    def run_deep_impact_audit(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Запуск аудита исходных данных (DEEP IMPACT - Раздел 1)
        
        Args:
            business_context: контекст бизнеса для аудита
        
        Returns:
            Результаты аудита и следующие шаги
        """
        # Получаем промпты для аудита
        audit_prompts = self.deep_impact.get_audit_prompts()
        
        # Обрабатываем этап аудита
        audit_results = self.deep_impact.process_stage("audit", business_context)
        
        self.current_stage = "hypothesis_generation"
        
        return {
            "status": "audit_completed",
            "audit_results": audit_results,
            "next_step": "hypothesis_generation",
            "message": "Аудит данных завершен. Начинаем генерацию гипотез по рынкам."
        }
    
    def generate_hypotheses(self, level: str, input_data: Dict[str, Any], llm_client=None) -> Dict[str, Any]:
        """
        Генерация гипотез на разных уровнях (DEEP IMPACT - Раздел 2)
        
        Args:
            level: уровень ("market", "niche", "audience", "segment", "pain", "task")
            input_data: входные данные для генерации
            llm_client: клиент для работы с LLM
        
        Returns:
            Результаты генерации гипотез
        """
        # Получаем промпты для уровня
        prompts = self.deep_impact.get_hypothesis_generation_prompts(level)
        
        # Генерируем гипотезы через LLM, если доступен
        hypotheses = []
        if llm_client and prompts.get("generate"):
            try:
                # Формируем контекст для генерации
                context = ""
                if self.product_profile:
                    context += f"Продукт: {self.product_profile.name}\n"
                    context += f"Описание: {self.product_profile.description}\n"
                    context += f"Категория: {self.product_profile.category}\n"
                
                # Добавляем контекст предыдущих уровней
                previous_levels = []
                level_order = ["market", "niche", "audience", "segment", "pain", "task"]
                current_index = level_order.index(level) if level in level_order else -1
                for prev_level in level_order[:current_index]:
                    if prev_level in self.deep_impact.hypotheses:
                        prev_choice = self.deep_impact.hypotheses[prev_level].get("final_choice")
                        if prev_choice:
                            previous_levels.append(f"{prev_level}: {prev_choice}")
                
                if previous_levels:
                    context += "\nПредыдущие выборы:\n" + "\n".join(previous_levels)
                
                # Формируем оптимизированный промпт (глубокий анализ по DEEP IMPACT)
                prompt = f"""{prompts['generate']}

КОНТЕКСТ:
{context}

Сгенерируй 10-12 вариантов гипотез для уровня "{level}" с глубоким анализом по фреймворку DEEP IMPACT.
Для КАЖДОЙ гипотезы укажи:
- "name": краткое название гипотезы
- "description": развёрнутое объяснение сути (2-4 предложения)
- "characteristics": 3-7 ключевых характеристик/наблюдений
- "potential": оценка потенциала и рисков (1-2 предложения)
- "emotional_triggers": список эмоциональных триггеров (3-5)
- "data_signals": какие данные/сигналы подтверждают гипотезу (2-4 пункта)
- "risks": риски и ограничения гипотезы (2-4 пункта)

Формат JSON: [{{"name": "...", "description": "...", "characteristics": ["..."], "potential": "...", "emotional_triggers": ["..."], "data_signals": ["..."], "risks": ["..."]}}]
"""
                
                # Вызываем LLM с оптимизациями для скорости
                try:
                    import json
                    import re
                    
                    # Набор моделей, которые пробуем по очереди
                    models_to_try = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
                    last_error: str | None = None
                    parsed_hypotheses = None
                    
                    def _parse_hypotheses(raw: str) -> list:
                        """Парсинг JSON из ответа модели в список гипотез."""
                        text = (raw or "").strip()
                        if not text.startswith("{") and not text.startswith("["):
                            match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
                            if match:
                                text = match.group(1)
                        data = json.loads(text)
                        if isinstance(data, dict) and "hypotheses" in data:
                            return data["hypotheses"]
                        if isinstance(data, list):
                            return data
                        raise ValueError("Unexpected JSON format for hypotheses")
                    
                    for model in models_to_try:
                        try:
                            # Базовые параметры запроса
                            base_kwargs = {
                                "model": model,
                                "messages": [
                                    {
                                        "role": "system",
                                        "content": "Ты - маркетинговый аналитик. Отвечай только в формате JSON.",
                                    },
                                    {"role": "user", "content": prompt},
                                ],
                                "temperature": 0.7,
                                "max_tokens": 2000,
                            }
                            
                            # 1) Пытаемся использовать JSON mode (response_format)
                            try:
                                create_kwargs = dict(base_kwargs)
                                create_kwargs["response_format"] = {"type": "json_object"}
                                create_kwargs["messages"][1]["content"] = (
                                    prompt
                                    + '\n\nВерни JSON объект: {"hypotheses": '
                                      '[{"name": "...", "description": "...", '
                                      '"characteristics": ["..."], "potential": "...", '
                                      '"emotional_triggers": ["..."], '
                                      '"data_signals": ["..."], '
                                      '"risks": ["..."]}]}'
                                )
                                response = llm_client.chat.completions.create(**create_kwargs)
                                content = response.choices[0].message.content
                                parsed_hypotheses = _parse_hypotheses(content)
                                break
                            except Exception:
                                # 2) Фолбэк: обычный режим без response_format
                                response = llm_client.chat.completions.create(**base_kwargs)
                                content = response.choices[0].message.content
                                parsed_hypotheses = _parse_hypotheses(content)
                                break
                        except Exception as model_error:
                            last_error = str(model_error)
                            parsed_hypotheses = None
                            continue
                    
                    if parsed_hypotheses is None:
                        raise RuntimeError(f"All hypothesis models failed: {last_error or 'unknown error'}")
                    
                    hypotheses = parsed_hypotheses
                    
                    # Ограничиваем количество гипотез до 12 для ускорения обработки
                    if len(hypotheses) > 12:
                        hypotheses = hypotheses[:12]
                except Exception:
                    # Если после всех попыток возникла ошибка, создаем демо-гипотезы
                    hypotheses = [
                        {
                            "name": f"Гипотеза {i+1} для {level}",
                            "description": f"Описание гипотезы {i+1}",
                            "characteristics": ["Характеристика 1", "Характеристика 2"],
                            "potential": "Потенциал гипотезы",
                        }
                        for i in range(10)
                    ]
                    
            except Exception as e:
                # Если ошибка, создаем демо-гипотезы
                hypotheses = [
                    {"name": f"Гипотеза {i+1} для {level}", "description": f"Описание гипотезы {i+1}", 
                     "characteristics": ["Характеристика 1", "Характеристика 2"], 
                     "potential": "Потенциал гипотезы"} 
                    for i in range(10)
                ]
        else:
            # Демо-гипотезы, если LLM недоступен
            hypotheses = [
                {"name": f"Гипотеза {i+1} для {level}", "description": f"Описание гипотезы {i+1}", 
                 "characteristics": ["Характеристика 1", "Характеристика 2"], 
                 "potential": "Потенциал гипотезы"} 
                for i in range(10)
            ]
        
        # Сохраняем результаты
        results = {
            "stage": level,
            "hypotheses": hypotheses,
            "evaluation": {},
            "top_3": [],
            "final_choice": None
        }
        
        if level not in self.deep_impact.hypotheses:
            self.deep_impact.hypotheses[level] = {}
        self.deep_impact.hypotheses[level] = results
        
        return {
            "status": f"{level}_hypotheses_generated",
            "results": results,
            "next_level": self._get_next_level(level),
            "message": f"Гипотезы по {level} сгенерированы."
        }
    
    def _get_next_level(self, level: str) -> Optional[str]:
        """Получить следующий уровень"""
        levels = ["market", "niche", "audience", "segment", "pain", "task"]
        try:
            current_index = levels.index(level)
            if current_index < len(levels) - 1:
                return levels[current_index + 1]
        except ValueError:
            pass
        return None
    
    def expand_audience_insights(self) -> Dict[str, Any]:
        """
        Расширение понимания аудитории (DEEP IMPACT - Раздел 3)
        
        Returns:
            Расширенные инсайты о аудитории
        """
        # Получаем промпты для расширения
        expansion_prompts = self.deep_impact.get_audience_expansion_prompts()
        
        # Используем данные из предыдущих этапов
        input_data = {
            "selected_segment": self.deep_impact.hypotheses.get("segment", {}),
            "selected_pain": self.deep_impact.hypotheses.get("pain", {}),
            "selected_task": self.deep_impact.hypotheses.get("task", {})
        }
        
        # Глубокое расширение инсайтов через LLM, если доступен
        if self.llm_client:
            try:
                import json
                import re
                
                segment_choice = input_data["selected_segment"].get("final_choice") or ""
                pain_choice = input_data["selected_pain"].get("final_choice") or ""
                task_choice = input_data["selected_task"].get("final_choice") or ""
                
                framework_instructions = "\n".join(expansion_prompts.values())
                
                prompt = f"""
Ты — маркетинговый аналитик, работающий по фреймворку DEEP IMPACT.
У тебя есть выбранные гипотезы:
- Сегмент: {segment_choice}
- Главная боль: {pain_choice}
- Главная задача (JTBD): {task_choice}

Твоя задача — глубоко раскрыть аудиторию по следующим направлениям (используй инструкции ниже):
{framework_instructions}

Сформируй единый, целостный портрет аудитории с акцентом на мотивации, страхи, триггеры и язык, которым они описывают свою реальность.

Верни результат строго в формате JSON со структурой:
{{
  "deep_insights": "текстовое резюме (3-5 абзацев)",
  "motivations": {{
    "core": "ядро мотивации (1 абзац)",
    "rational": "рациональные мотивы",
    "emotional": "эмоциональные мотивы"
  }},
  "triggers": ["триггер 1", "триггер 2", "..."],
  "language_patterns": {{
    "common_phrases": ["фраза 1", "фраза 2", "..."],
    "style": "как обычно говорит аудитория",
    "do_not_say": ["чего избегать в коммуникации"]
  }},
  "expectations": {{
    "from_solution": "ожидания от решения",
    "from_brand": "ожидания от бренда/коммуникации"
  }},
  "aspirations": ["мечта/идеальный результат 1", "мечта 2", "..."],
  "fears": {{
    "barriers": ["барьер 1", "барьер 2", "..."],
    "negative_beliefs": ["убеждение 1", "убеждение 2", "..."]
  }}
}}
"""
                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Ты — эксперт по глубинному анализу аудитории. "
                                "Всегда следуй структуре JSON и не добавляй лишний текст."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=2200,
                )
                
                content = response.choices[0].message.content.strip()
                if not content.startswith("{"):
                    match = re.search(r"(\{.*\})", content, re.DOTALL)
                    if match:
                        content = match.group(1)
                
                expansion_results = json.loads(content)
            except Exception:
                # Фолбэк к базовой реализации фреймворка
                expansion_results = self.deep_impact.process_stage("expansion", input_data)
        else:
            # Если LLM недоступен, используем базовую реализацию
            expansion_results = self.deep_impact.process_stage("expansion", input_data)
        
        # Формируем итоговые инсайты
        self.audience_insights = {
            "main_pain": self.deep_impact.hypotheses.get("pain", {}).get("final_choice", ""),
            "main_task": self.deep_impact.hypotheses.get("task", {}).get("final_choice", ""),
            "target_segment": self.deep_impact.hypotheses.get("segment", {}).get("final_choice", ""),
            "motivations": expansion_results.get("motivations", {}),
            "triggers": expansion_results.get("triggers", []),
            "language_patterns": expansion_results.get("language_patterns", {}),
            "expectations": expansion_results.get("expectations", {}),
            "aspirations": expansion_results.get("aspirations", {}),
            "fears": expansion_results.get("fears", {}),
            **expansion_results
        }
        
        self.current_stage = "strategy_generation"
        
        return {
            "status": "audience_insights_expanded",
            "insights": self.audience_insights,
            "next_step": "strategy_generation",
            "message": "Инсайты о аудитории расширены. Генерируем контент-стратегию."
        }
    
    def generate_content_strategy(self, business_goals: List[str]) -> ContentStrategy:
        """
        Генерация контент-стратегии на основе инсайтов
        
        Args:
            business_goals: бизнес-цели
        
        Returns:
            Контент-стратегия
        """
        if not self.product_profile:
            raise ValueError("Product profile not set. Run start_onboarding first.")
        
        if not self.audience_insights:
            raise ValueError("Audience insights not set. Run expand_audience_insights first.")
        
        # Конвертируем ProductProfile в dict
        product_dict = {
            "name": self.product_profile.name,
            "description": self.product_profile.description,
            "category": self.product_profile.category,
            "target_audience": self.product_profile.target_audience,
            "value_proposition": self.product_profile.value_proposition,
            "key_features": self.product_profile.key_features,
            "pain_points_solved": self.product_profile.pain_points_solved,
            "competitive_advantages": self.product_profile.competitive_advantages,
            "tone_of_voice": self.product_profile.tone_of_voice,
            "key_messages": self.product_profile.key_messages
        }
        
        # Генерируем стратегию
        self.strategy = self.content_strategy.generate_strategy(
            product_profile=product_dict,
            audience_insights=self.audience_insights,
            business_goals=business_goals
        )
        
        self.current_stage = "content_generation"
        
        return self.strategy
    
    def generate_content_batch(self, count: int = 10) -> List[ContentPiece]:
        """
        Генерация батча контента на основе стратегии
        
        Args:
            count: количество постов для генерации
        
        Returns:
            Список сгенерированного контента
        """
        if not self.strategy:
            raise ValueError("Strategy not set. Run generate_content_strategy first.")
        
        generated_content = []
        
        # Конвертируем стратегию в dict
        strategy_dict = {
            "pillar": "",
            "funnel_stage": "",
            "tone_of_voice": self.strategy.tone_of_voice,
            "key_messages": self.strategy.key_messages
        }
        
        # Конвертируем ProductProfile в dict
        product_dict = {
            "name": self.product_profile.name,
            "value_proposition": self.product_profile.value_proposition,
            "key_features": self.product_profile.key_features
        }
        
        # Генерируем контент из календаря стратегии
        posts_generated = 0
        
        # Проверяем, есть ли календарь с постами
        if self.strategy.content_calendar:
            for week_key, week_posts in list(self.strategy.content_calendar.items())[:4]:  # Первые 4 недели
                if not week_posts:
                    continue
                    
                for post_plan in week_posts:
                    if posts_generated >= count:
                        break
                        
                    strategy_dict["pillar"] = post_plan.get("pillar", self.strategy.content_pillars[0] if self.strategy.content_pillars else "")
                    strategy_dict["funnel_stage"] = post_plan.get("funnel_stage", "awareness")
                    
                    content = self.content_agent.generate_content(
                        topic=post_plan.get("topic", f"Пост {posts_generated + 1}"),
                        content_strategy=strategy_dict,
                        product_profile=product_dict,
                        audience_insights=self.audience_insights,
                        format=ContentFormat.POST,
                        channel=post_plan.get("channel", self.strategy.channels[0] if self.strategy.channels else "linkedin")
                    )
                    
                    generated_content.append(content)
                    posts_generated += 1
                
                if posts_generated >= count:
                    break
        
        # Если календаря нет или недостаточно постов, генерируем на основе столпов
        if posts_generated < count:
            import random
            pillars = self.strategy.content_pillars if self.strategy.content_pillars else ["Образовательный контент", "Решение проблем"]
            funnel_stages = list(self.strategy.content_funnel.keys()) if self.strategy.content_funnel else ["awareness", "interest", "decision"]
            channels = self.strategy.channels if self.strategy.channels else ["linkedin"]
            
            # Генерируем темы на основе столпов и стадий воронки
            topics_list = []
            for pillar in pillars:
                for stage in funnel_stages:
                    topics_list.append(f"{pillar} - {stage}")
            
            # Если тем недостаточно, добавляем базовые
            if len(topics_list) < (count - posts_generated):
                for i in range(count - posts_generated - len(topics_list)):
                    topics_list.append(f"Пост {posts_generated + len(topics_list) + i + 1}")
            
            for i in range(posts_generated, count):
                topic_index = (i - posts_generated) % len(topics_list)
                topic = topics_list[topic_index]
                
                pillar = pillars[(i - posts_generated) % len(pillars)]
                funnel_stage = funnel_stages[(i - posts_generated) % len(funnel_stages)]
                channel = channels[(i - posts_generated) % len(channels)]
                
                strategy_dict["pillar"] = pillar
                strategy_dict["funnel_stage"] = funnel_stage
                
                try:
                    content = self.content_agent.generate_content(
                        topic=topic,
                        content_strategy=strategy_dict,
                        product_profile=product_dict,
                        audience_insights=self.audience_insights,
                        format=ContentFormat.POST,
                        channel=channel
                    )
                    
                    # Проверяем, что контент не пустой
                    if not content.content or len(content.content.strip()) < 10:
                        # Если контент пустой, генерируем базовый
                        content.content = f"Контент на тему: {topic}\n\nЭтот пост посвящен {pillar.lower()} для стадии {funnel_stage}.\n\nПожалуйста, настройте API ключ OpenAI для полноценной генерации контента."
                    
                    generated_content.append(content)
                except Exception as e:
                    # Если ошибка генерации, создаем контент с сообщением об ошибке
                    import uuid
                    from datetime import datetime
                    error_content = ContentPiece(
                        id=f"content_error_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
                        title=f"Пост {i + 1} - {topic}",
                        content=f"Ошибка при генерации контента: {str(e)}\n\nТема: {topic}",
                        format=ContentFormat.POST,
                        pillar=pillar,
                        funnel_stage=funnel_stage,
                        channel=channel,
                        tone_of_voice=strategy_dict.get('tone_of_voice', 'professional'),
                        key_messages=strategy_dict.get('key_messages', []),
                        status=ContentStatus.DRAFT,
                        created_at=datetime.now()
                    )
                    generated_content.append(error_content)
        
        # Убеждаемся, что вернули ровно столько постов, сколько запрошено
        return generated_content[:count]
    
    def approve_and_schedule_content(self, content_ids: List[str],
                                   start_date: datetime,
                                   channels: List[str]) -> Dict[str, List[ScheduledPost]]:
        """
        Подтверждение и планирование контента
        
        Args:
            content_ids: ID контента для публикации
            start_date: дата начала публикаций
            channels: каналы публикации
        
        Returns:
            Расписание публикаций
        """
        # Получаем контент по ID
        content_to_schedule = []
        for content_id in content_ids:
            content = self.content_agent.get_content_by_id(content_id)
            if content:
                content.status = ContentStatus.APPROVED
                content_to_schedule.append(content)
        
        # Создаем расписание
        schedule = self.scheduler.create_schedule(
            content_pieces=content_to_schedule,
            start_date=start_date,
            channels=channels,
            posts_per_week=5
        )
        
        self.current_stage = "scheduled"
        
        return schedule
    
    def get_analytics_report(self, days: int = 30, content_list: Optional[List[ContentPiece]] = None) -> AnalyticsReport:
        """
        Получение отчета по аналитике
        
        Args:
            days: количество дней для анализа
            content_list: опциональный список контента для анализа
        
        Returns:
            Отчет по аналитике
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Получаем контент из переданного списка или из истории агента
        if content_list is not None:
            content_to_analyze = content_list
        else:
            # Используем контент из истории агента, если доступен
            try:
                content_to_analyze = self.content_agent.get_content_history()
            except:
                content_to_analyze = []
        
        # Для демо-режима: если есть контент, но нет метрик, генерируем демо-метрики
        if content_to_analyze:
            import random
            for content in content_to_analyze:
                # Если у контента нет метрик, создаем демо-метрики
                if content.id not in self.analytics.metrics:
                    demo_metrics = {
                        'views': random.randint(50, 500),
                        'likes': random.randint(5, 50),
                        'comments': random.randint(0, 10),
                        'shares': random.randint(0, 5),
                        'impressions': random.randint(100, 1000),
                        'reach': random.randint(80, 800)
                    }
                    self.analytics.track_content(content, demo_metrics)
                
                # Если контент не опубликован, но был создан в указанный период, считаем его как опубликованный
                if not content.published_at and content.created_at:
                    if start_date <= content.created_at <= end_date:
                        content.published_at = content.created_at
                        content.status = ContentStatus.PUBLISHED
        
        report = self.analytics.generate_report(
            start_date=start_date,
            end_date=end_date,
            content_list=content_to_analyze
        )
        
        return report
    
    def _get_next_level(self, current_level: str) -> Optional[str]:
        """Получить следующий уровень генерации гипотез"""
        levels = ["market", "niche", "audience", "segment", "pain", "task"]
        try:
            current_index = levels.index(current_level)
            if current_index < len(levels) - 1:
                return levels[current_index + 1]
        except ValueError:
            pass
        return None
    
    def get_current_state(self) -> Dict[str, Any]:
        """Получить текущее состояние системы"""
        return {
            "stage": self.current_stage,
            "product_profile": {
                "name": self.product_profile.name if self.product_profile else None,
                "value_proposition": self.product_profile.value_proposition if self.product_profile else None
            },
            "has_audience_insights": bool(self.audience_insights),
            "has_strategy": self.strategy is not None,
            "content_count": len(self.content_agent.get_content_history()),
            "scheduled_posts": sum(
                len(posts) for posts in self.scheduler.get_schedule().values()
            )
        }

