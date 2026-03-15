# SMS Gate

SMS-шлюз для отправки и приёма SMS через Android-телефон, подключённый к macOS по USB.

## Архитектура

```
Клиент → [FastAPI :8095] → [ADB USB forward :8081] → [Android SMS Gateway app] → SMS
                         ← webhook входящих SMS ←
```

- **macOS**: FastAPI сервер (REST API), ADB port forwarding
- **Android**: приложение SMS Gateway (capcom6/android-sms-gateway), подключение по USB
- Интернет приходит НЕ через телефон — телефон только для SMS

## Стек

- Python 3.12+, FastAPI, httpx, pydantic-settings
- ADB (Android SDK Platform Tools) для USB-подключения
- Android SMS Gateway app на телефоне

## Команды

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # настроить credentials

# Run
python main.py

# ADB (если не установлен)
brew install android-platform-tools
```

## API эндпоинты

| Method | Path | Auth | Описание |
|--------|------|------|----------|
| GET | /health | — | Статус подключения |
| GET | /device | API key | Инфо об Android-устройстве |
| POST | /device/reconnect | API key | Переподключить ADB |
| POST | /sms/send | API key | Отправить SMS |
| GET | /sms/{id} | API key | Статус сообщения |
| GET | /sms/inbox | API key | Входящие SMS |
| POST | /webhook/incoming | — | Webhook от Android app |
| POST | /webhooks/register | API key | Зарегистрировать webhook |
| GET | /webhooks | API key | Список webhooks |
| DELETE | /webhooks/{id} | API key | Удалить webhook |
