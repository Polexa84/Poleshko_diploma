### Инструкция по развертыванию и запуску проекта

## Предварительные требования

- Python 3.10+
- PostgreSQL 13+
- Redis (для кеширования)
- Nginx
- Git
- rsync (для деплоя)

## Установка и настройка (разработка и production)

### 1. Клонирование проекта

```bash
git clone <URL_вашего_репозитория>
cd <имя_папки_проекта>
```

### 2. Настройка окружения

1. Переименуйте файл `.env.example` в `.env`:
```bash
mv .env.example .env
```

2. Отредактируйте `.env` (настройки для разработки и production):
```ini

### 3. Установка зависимостей

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### 4. Настройка базы данных

1. Создайте базу данных:
```bash
sudo -u postgres psql -c "CREATE DATABASE testdb;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';"
```

2. Примените миграции:
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Запуск в режиме разработки

```bash
python manage.py runserver
```

Откройте http://localhost:8000 в браузере.

## Production развертывание

### 1. Настройка сервера (Ubuntu)

```bash
sudo apt update
sudo apt install -y python3 python3-venv postgresql redis-server nginx gunicorn
```

### 2. Настройка Gunicorn

1. Создайте файл сервиса `/etc/systemd/system/gunicorn.service`:
```ini
[Unit]
Description=Gunicorn для Django
After=network.target

[Service]
User=deployer
Group=www-data
WorkingDirectory=/home/deployer/ваш_проект
Environment="PATH=/home/deployer/ваш_проект/venv/bin"
ExecStart=/home/deployer/ваш_проект/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    ваш_проект.wsgi:application

[Install]
WantedBy=multi-user.target
```

2. Запустите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### 3. Настройка Nginx

1. Создайте конфиг `/etc/nginx/sites-available/ваш_проект`:
```nginx
server {
    listen 80;
    server_name ваш_домен;

    location /static/ {
        root /home/deployer/ваш_проект;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

2. Активируйте конфиг:
```bash
sudo ln -s /etc/nginx/sites-available/ваш_проект /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## CI/CD с GitHub Actions

Пример `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: webfactory/ssh-agent@v0.8.0
        with:
          ssh-private-key: ${{ secrets.SSH_KEY }}
      
      - name: Deploy to server
        run: |
          rsync -avz --delete \
            --exclude '__pycache__' \
            --exclude '.env' \
            . deployer@${{ secrets.SERVER_IP }}:${{ secrets.DEPLOY_DIR }}
          
          ssh deployer@${{ secrets.SERVER_IP }} << 'EOF'
            cd $DEPLOY_DIR
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate
            python manage.py collectstatic --noinput
            sudo systemctl restart gunicorn
          EOF
```

## Управление проектом

- Перезапуск Gunicorn: `sudo systemctl restart gunicorn`
- Просмотр логов: `sudo journalctl -u gunicorn -f`
- Обновление статики: `python manage.py collectstatic`

## Решение проблем

1. Ошибки миграций:
```bash
python manage.py migrate --fake-initial
```

2. Проблемы с правами:
```bash
sudo chown -R deployer:www-data /home/deployer/ваш_проект
sudo chmod -R 755 /home/deployer/ваш_проект
```

3. Проверка работы Gunicorn:
```bash
curl --unix-socket /run/gunicorn.sock http
```
```

Этот README содержит:
1. Полные инструкции для локальной разработки
2. Настройку production-окружения
3. Конфигурацию CI/CD
4. Управление проектом
5. Решение частых проблем

Особое внимание обратите на:
- Правильное переименование `.env.example` → `.env`
- Настройку переменных окружения
- Конфигурацию Gunicorn и Nginx
- Права доступа к файлам
