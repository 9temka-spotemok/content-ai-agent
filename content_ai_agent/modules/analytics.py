"""
Модуль Simple Analytics - базовая аналитика контента
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from content_ai_agent.modules.content_agent import ContentPiece, ContentStatus

@dataclass
class ContentMetrics:
    """Метрики контента"""
    content_id: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    
    def calculate_engagement_rate(self):
        """Расчет engagement rate"""
        if self.impressions > 0:
            self.engagement_rate = (
                (self.likes + self.comments + self.shares) / self.impressions
            ) * 100
        return self.engagement_rate

@dataclass
class AnalyticsReport:
    """Отчет по аналитике"""
    period_start: datetime
    period_end: datetime
    total_posts: int
    total_views: int
    total_engagement: int
    avg_engagement_rate: float
    top_performing_content: List[Dict[str, Any]]
    channel_performance: Dict[str, Dict[str, Any]]
    pillar_performance: Dict[str, Dict[str, Any]]
    funnel_stage_performance: Dict[str, Dict[str, Any]]

class SimpleAnalytics:
    """
    Простая аналитика контента
    
    Функции:
    - Базовые метрики
    - Отчеты
    - Рекомендации
    """
    
    def __init__(self):
        self.metrics: Dict[str, ContentMetrics] = {}  # content_id -> metrics
    
    def track_content(self, content: ContentPiece, 
                     metrics_data: Dict[str, Any]) -> ContentMetrics:
        """
        Отслеживание метрик контента
        
        Args:
            content: контент
            metrics_data: данные метрик
        """
        if content.id not in self.metrics:
            self.metrics[content.id] = ContentMetrics(content_id=content.id)
        
        metrics = self.metrics[content.id]
        
        # Обновление метрик
        metrics.views = metrics_data.get('views', metrics.views)
        metrics.likes = metrics_data.get('likes', metrics.likes)
        metrics.comments = metrics_data.get('comments', metrics.comments)
        metrics.shares = metrics_data.get('shares', metrics.shares)
        metrics.clicks = metrics_data.get('clicks', metrics.clicks)
        metrics.reach = metrics_data.get('reach', metrics.reach)
        metrics.impressions = metrics_data.get('impressions', metrics.impressions)
        
        # Расчет engagement rate
        metrics.calculate_engagement_rate()
        
        # Сохранение в контент
        if content.metrics is None:
            content.metrics = {}
        content.metrics.update(metrics_data)
        
        return metrics
    
    def get_content_metrics(self, content_id: str) -> Optional[ContentMetrics]:
        """Получить метрики контента"""
        return self.metrics.get(content_id)
    
    def generate_report(self, 
                      start_date: datetime,
                      end_date: datetime,
                      content_list: List[ContentPiece]) -> AnalyticsReport:
        """
        Генерация отчета по аналитике
        
        Args:
            start_date: начало периода
            end_date: конец периода
            content_list: список контента для анализа
        """
        # Фильтрация контента по периоду
        # Используем published_at если есть, иначе created_at
        period_content = []
        for c in content_list:
            date_to_check = c.published_at if c.published_at else c.created_at
            if date_to_check and start_date <= date_to_check <= end_date:
                period_content.append(c)
        
        # Общие метрики
        total_posts = len(period_content)
        total_views = sum(
            self.metrics.get(c.id, ContentMetrics(c.id)).views 
            for c in period_content
        )
        total_engagement = sum(
            self.metrics.get(c.id, ContentMetrics(c.id)).likes +
            self.metrics.get(c.id, ContentMetrics(c.id)).comments +
            self.metrics.get(c.id, ContentMetrics(c.id)).shares
            for c in period_content
        )
        
        # Средний engagement rate
        engagement_rates = [
            self.metrics.get(c.id, ContentMetrics(c.id)).engagement_rate
            for c in period_content
            if self.metrics.get(c.id, ContentMetrics(c.id)).engagement_rate > 0
        ]
        avg_engagement_rate = (
            sum(engagement_rates) / len(engagement_rates) 
            if engagement_rates else 0.0
        )
        
        # Топ контент
        content_with_metrics = [
            {
                "content": c,
                "metrics": self.metrics.get(c.id, ContentMetrics(c.id)),
                "total_engagement": (
                    self.metrics.get(c.id, ContentMetrics(c.id)).likes +
                    self.metrics.get(c.id, ContentMetrics(c.id)).comments +
                    self.metrics.get(c.id, ContentMetrics(c.id)).shares
                )
            }
            for c in period_content
        ]
        content_with_metrics.sort(
            key=lambda x: x["total_engagement"], 
            reverse=True
        )
        top_performing = content_with_metrics[:5]
        
        # Производительность по каналам
        channel_performance = {}
        for c in period_content:
            channel = c.channel
            if channel not in channel_performance:
                channel_performance[channel] = {
                    "posts": 0,
                    "views": 0,
                    "engagement": 0,
                    "avg_engagement_rate": 0.0
                }
            
            metrics = self.metrics.get(c.id, ContentMetrics(c.id))
            channel_performance[channel]["posts"] += 1
            channel_performance[channel]["views"] += metrics.views
            channel_performance[channel]["engagement"] += (
                metrics.likes + metrics.comments + metrics.shares
            )
        
        # Средний engagement rate по каналам
        for channel in channel_performance:
            channel_posts = [
                c for c in period_content if c.channel == channel
            ]
            channel_rates = [
                self.metrics.get(c.id, ContentMetrics(c.id)).engagement_rate
                for c in channel_posts
                if self.metrics.get(c.id, ContentMetrics(c.id)).engagement_rate > 0
            ]
            if channel_rates:
                channel_performance[channel]["avg_engagement_rate"] = (
                    sum(channel_rates) / len(channel_rates)
                )
        
        # Производительность по столпам
        pillar_performance = {}
        for c in period_content:
            pillar = c.pillar
            if pillar not in pillar_performance:
                pillar_performance[pillar] = {
                    "posts": 0,
                    "avg_engagement_rate": 0.0
                }
            
            metrics = self.metrics.get(c.id, ContentMetrics(c.id))
            pillar_performance[pillar]["posts"] += 1
        
        # Производительность по стадиям воронки
        funnel_performance = {}
        for c in period_content:
            stage = c.funnel_stage
            if stage not in funnel_performance:
                funnel_performance[stage] = {
                    "posts": 0,
                    "avg_engagement_rate": 0.0
                }
            
            metrics = self.metrics.get(c.id, ContentMetrics(c.id))
            funnel_performance[stage]["posts"] += 1
        
        report = AnalyticsReport(
            period_start=start_date,
            period_end=end_date,
            total_posts=total_posts,
            total_views=total_views,
            total_engagement=total_engagement,
            avg_engagement_rate=avg_engagement_rate,
            top_performing_content=[
                {
                    "content_id": item["content"].id,
                    "title": item["content"].title,
                    "engagement": item["total_engagement"],
                    "engagement_rate": item["metrics"].engagement_rate
                }
                for item in top_performing
            ],
            channel_performance=channel_performance,
            pillar_performance=pillar_performance,
            funnel_stage_performance=funnel_performance
        )
        
        return report
    
    def get_recommendations(self, report: AnalyticsReport) -> List[str]:
        """
        Получить рекомендации на основе аналитики
        
        Args:
            report: отчет по аналитике
        """
        recommendations = []
        
        # Анализ engagement rate
        if report.avg_engagement_rate < 2.0:
            recommendations.append(
                "Низкий engagement rate. Рекомендуется пересмотреть tone of voice "
                "и формат контента для лучшего вовлечения аудитории."
            )
        
        # Анализ каналов
        best_channel = max(
            report.channel_performance.items(),
            key=lambda x: x[1].get("avg_engagement_rate", 0)
        )[0] if report.channel_performance else None
        
        worst_channel = min(
            report.channel_performance.items(),
            key=lambda x: x[1].get("avg_engagement_rate", 0)
        )[0] if report.channel_performance else None
        
        if best_channel and worst_channel:
            recommendations.append(
                f"Лучший канал по engagement: {best_channel}. "
                f"Рекомендуется увеличить активность на этом канале."
            )
            recommendations.append(
                f"Канал {worst_channel} показывает низкую эффективность. "
                f"Рекомендуется пересмотреть стратегию для этого канала."
            )
        
        # Анализ столпов
        if report.pillar_performance:
            best_pillar = max(
                report.pillar_performance.items(),
                key=lambda x: x[1].get("avg_engagement_rate", 0)
            )[0]
            recommendations.append(
                f"Столп '{best_pillar}' показывает лучшие результаты. "
                f"Рекомендуется увеличить долю контента по этому столпу."
            )
        
        # Анализ воронки
        if report.funnel_stage_performance:
            best_stage = max(
                report.funnel_stage_performance.items(),
                key=lambda x: x[1].get("avg_engagement_rate", 0)
            )[0]
            recommendations.append(
                f"Стадия воронки '{best_stage}' наиболее эффективна. "
                f"Рекомендуется оптимизировать контент для других стадий."
            )
        
        return recommendations

