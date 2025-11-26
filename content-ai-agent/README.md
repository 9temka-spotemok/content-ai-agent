# Content AI Agent

Автономная система контент-маркетинга для стартапов и владельцев бизнесов.

## Описание

Content AI Agent помогает стартапам выстраивать системный контент-маркетинг, который объясняет ценность продукта и приводит клиентов без перегрузки команды.

### Основные возможности

1. **Product Intelligence** - анализ продукта и создание профиля
2. **Content Strategy Generator** - генерация контент-стратегии на основе фреймворка DEEP IMPACT
3. **AI Content Agent** - генерация контента с адаптацией под стиль и каналы
4. **Content Scheduler** - планирование публикаций
5. **Simple Analytics** - базовая аналитика и отчеты

## Архитектура

Система построена на основе:

- **Фреймворк DEEP IMPACT** - для глубокого анализа целевой аудитории
- **База знаний "Продающие Смыслы"** - для создания эффективного контента
- **Модульная архитектура** - каждый компонент работает независимо

## Установка

```bash
# Перейдите в папку проекта
cd content-ai-agent

# Установите зависимости
pip install -r requirements.txt

# Настройте переменные окружения (опционально)
# Создайте .env файл и добавьте OPENAI_API_KEY (если используете LLM)
```

## Использование

### Веб-интерфейс (Streamlit)

```bash
cd content-ai-agent
streamlit run streamlit_app.py
```

Или для локальной разработки:
```bash
streamlit run content_ai_agent/web_app.py
```

### CLI интерфейс

```bash
cd content-ai-agent
python -m content_ai_agent.cli
```

### Программный интерфейс

```python
from content_ai_agent.main import ContentAIAgent

# Инициализация
agent = ContentAIAgent()

# Онбординг
product_info = {
    "name": "Мой продукт",
    "description": "Описание продукта",
    "category": "SaaS",
    "features": ["функция 1", "функция 2"],
    "target_audience": "AI стартапы"
}

result = agent.start_onboarding(product_info)
```

## Развертывание

### Streamlit Cloud (Рекомендуется)

1. Загрузите папку `content-ai-agent` на GitHub
2. Перейдите на https://share.streamlit.io
3. Подключите репозиторий
4. Укажите путь: `streamlit_app.py`
5. Deploy!

Подробная инструкция: см. `START_HERE.md`

## Структура проекта

```
content-ai-agent/
├── content_ai_agent/          # Основной код приложения
│   ├── __init__.py
│   ├── main.py               # Главный оркестратор
│   ├── web_app.py            # Streamlit веб-интерфейс
│   ├── cli.py                # CLI интерфейс
│   ├── config.py             # Конфигурация
│   ├── frameworks/           # Фреймворки
│   │   └── deep_impact.py   # DEEP IMPACT фреймворк
│   └── modules/               # Модули системы
│       ├── product_intelligence.py
│       ├── content_strategy.py
│       ├── content_agent.py
│       ├── scheduler.py
│       └── analytics.py
├── streamlit_app.py          # Точка входа для Streamlit Cloud
├── requirements.txt           # Зависимости
├── Procfile                  # Для Railway/Render
├── runtime.txt               # Версия Python
├── setup.sh                  # Скрипт настройки
├── .gitignore                # Git ignore файл
├── README.md                 # Этот файл
└── START_HERE.md             # Краткая инструкция
```

## Фреймворк DEEP IMPACT

Система использует фреймворк DEEP IMPACT для анализа целевой аудитории:

- **D** - Desires and Dreams (Желания и Мечты)
- **E** - Emotions and Experiences (Эмоции и Опыт)
- **E** - Expectations and Evaluations (Ожидания и Оценки)
- **P** - Pain Points and Problems (Болевые точки и Проблемы)

- **I** - Insights and Intentions (Инсайты и Намерения)
- **M** - Motivations and Mindsets (Мотивации и Образ мышления)
- **P** - Perceptions and Preferences (Восприятие и Предпочтения)
- **A** - Aspirations and Actions (Стремления и Действия)
- **C** - Concerns and Challenges (Опасения и Вызовы)
- **T** - Triggers and Transformations (Триггеры и Трансформации)

## Лицензия

MIT

## Авторы

Разработано на основе концепции из Test1.pdf и фреймворков DEEP IMPACT и "Продающие Смыслы".
