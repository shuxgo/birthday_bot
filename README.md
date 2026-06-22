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
- Объединение нескольких именинников в один пост на дату.

## Быстрый локальный запуск

1. Скопируйте переменные окружения:

```bash
cp .env.example .env
```

2. Заполните минимум:

```env
BOT_TOKEN=...
INITIAL_ADMIN_IDS=123456789
OPENAI_API_KEY=...
CHANNEL_ID=@your_channel
```

3. Запустите:

```bash
docker compose up -d --build
```

4. Посмотрите логи:

```bash
docker compose logs -f bot
```

## Как назначить первого администратора

Укажите Telegram ID первого администратора в `.env`:

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

Или в Telegram-боте откройте `Настройки канала` и отправьте новый ID/username канала.

## Как менять промты

Администратор открывает:

- `Промт для фото`
- `Промт для текста`

Затем отправляет:

```text
изменить фото промт
```

или:

```text
изменить промт
```

Каждое изменение сохраняется новой версией в таблице `prompt_templates`.

## Деплой на Google Cloud VM

### 1. Создать VM

Рекомендуемый минимум для MVP:

- Ubuntu 24.04 LTS
- 1-2 vCPU
- 1-2 GB RAM
- 20 GB disk

Откройте исходящий доступ в интернет. Входящие порты для long polling не нужны, достаточно SSH.

### 2. Установить Docker

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

Перезайдите по SSH.

### 3. Разместить проект

```bash
sudo mkdir -p /opt/birthday_bot
sudo chown $USER:$USER /opt/birthday_bot
git clone https://github.com/YOUR_ORG/YOUR_REPO.git /opt/birthday_bot
cd /opt/birthday_bot
cp .env.example .env
nano .env
docker compose up -d --build
```

### 4. Настроить GitHub Actions

В GitHub repository secrets добавьте:

- `GCP_VM_HOST`
- `GCP_VM_USER`
- `GCP_VM_SSH_KEY`

Workflow `.github/workflows/deploy.yml` после push в `main` запускает тесты, подключается к VM, делает `git pull`, пересобирает и перезапускает контейнеры.

## Защита от дублей публикаций

Планировщик каждую минуту выбирает due-посты со статусом `approved` или `scheduled`. В PostgreSQL используется `FOR UPDATE SKIP LOCKED`, а после успешной публикации заполняется `published_at` и статус меняется на `published`.

## Статусы поста

- `draft` — начат черновик.
- `preview` — сформирован предпросмотр.
- `approved` — подтвержден.
- `scheduled` — стоит в очереди публикации.
- `published` — опубликован.
- `cancelled` — отменен.
- `failed` — публикация не удалась.

## Важное ограничение MVP

Сервис генерации изображений сейчас оформлен как отдельный слой, но в MVP он переиспользует Telegram `file_id` вместо реального image-edit API. Это сделано намеренно: интерфейс уже готов, и провайдера можно подключить в `app/services/image_generation.py`, не меняя сценарии бота.

