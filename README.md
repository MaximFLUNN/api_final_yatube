# API для социальной сети Yatube

Yatube API — это сервис для социальной платформы, позволяющий пользователям создавать публикации, оставлять комментарии и подписываться на авторов.

## 📋 Функциональность

- Создание и просмотр публикаций
- Добавление комментариев к публикациям
- Управление тематическими группами
- Система подписок на авторов (`/follow/`)
- Аутентификация с использованием JWT-токенов

## 🛠️ Развертывание проекта

1. Скопируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/yatube-api.git
   cd yatube-api
   ```

2. Настройте виртуальное окружение:
   ```bash
   python -m venv env
   source env/bin/activate  # Для Windows: env\Scripts\activate
   ```

3. Установите необходимые пакеты:
   ```bash
   pip install -r requirements.txt
   ```

4. Примените миграции и запустите сервер:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. Документация API доступна по адресу:
   ```
   http://127.0.0.1:8000/redoc/
   ```

## 🔑 Система аутентификации

В проекте используется JWT-аутентификация:
- `POST /jwt/create/` — получение токена доступа
- `POST /jwt/refresh/` — обновление токена

## 📝 Примеры запросов

### Получение токена доступа
```http
POST /jwt/create/
{
  "username": "ваш_логин",
  "password": "ваш_пароль"
}
```

### Оформление подписки
```http
POST /api/v1/follow/
Authorization: Bearer <ваш_токен>
{
  "following": "имя_автора"
}
```

### Получение списка подписок
```http
GET /api/v1/follow/
Authorization: Bearer <ваш_токен>
