"""
Главный модуль Content AI Agent - оркестратор всех компонентов
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from content_ai_agent.modules.product_intelligence import ProductIntelligence, ProductProfile
from content_ai_agent.modules.content_strategy import ContentStrategyGenerator, ContentStrategy
from content_ai_agent.modules.content_agent import AIContentAgent, ContentPiece, ContentFormat, ContentStatus
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
    
    def generate_hypotheses(self, level: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерация гипотез на разных уровнях (DEEP IMPACT - Раздел 2)
        
        Args:
            level: уровень ("market", "niche", "audience", "segment", "pain", "task")
            input_data: входные данные для генерации
        
        Returns:
            Результаты генерации гипотез
        """
        # Получаем промпты для уровня
        prompts = self.deep_impact.get_hypothesis_generation_prompts(level)
        
        # Обрабатываем этап
        results = self.deep_impact.process_stage(level, input_data)
        
        # Сохраняем результаты
        if level not in self.deep_impact.hypotheses:
            self.deep_impact.hypotheses[level] = {}
        self.deep_impact.hypotheses[level] = results
        
        return {
            "status": f"{level}_hypotheses_generated",
            "results": results,
            "next_level": self._get_next_level(level),
            "message": f"Гипотезы по {level} сгенерированы."
        }
    
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
        
        # Обрабатываем расширение
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
        for week_key, week_posts in list(self.strategy.content_calendar.items())[:2]:  # Первые 2 недели
            for post_plan in week_posts[:count]:
                strategy_dict["pillar"] = post_plan["pillar"]
                strategy_dict["funnel_stage"] = post_plan["funnel_stage"]
                
                content = self.content_agent.generate_content(
                    topic=post_plan["topic"],
                    content_strategy=strategy_dict,
                    product_profile=product_dict,
                    audience_insights=self.audience_insights,
                    format=ContentFormat.POST,
                    channel=post_plan.get("channel", "linkedin")
                )
                
                generated_content.append(content)
                
                if len(generated_content) >= count:
                    break
            
            if len(generated_content) >= count:
                break
        
        return generated_content
    
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
    
    def get_analytics_report(self, days: int = 30) -> AnalyticsReport:
        """
        Получение отчета по аналитике
        
        Args:
            days: количество дней для анализа
        
        Returns:
            Отчет по аналитике
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Получаем опубликованный контент
        published_content = [
            c for c in self.content_agent.get_content_history()
            if c.status == ContentStatus.PUBLISHED
        ]
        
        report = self.analytics.generate_report(
            start_date=start_date,
            end_date=end_date,
            content_list=published_content
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

