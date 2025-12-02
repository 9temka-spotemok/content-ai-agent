"""
CLI интерфейс для Content AI Agent
"""
import json
from typing import Dict, Any
from datetime import datetime, timedelta
from content_ai_agent.main import ContentAIAgent

def print_header(text: str):
    """Печать заголовка"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_section(text: str):
    """Печать секции"""
    print(f"\n--- {text} ---\n")

def interactive_onboarding(agent: ContentAIAgent):
    """Интерактивный онбординг"""
    print_header("Content AI Agent - Онбординг")
    
    print("Добро пожаловать в Content AI Agent!")
    print("Мы поможем вам создать системный контент-маркетинг для вашего продукта.\n")
    
    # Сбор информации о продукте
    product_info = {}
    
    print("Шаг 1: Информация о продукте")
    product_info["name"] = input("Название продукта: ").strip()
    product_info["description"] = input("Описание продукта: ").strip()
    product_info["category"] = input("Категория продукта: ").strip()
    
    print("\nКлючевые функции (введите через запятую):")
    features_input = input("Функции: ").strip()
    product_info["features"] = [f.strip() for f in features_input.split(",") if f.strip()]
    
    product_info["target_audience"] = input("Целевая аудитория (предварительно): ").strip()
    
    # Запуск онбординга
    result = agent.start_onboarding(product_info)
    print_section("Результат анализа продукта")
    print(f"✓ Продукт проанализирован: {result['product_profile']['name']}")
    print(f"✓ Value Proposition: {result['product_profile']['value_proposition']}")
    
    return result

def interactive_deep_impact(agent: ContentAIAgent):
    """Интерактивный проход по DEEP IMPACT"""
    print_header("DEEP IMPACT - Анализ целевой аудитории")
    
    print("Теперь мы проведем глубокий анализ вашей целевой аудитории")
    print("используя фреймворк DEEP IMPACT.\n")
    
    # Аудит исходных данных
    print_section("Раздел 1: Аудит исходных данных")
    print("Соберите информацию о вашем бизнесе для аудита.")
    
    business_context = {
        "business_niche": input("Бизнес-ниша: ").strip(),
        "stage": input("Стадия развития бизнеса: ").strip(),
        "existing_data": input("Какие данные о аудитории у вас есть: ").strip()
    }
    
    audit_result = agent.run_deep_impact_audit(business_context)
    print("✓ Аудит данных завершен")
    
    # Генерация гипотез
    print_section("Раздел 2: Генерация гипотез")
    
    levels = ["market", "niche", "audience", "segment", "pain", "task"]
    
    for level in levels:
        print(f"\nГенерация гипотез: {level}")
        print("(В реальной версии здесь будет интерактивный диалог с AI)")
        
        # В реальной версии здесь будет вызов LLM для генерации гипотез
        input_data = {"context": business_context}
        result = agent.generate_hypotheses(level, input_data)
        print(f"✓ Гипотезы по {level} сгенерированы")
        
        if result.get("next_level"):
            continue
        else:
            break
    
    # Расширение инсайтов
    print_section("Раздел 3: Расширение понимания аудитории")
    print("Расширяем инсайты о целевой аудитории...")
    
    expansion_result = agent.expand_audience_insights()
    print("✓ Инсайты о аудитории расширены")
    print(f"  Главная боль: {expansion_result['insights'].get('main_pain', 'N/A')}")
    print(f"  Главная задача: {expansion_result['insights'].get('main_task', 'N/A')}")
    
    return expansion_result

def interactive_strategy_generation(agent: ContentAIAgent):
    """Интерактивная генерация стратегии"""
    print_header("Генерация контент-стратегии")
    
    print("Введите бизнес-цели (через запятую):")
    goals_input = input("Цели: ").strip()
    business_goals = [g.strip() for g in goals_input.split(",") if g.strip()]
    
    if not business_goals:
        business_goals = ["Рост видимости продукта", "Привлечение клиентов"]
    
    print("\nГенерируем контент-стратегию...")
    strategy = agent.generate_content_strategy(business_goals)
    
    print_section("Контент-стратегия создана")
    print(f"Контентные столпы ({len(strategy.content_pillars)}):")
    for i, pillar in enumerate(strategy.content_pillars, 1):
        print(f"  {i}. {pillar}")
    
    print(f"\nКаналы публикации: {', '.join(strategy.channels)}")
    print(f"Tone of Voice: {strategy.tone_of_voice}")
    
    return strategy

def interactive_content_generation(agent: ContentAIAgent):
    """Интерактивная генерация контента"""
    print_header("Генерация контента")
    
    count_input = input("Сколько постов сгенерировать? (по умолчанию 10): ").strip()
    count = int(count_input) if count_input.isdigit() else 10
    
    print(f"\nГенерируем {count} постов...")
    content_list = agent.generate_content_batch(count)
    
    print_section("Контент сгенерирован")
    print(f"Создано постов: {len(content_list)}\n")
    
    for i, content in enumerate(content_list[:5], 1):  # Показываем первые 5
        print(f"{i}. {content.title}")
        print(f"   Столп: {content.pillar} | Стадия: {content.funnel_stage}")
        print(f"   Канал: {content.channel} | Статус: {content.status.value}")
        print()
    
    if len(content_list) > 5:
        print(f"... и еще {len(content_list) - 5} постов")
    
    return content_list

def interactive_scheduling(agent: ContentAIAgent, content_list):
    """Интерактивное планирование"""
    print_header("Планирование публикаций")
    
    print("Выберите контент для публикации (ID через запятую):")
    print("Или нажмите Enter для публикации всего сгенерированного контента")
    
    content_ids_input = input("ID контента: ").strip()
    
    if not content_ids_input:
        content_ids = [c.id for c in content_list]
    else:
        content_ids = [id.strip() for id in content_ids_input.split(",")]
    
    print("\nВыберите каналы публикации (linkedin, twitter, telegram):")
    channels_input = input("Каналы (через запятую): ").strip()
    channels = [c.strip() for c in channels_input.split(",")] if channels_input else ["linkedin"]
    
    print("\nДата начала публикаций (YYYY-MM-DD) или Enter для завтра:")
    date_input = input("Дата: ").strip()
    
    if date_input:
        try:
            start_date = datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            print("Неверный формат даты, используем завтра")
            start_date = datetime.now() + timedelta(days=1)
    else:
        start_date = datetime.now() + timedelta(days=1)
    
    print(f"\nСоздаем расписание начиная с {start_date.strftime('%Y-%m-%d')}...")
    schedule = agent.approve_and_schedule_content(
        content_ids=content_ids,
        start_date=start_date,
        channels=channels
    )
    
    print_section("Расписание создано")
    for channel, posts in schedule.items():
        print(f"\n{channel.upper()}: {len(posts)} постов запланировано")
        for post in posts[:3]:
            print(f"  - {post.scheduled_time.strftime('%Y-%m-%d %H:%M')}: {post.content.title}")
        if len(posts) > 3:
            print(f"  ... и еще {len(posts) - 3} постов")
    
    return schedule

def main():
    """Главная функция CLI"""
    print_header("Content AI Agent")
    print("Автономная система контент-маркетинга для стартапов\n")
    
    # Инициализация агента
    agent = ContentAIAgent()
    
    try:
        # Онбординг
        onboarding_result = interactive_onboarding(agent)
        
        # DEEP IMPACT анализ
        deep_impact_result = interactive_deep_impact(agent)
        
        # Генерация стратегии
        strategy = interactive_strategy_generation(agent)
        
        # Генерация контента
        content_list = interactive_content_generation(agent)
        
        # Планирование
        schedule = interactive_scheduling(agent, content_list)
        
        # Итоговое состояние
        print_header("Готово!")
        state = agent.get_current_state()
        print(f"Текущая стадия: {state['stage']}")
        print(f"Контент создан: {state['content_count']} постов")
        print(f"Запланировано публикаций: {state['scheduled_posts']}")
        
        print("\n✓ Content AI Agent настроен и готов к работе!")
        print("\nСледующие шаги:")
        print("1. Просмотрите сгенерированный контент")
        print("2. При необходимости отредактируйте")
        print("3. Запустите публикации по расписанию")
        print("4. Отслеживайте метрики в аналитике")
        
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\n\nОшибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

