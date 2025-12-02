"""
Главный файл для Streamlit Cloud
Streamlit Cloud требует файл streamlit_app.py в корне репозитория
"""
import sys
import os

# Получаем абсолютный путь к корню репозитория
current_dir = os.path.dirname(os.path.abspath(__file__))

# Добавляем пути к sys.path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

content_ai_path = os.path.join(current_dir, 'content_ai_agent')
if content_ai_path not in sys.path:
    sys.path.insert(0, content_ai_path)

# Импортируем streamlit
import streamlit as st

# Пытаемся импортировать стандартным способом
main = None
try:
    from content_ai_agent.web_app import main
    # Если main успешно импортирована, импортируем остальное
    from content_ai_agent.web_app import *
except ImportError as e:
    # Логируем ошибку для отладки (только в режиме разработки)
    import traceback
    # В Streamlit Cloud не выводим traceback в UI, чтобы не пугать пользователей
    # Если стандартный импорт не работает, загружаем модули вручную
    import importlib.util
    import types
    
    # Создаем структуру модулей
    def create_module(name, path=None):
        """Создает модуль в sys.modules"""
        if name not in sys.modules:
            module = types.ModuleType(name)
            if path:
                module.__path__ = [path]
            sys.modules[name] = module
        return sys.modules[name]
    
    # Создаем базовые модули
    create_module('content_ai_agent', os.path.join(current_dir, 'content_ai_agent'))
    create_module('content_ai_agent.modules', os.path.join(current_dir, 'content_ai_agent', 'modules'))
    create_module('content_ai_agent.frameworks', os.path.join(current_dir, 'content_ai_agent', 'frameworks'))
    
    # Загружаем модули в правильном порядке
    modules_order = [
        ('content_ai_agent.__init__', 'content_ai_agent/__init__.py'),
        ('content_ai_agent.config', 'content_ai_agent/config.py'),
        ('content_ai_agent.frameworks.__init__', 'content_ai_agent/frameworks/__init__.py'),
        ('content_ai_agent.frameworks.deep_impact', 'content_ai_agent/frameworks/deep_impact.py'),
        ('content_ai_agent.modules.__init__', 'content_ai_agent/modules/__init__.py'),
        ('content_ai_agent.modules.product_intelligence', 'content_ai_agent/modules/product_intelligence.py'),
        ('content_ai_agent.modules.content_strategy', 'content_ai_agent/modules/content_strategy.py'),
        ('content_ai_agent.modules.content_agent', 'content_ai_agent/modules/content_agent.py'),
        ('content_ai_agent.modules.scheduler', 'content_ai_agent/modules/scheduler.py'),
        ('content_ai_agent.modules.analytics', 'content_ai_agent/modules/analytics.py'),
        ('content_ai_agent.main', 'content_ai_agent/main.py'),
    ]
    
    # Загружаем все модули
    for module_name, file_path in modules_order:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            try:
                spec = importlib.util.spec_from_file_location(module_name, full_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    # Устанавливаем package для правильных относительных импортов
                    parts = module_name.split('.')
                    if len(parts) > 1:
                        module.__package__ = '.'.join(parts[:-1])
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
            except Exception as e:
                # Продолжаем загрузку других модулей
                # В production не логируем каждую ошибку импорта
                pass
    
    # Теперь загружаем web_app
    web_app_path = os.path.join(current_dir, 'content_ai_agent', 'web_app.py')
    
    if os.path.exists(web_app_path):
        spec = importlib.util.spec_from_file_location("content_ai_agent.web_app", web_app_path)
        if spec and spec.loader:
            web_app = importlib.util.module_from_spec(spec)
            web_app.__package__ = 'content_ai_agent'
            sys.modules['content_ai_agent.web_app'] = web_app
            
            # Выполняем модуль
            spec.loader.exec_module(web_app)
            
            # Копируем все публичные атрибуты в глобальное пространство
            for attr_name in dir(web_app):
                if not attr_name.startswith('_'):
                    globals()[attr_name] = getattr(web_app, attr_name)
            
            # Убеждаемся, что main доступна
            if hasattr(web_app, 'main'):
                main = web_app.main
    else:
        st.error(f"❌ Файл web_app.py не найден!")
        st.error(f"Ищем в: {web_app_path}")
        st.error(f"Текущая директория: {current_dir}")
        if os.path.exists(current_dir):
            st.error(f"Файлы: {', '.join(os.listdir(current_dir)[:10])}")
        st.stop()

# Запускаем приложение
# В Streamlit Cloud код выполняется напрямую, поэтому вызываем main() всегда
if main is None:
    st.error("❌ Функция main() не найдена в web_app.py")
    st.error("Проверьте, что web_app.py содержит функцию main()")
    st.stop()
else:
    main()

