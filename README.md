# 🛎️ Notification Service (Django + DRF + OneSignal)

This is a standalone notification microservice built with Django REST Framework. It supports push notifications via OneSignal and uses PostgreSQL for storage.

---

## 📦 Features

- 📬 Send user-specific and broadcast push notifications
- 🔄 Register OneSignal player IDs per user
- 🧪 Full unit and integration tests with pytest
- 🐘 PostgreSQL support
- 🌐 Swagger/OpenAPI docs

---

## 🧱 Project Setup

### 1. 📁 Clone and Enter Project

```bash
git clone https://github.com/opencrafts-io/notifications
cd notifications
```

---

### 2. 🐍 Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate 
```

---

### 3. 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. ⚙️ Setup PostgreSQL Database

- Ensure PostgreSQL is running locally

```bash
sudo -u postgres psql

```
- Create a database and a user with permissions:

```sql
CREATE DATABASE notifications;
CREATE USER your-user WITH PASSWORD your-password;
GRANT ALL PRIVILEGES ON DATABASE notifications TO your-user;
ALTER USER your-user CREATEDB;


```

---

### 5. 🧪 Setup Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` to include:

```env
ONESIGNAL_APP_ID=your-onesignal-app-id
ONESIGNAL_API_KEY=your-onesignal-api-key

DB_NAME=notifications
DB_USER=your-user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432


```

---

### 6. 🔨 Run Migrations

```bash
python manage.py makemigrations users notifications
python manage.py migrate
```

---

### 7. 🔨 Create a superuser to mock admin users

```bash
python manage.py createsuperuser
```

---

### 8. 🚀 Start the Development Server

```bash
python manage.py runserver
```

API will be available at: `http://localhost:8000/api/`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /api/notifications/              | List user notifications |
| GET    | /api/notifications/<id>/        | View a notification |
| POST   | /api/notifications/send/        | Send notification to user |
| POST   | /api/notifications/send-broadcast/ | Broadcast notification |
| PATCH  | /api/profiles/register-onesignal-player/ | Update player ID |


---

## 🧪 Running Tests

```bash
pytest
```

To view test coverage:

```bash
pytest --cov=notifications
```
