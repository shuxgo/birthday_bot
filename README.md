# Birthday Bot

Telegram-бот для подготовки, утверждения и отложенной публикации корпоративных поздравлений с днем рождения.

## Что входит

- Python 3.12 + aiogram 3.
- PostgreSQL для данных.
- Redis для FSM-состояний.
- APScheduler для публикаций и ежедневного дайджеста.
- Docker Compose для Google Cloud VM.
- GitHub Actions для тестов и деплоя на VM.
- Роли: `admin`, `moderator`.
- Версионируемые промты для текста и фото.
- Генерация текста через Google AI Studio / Gemini API.
- Объединение нескольких именинников в один пост на дату.

## Быстрый запуск

Создайте `.env`:

```bash
cp .env.example .env
```

Минимально заполните:

```env
BOT_TOKEN=...
INITIAL_ADMIN_IDS=123456789
CHANNEL_ID=@your_channel

AI_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_TEXT_MODEL=gemini-3.1-flash-lite
```

Запустите:

```bash
docker compose up -d --build
docker compose logs -f bot
```

## Google AI Studio / Gemini

1. Откройте https://aistudio.google.com/app/apikey
2. Создайте API key.
3. Вставьте его в `.env`:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=ваш_ключ
GEMINI_TEXT_MODEL=gemini-3.1-flash-lite
```

Gemini API имеет бесплатный tier, но лимиты и условия зависят от Google. Для production можно перейти на paid tier.

## OpenAI как запасной вариант

Если нужно вернуться на OpenAI:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=ваш_openai_key
OPENAI_TEXT_MODEL=gpt-4.1-mini
```

## Как назначить первого администратора

Укажите Telegram ID первого администратора:

```env
INITIAL_ADMIN_IDS=123456789
```

При первом `/start` этот пользователь будет создан как `admin`.

## Как добавить бота в канал

1. Откройте настройки канала.
2. Добавьте бота в администраторы.
3. Дайте право публиковать сообщения.
4. В `.env` укажите:

```env
CHANNEL_ID=@your_channel
```

Или настройте канал через кнопку `📣 Настройки канала` в боте.

## Деплой на Google Cloud VM

На VM:

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

После повторного входа по SSH:

```bash
sudo mkdir -p /opt/birthday_bot
sudo chown $USER:$USER /opt/birthday_bot
git clone https://github.com/YOUR_ORG/YOUR_REPO.git /opt/birthday_bot
cd /opt/birthday_bot
nano .env
docker compose up -d --build
```

## Обновление на VM

```bash
cd /opt/birthday_bot
git pull
docker compose up -d --build
docker compose logs -f bot
```

## Важное ограничение MVP

Сервис генерации изображений сейчас оформлен отдельным слоем, но в MVP он переиспользует Telegram `file_id` вместо реального image-edit API. Провайдера можно подключить в `app/services/image_generation.py`, не меняя сценарии бота.
