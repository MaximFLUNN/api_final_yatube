import sys
import os


# Определяем корневую директорию проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Устанавливаем базовую директорию
PROJECT_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_contents = os.listdir(PROJECT_BASE_DIR)
YATUBE_DIR_NAME = 'yatube_api'

# Проверяем наличие директории проекта
if (
        YATUBE_DIR_NAME not in root_contents
        or not os.path.isdir(os.path.join(PROJECT_BASE_DIR, YATUBE_DIR_NAME))
):
    raise AssertionError(
        f'Директория проекта `{YATUBE_DIR_NAME}` не найдена в `{PROJECT_BASE_DIR}`. '
        'Пожалуйста, проверьте структуру вашего проекта.'
    )

# Путь к директории с файлом manage.py
MANAGE_DIR = os.path.join(PROJECT_BASE_DIR, YATUBE_DIR_NAME)
manage_dir_contents = os.listdir(MANAGE_DIR)
MANAGE_FILENAME = 'manage.py'

# Проверяем наличие файла manage.py
if MANAGE_FILENAME not in manage_dir_contents:
    raise AssertionError(
        f'Файл `{MANAGE_FILENAME}` не обнаружен в директории `{MANAGE_DIR}`. '
        'Пожалуйста, проверьте структуру вашего проекта.'
    )

# Регистрируем плагины для pytest
pytest_plugins = [
    'tests.fixtures.fixture_user',
    'tests.fixtures.fixture_data',
]
