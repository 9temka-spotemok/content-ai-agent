"""
Streamlit веб-интерфейс для Content AI Agent
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

from content_ai_agent.main import ContentAIAgent
from content_ai_agent.modules.content_agent import ContentStatus, ContentFormat

# Настройка страницы
st.set_page_config(
    page_title="Content AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация сессии
if 'agent' not in st.session_state:
    st.session_state.agent = ContentAIAgent()
    st.session_state.current_stage = "onboarding"
    st.session_state.product_info = {}
    st.session_state.audience_insights = {}
    st.session_state.strategy = None
    st.session_state.content_list = []
    st.session_state.schedule = {}

def render_header():
    """Отображение заголовка"""
    st.title("🤖 Content AI Agent")
    st.markdown("**Автономная система контент-маркетинга для стартапов**")
    st.markdown("---")

def render_sidebar():
    """Боковая панель с навигацией"""
    st.sidebar.title("📋 Навигация")
    
    stages = {
        "onboarding": "1️⃣ Онбординг",
        "deep_impact": "2️⃣ DEEP IMPACT",
        "strategy": "3️⃣ Стратегия",
        "content": "4️⃣ Контент",
        "scheduling": "5️⃣ Планирование",
        "analytics": "6️⃣ Аналитика"
    }
    
    current = st.session_state.current_stage
    
    # Интерактивная навигация
    for stage_key, stage_name in stages.items():
        if stage_key == current:
            st.sidebar.markdown(f"**{stage_name}** ✅")
        else:
            # Создаем кнопку для перехода к другому этапу
            if st.sidebar.button(stage_name, key=f"nav_{stage_key}", use_container_width=True):
                st.session_state.current_stage = stage_key
                st.rerun()
    
    st.sidebar.markdown("---")
    
    # Текущее состояние
    if st.session_state.agent.product_profile:
        st.sidebar.markdown("### 📊 Статус")
        state = st.session_state.agent.get_current_state()
        st.sidebar.metric("Контент", state['content_count'])
        st.sidebar.metric("Запланировано", state['scheduled_posts'])

def render_onboarding():
    """Экран онбординга"""
    # Кнопка "Назад" - на первой странице не нужна
    st.header("1️⃣ Онбординг - Описание продукта")
    st.markdown("Начнем с анализа вашего продукта")
    
    with st.form("product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input(
                "Название продукта *",
                value=st.session_state.product_info.get("name", ""),
                help="Название вашего продукта или сервиса"
            )
            
            product_category = st.selectbox(
                "Категория *",
                ["SaaS", "E-commerce", "Образование", "Здоровье", "Финансы", "Другое"],
                index=0 if st.session_state.product_info.get("category") != "Другое" else 5
            )
        
        with col2:
            product_description = st.text_area(
                "Описание продукта *",
                value=st.session_state.product_info.get("description", ""),
                height=100,
                help="Краткое описание того, что делает ваш продукт"
            )
        
        features_input = st.text_input(
            "Ключевые функции (через запятую) *",
            value=", ".join(st.session_state.product_info.get("features", [])),
            help="Основные функции и возможности продукта"
        )
        
        target_audience = st.text_input(
            "Целевая аудитория (предварительно)",
            value=st.session_state.product_info.get("target_audience", ""),
            help="Кто ваши потенциальные клиенты?"
        )
        
        submitted = st.form_submit_button("🚀 Начать анализ", use_container_width=True)
        
        if submitted:
            if not all([product_name, product_description, features_input]):
                st.error("Пожалуйста, заполните все обязательные поля")
            else:
                with st.spinner("Анализируем продукт..."):
                    product_info = {
                        "name": product_name,
                        "description": product_description,
                        "category": product_category,
                        "features": [f.strip() for f in features_input.split(",") if f.strip()],
                        "target_audience": target_audience
                    }
                    
                    st.session_state.product_info = product_info
                    result = st.session_state.agent.start_onboarding(product_info)
                    
                    st.session_state.current_stage = "deep_impact"
                    st.success("✅ Продукт проанализирован!")
                    st.rerun()

def render_deep_impact():
    """Экран DEEP IMPACT анализа"""
    # Кнопка "Назад"
    col_back, col_title = st.columns([1, 10])
    with col_back:
        if st.button("← Назад", key="back_deep_impact"):
            st.session_state.current_stage = "onboarding"
            st.rerun()
    with col_title:
        st.header("2️⃣ DEEP IMPACT - Анализ целевой аудитории")
    st.markdown("Проведем глубокий анализ вашей целевой аудитории")
    
    tab1, tab2, tab3 = st.tabs(["Аудит данных", "Генерация гипотез", "Расширение инсайтов"])
    
    with tab1:
        st.subheader("Аудит исходных данных")
        
        with st.form("audit_form"):
            business_niche = st.text_input("Бизнес-ниша")
            business_stage = st.selectbox(
                "Стадия развития",
                ["Идея", "MVP", "Первые клиенты", "Рост", "Масштабирование"]
            )
            existing_data = st.text_area(
                "Какие данные о аудитории у вас есть?",
                height=100
            )
            
            if st.form_submit_button("Провести аудит"):
                with st.spinner("Проводим аудит..."):
                    business_context = {
                        "business_niche": business_niche,
                        "stage": business_stage,
                        "existing_data": existing_data
                    }
                    
                    result = st.session_state.agent.run_deep_impact_audit(business_context)
                    st.success("✅ Аудит завершен!")
                    st.json(result)
    
    with tab2:
        st.subheader("Генерация гипотез")
        st.info("В полной версии здесь будет интерактивный процесс генерации гипотез по уровням: Рынок → Ниша → Аудитория → Сегмент → Боль → Задача")
        
        if st.button("🚀 Запустить генерацию гипотез (демо)"):
            with st.spinner("Генерируем гипотезы..."):
                # Демо-версия - в реальной версии здесь будет полный процесс
                st.success("✅ Гипотезы сгенерированы!")
                st.info("В полной версии здесь будут отображены результаты генерации гипотез")
    
    with tab3:
        st.subheader("Расширение инсайтов о аудитории")
        
        if st.button("🔍 Расширить инсайты"):
            with st.spinner("Расширяем понимание аудитории..."):
                result = st.session_state.agent.expand_audience_insights()
                st.session_state.audience_insights = result['insights']
                st.success("✅ Инсайты расширены!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Главная боль", result['insights'].get('main_pain', 'N/A'))
                    st.metric("Главная задача", result['insights'].get('main_task', 'N/A'))
                
                with col2:
                    if result['insights'].get('motivations'):
                        st.write("**Мотивации:**")
                        for mot in list(result['insights']['motivations'].values())[:3]:
                            st.write(f"- {mot}")
                
                st.session_state.current_stage = "strategy"
                st.rerun()

def render_strategy():
    """Экран генерации стратегии"""
    # Кнопка "Назад"
    col_back, col_title = st.columns([1, 10])
    with col_back:
        if st.button("← Назад", key="back_strategy"):
            st.session_state.current_stage = "deep_impact"
            st.rerun()
    with col_title:
        st.header("3️⃣ Генерация контент-стратегии")
    
    if not st.session_state.audience_insights:
        st.warning("⚠️ Сначала завершите анализ DEEP IMPACT")
        if st.button("Вернуться к DEEP IMPACT"):
            st.session_state.current_stage = "deep_impact"
            st.rerun()
        return
    
    with st.form("strategy_form"):
        business_goals = st.text_input(
            "Бизнес-цели (через запятую)",
            value="Рост видимости, Привлечение клиентов",
            help="Какие цели вы хотите достичь с помощью контента?"
        )
        
        if st.form_submit_button("🎯 Создать стратегию", use_container_width=True):
            with st.spinner("Генерируем контент-стратегию..."):
                goals_list = [g.strip() for g in business_goals.split(",") if g.strip()]
                
                strategy = st.session_state.agent.generate_content_strategy(goals_list)
                st.session_state.strategy = strategy
                
                st.success("✅ Контент-стратегия создана!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📌 Контентные столпы")
                    for i, pillar in enumerate(strategy.content_pillars, 1):
                        st.write(f"{i}. {pillar}")
                
                with col2:
                    st.subheader("📱 Каналы")
                    for channel in strategy.channels:
                        st.write(f"- {channel.title()}")
                    
                    st.subheader("🎨 Tone of Voice")
                    st.write(strategy.tone_of_voice)
                
                st.session_state.current_stage = "content"
                st.rerun()

def render_content():
    """Экран генерации контента"""
    # Кнопка "Назад"
    col_back, col_title = st.columns([1, 10])
    with col_back:
        if st.button("← Назад", key="back_content"):
            st.session_state.current_stage = "strategy"
            st.rerun()
    with col_title:
        st.header("4️⃣ Генерация контента")
    
    if not st.session_state.strategy:
        st.warning("⚠️ Сначала создайте контент-стратегию")
        if st.button("Вернуться к стратегии"):
            st.session_state.current_stage = "strategy"
            st.rerun()
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        count = st.number_input("Количество постов", min_value=1, max_value=50, value=10)
        
        if st.button("✨ Сгенерировать контент", use_container_width=True):
            with st.spinner(f"Генерируем {count} постов..."):
                content_list = st.session_state.agent.generate_content_batch(count)
                st.session_state.content_list = content_list
                st.success(f"✅ Создано {len(content_list)} постов!")
                st.rerun()
    
    with col1:
        if st.session_state.content_list:
            st.subheader(f"Сгенерированный контент ({len(st.session_state.content_list)} постов)")
            
            for i, content in enumerate(st.session_state.content_list):
                # Используем индекс для гарантированно уникального ключа
                # Индекс начинается с 0, поэтому используем i+1 для отображения, но i для ключей
                content_id = getattr(content, 'id', None)
                unique_suffix = f"{i}_{content_id}" if content_id else str(i)
                
                with st.expander(f"📝 {content.title} ({content.channel})", key=f"expander_content_{unique_suffix}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.caption(f"Столп: {content.pillar}")
                        st.caption(f"Стадия воронки: {content.funnel_stage}")
                    with col_b:
                        st.caption(f"Канал: {content.channel}")
                        st.caption(f"Статус: {content.status.value}")
                    
                    st.text_area(
                        "Содержание",
                        value=content.content,
                        height=200,
                        key=f"text_area_content_{unique_suffix}",
                        label_visibility="collapsed",
                        disabled=True  # Делаем только для чтения, чтобы избежать проблем с состоянием
                    )
            
            if st.button("📅 Перейти к планированию", use_container_width=True):
                st.session_state.current_stage = "scheduling"
                st.rerun()

def render_scheduling():
    """Экран планирования"""
    # Кнопка "Назад"
    col_back, col_title = st.columns([1, 10])
    with col_back:
        if st.button("← Назад", key="back_scheduling"):
            st.session_state.current_stage = "content"
            st.rerun()
    with col_title:
        st.header("5️⃣ Планирование публикаций")
    
    if not st.session_state.content_list:
        st.warning("⚠️ Сначала сгенерируйте контент")
        if st.button("Вернуться к генерации"):
            st.session_state.current_stage = "content"
            st.rerun()
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Настройки расписания")
        
        channels = st.multiselect(
            "Каналы публикации",
            ["linkedin", "twitter", "telegram"],
            default=["linkedin"]
        )
        
        start_date = st.date_input(
            "Дата начала публикаций",
            value=datetime.now().date() + timedelta(days=1)
        )
        
        posts_per_week = st.slider("Постов в неделю", 1, 10, 5)
    
    with col2:
        st.subheader("Выбор контента")
        st.info(f"Доступно постов: {len(st.session_state.content_list)}")
        
        selected_ids = st.multiselect(
            "Выберите контент для публикации",
            options=[c.id for c in st.session_state.content_list],
            default=[c.id for c in st.session_state.content_list],
            format_func=lambda x: next(
                (c.title for c in st.session_state.content_list if c.id == x), x
            )
        )
    
    if st.button("📅 Создать расписание", use_container_width=True):
        if not channels:
            st.error("Выберите хотя бы один канал")
        elif not selected_ids:
            st.error("Выберите контент для публикации")
        else:
            with st.spinner("Создаем расписание..."):
                schedule = st.session_state.agent.approve_and_schedule_content(
                    content_ids=selected_ids,
                    start_date=datetime.combine(start_date, datetime.min.time()),
                    channels=channels
                )
                
                st.session_state.schedule = schedule
                st.success("✅ Расписание создано!")
                
                st.subheader("📅 Календарь публикаций")
                
                for channel, posts in schedule.items():
                    with st.expander(f"{channel.upper()} - {len(posts)} постов"):
                        for post in posts[:10]:  # Показываем первые 10
                            st.write(f"**{post.scheduled_time.strftime('%Y-%m-%d %H:%M')}** - {post.content.title}")
                        if len(posts) > 10:
                            st.caption(f"... и еще {len(posts) - 10} постов")
                
                st.session_state.current_stage = "analytics"
                st.rerun()

def render_analytics():
    """Экран аналитики"""
    # Кнопка "Назад"
    col_back, col_title = st.columns([1, 10])
    with col_back:
        if st.button("← Назад", key="back_analytics"):
            st.session_state.current_stage = "scheduling"
            st.rerun()
    with col_title:
        st.header("6️⃣ Аналитика")
    
    days = st.slider("Период анализа (дней)", 7, 90, 30)
    
    if st.button("📊 Сгенерировать отчет"):
        with st.spinner("Анализируем данные..."):
            report = st.session_state.agent.get_analytics_report(days=days)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Всего постов", report.total_posts)
            with col2:
                st.metric("Просмотры", report.total_views)
            with col3:
                st.metric("Вовлеченность", report.total_engagement)
            with col4:
                st.metric("Engagement Rate", f"{report.avg_engagement_rate:.2f}%")
            
            st.subheader("🏆 Топ контент")
            for item in report.top_performing_content:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**{item['title']}**")
                with col_b:
                    st.metric("Engagement", item['engagement'])
            
            if report.channel_performance:
                st.subheader("📱 Производительность по каналам")
                channel_data = []
                for channel, perf in report.channel_performance.items():
                    channel_data.append({
                        "Канал": channel,
                        "Посты": perf.get("posts", 0),
                        "Просмотры": perf.get("views", 0),
                        "Engagement Rate": f"{perf.get('avg_engagement_rate', 0):.2f}%"
                    })
                st.dataframe(channel_data)
            
            # Рекомендации
            recommendations = st.session_state.agent.analytics.get_recommendations(report)
            if recommendations:
                st.subheader("💡 Рекомендации")
                for rec in recommendations:
                    st.info(rec)

def main():
    """Главная функция"""
    render_header()
    render_sidebar()
    
    # Роутинг по стадиям
    stage = st.session_state.current_stage
    
    if stage == "onboarding":
        render_onboarding()
    elif stage == "deep_impact":
        render_deep_impact()
    elif stage == "strategy":
        render_strategy()
    elif stage == "content":
        render_content()
    elif stage == "scheduling":
        render_scheduling()
    elif stage == "analytics":
        render_analytics()
    else:
        render_onboarding()

if __name__ == "__main__":
    main()

