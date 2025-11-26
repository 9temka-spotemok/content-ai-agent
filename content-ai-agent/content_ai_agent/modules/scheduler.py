"""
Модуль Content Scheduler - планирование публикаций
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from content_ai_agent.modules.content_agent import ContentPiece, ContentStatus

class ScheduleStatus(Enum):
    """Статусы расписания"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

@dataclass
class ScheduledPost:
    """Запланированная публикация"""
    id: str
    content: ContentPiece
    scheduled_time: datetime
    channel: str
    status: ScheduleStatus
    published: bool = False
    published_at: Optional[datetime] = None

class ContentScheduler:
    """
    Планировщик контента
    
    Функции:
    - План публикаций
    - Контроль регулярности
    - Автоматическое планирование
    """
    
    def __init__(self):
        self.schedule: Dict[str, List[ScheduledPost]] = {}  # channel -> posts
        self.posting_times: Dict[str, List[str]] = {}  # channel -> times
    
    def create_schedule(self, 
                       content_pieces: List[ContentPiece],
                       start_date: datetime,
                       channels: List[str],
                       posts_per_week: int = 5) -> Dict[str, List[ScheduledPost]]:
        """
        Создание расписания публикаций
        
        Args:
            content_pieces: список контента для публикации
            start_date: дата начала публикаций
            channels: каналы публикации
            posts_per_week: количество постов в неделю
        """
        from content_ai_agent.config import Config
        
        schedule = {}
        
        for channel in channels:
            schedule[channel] = []
            
            # Получаем оптимальное время публикации для канала
            optimal_times = Config.OPTIMAL_POSTING_TIMES.get(
                channel, ["09:00", "13:00", "17:00"]
            )
            
            # Распределяем контент по датам и времени
            current_date = start_date
            content_index = 0
            
            # Планируем на 4 недели вперед
            for week in range(4):
                # Количество постов в неделю для канала
                posts_this_week = min(
                    posts_per_week,
                    len(content_pieces) - content_index
                )
                
                # Распределяем по рабочим дням (Пн-Пт)
                for day in range(5):
                    if content_index >= len(content_pieces):
                        break
                    
                    if day < posts_this_week:
                        # Выбираем время публикации
                        time_index = day % len(optimal_times)
                        time_str = optimal_times[time_index]
                        hour, minute = map(int, time_str.split(':'))
                        
                        scheduled_time = current_date.replace(
                            hour=hour, minute=minute, second=0, microsecond=0
                        )
                        
                        # Создаем запланированную публикацию
                        scheduled_post = ScheduledPost(
                            id=f"schedule_{channel}_{scheduled_time.strftime('%Y%m%d%H%M')}",
                            content=content_pieces[content_index],
                            scheduled_time=scheduled_time,
                            channel=channel,
                            status=ScheduleStatus.DRAFT
                        )
                        
                        schedule[channel].append(scheduled_post)
                        content_index += 1
                    
                    current_date += timedelta(days=1)
                
                # Переходим к следующей неделе
                current_date += timedelta(days=2)  # Пропускаем выходные
        
        self.schedule = schedule
        return schedule
    
    def add_to_schedule(self, content: ContentPiece, 
                       scheduled_time: datetime,
                       channel: str) -> ScheduledPost:
        """
        Добавление контента в расписание
        
        Args:
            content: контент для публикации
            scheduled_time: время публикации
            channel: канал публикации
        """
        scheduled_post = ScheduledPost(
            id=f"schedule_{channel}_{scheduled_time.strftime('%Y%m%d%H%M')}",
            content=content,
            scheduled_time=scheduled_time,
            channel=channel,
            status=ScheduleStatus.DRAFT
        )
        
        if channel not in self.schedule:
            self.schedule[channel] = []
        
        self.schedule[channel].append(scheduled_post)
        
        # Сортируем по времени
        self.schedule[channel].sort(key=lambda x: x.scheduled_time)
        
        return scheduled_post
    
    def get_upcoming_posts(self, channel: Optional[str] = None,
                          days: int = 7) -> List[ScheduledPost]:
        """
        Получить предстоящие публикации
        
        Args:
            channel: канал (если None - все каналы)
            days: количество дней вперед
        """
        upcoming = []
        cutoff_date = datetime.now() + timedelta(days=days)
        
        channels_to_check = [channel] if channel else self.schedule.keys()
        
        for ch in channels_to_check:
            if ch in self.schedule:
                for post in self.schedule[ch]:
                    if (post.scheduled_time <= cutoff_date and 
                        not post.published and
                        post.status == ScheduleStatus.ACTIVE):
                        upcoming.append(post)
        
        upcoming.sort(key=lambda x: x.scheduled_time)
        return upcoming
    
    def mark_as_published(self, post_id: str) -> bool:
        """
        Отметить публикацию как опубликованную
        
        Args:
            post_id: ID запланированной публикации
        """
        for channel_posts in self.schedule.values():
            for post in channel_posts:
                if post.id == post_id:
                    post.published = True
                    post.published_at = datetime.now()
                    post.content.status = ContentStatus.PUBLISHED
                    return True
        return False
    
    def get_schedule_for_date(self, date: datetime,
                             channel: Optional[str] = None) -> List[ScheduledPost]:
        """
        Получить расписание на конкретную дату
        
        Args:
            date: дата
            channel: канал (если None - все каналы)
        """
        posts = []
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        channels_to_check = [channel] if channel else self.schedule.keys()
        
        for ch in channels_to_check:
            if ch in self.schedule:
                for post in self.schedule[ch]:
                    if date_start <= post.scheduled_time < date_end:
                        posts.append(post)
        
        posts.sort(key=lambda x: x.scheduled_time)
        return posts
    
    def get_schedule_calendar(self, start_date: datetime,
                            weeks: int = 4) -> Dict[str, List[ScheduledPost]]:
        """
        Получить календарь расписания
        
        Args:
            start_date: дата начала
            weeks: количество недель
        """
        calendar = {}
        current_date = start_date
        
        for week in range(weeks):
            for day in range(7):
                date_key = current_date.strftime("%Y-%m-%d")
                calendar[date_key] = self.get_schedule_for_date(current_date)
                current_date += timedelta(days=1)
        
        return calendar
    
    def update_post_status(self, post_id: str, 
                          status: ScheduleStatus) -> bool:
        """
        Обновить статус публикации
        
        Args:
            post_id: ID публикации
            status: новый статус
        """
        for channel_posts in self.schedule.values():
            for post in channel_posts:
                if post.id == post_id:
                    post.status = status
                    return True
        return False
    
    def get_schedule(self) -> Dict[str, List[ScheduledPost]]:
        """Получить полное расписание"""
        return self.schedule

