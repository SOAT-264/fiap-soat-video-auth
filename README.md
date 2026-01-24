# 🔐 Video Processor - Auth Service

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Microserviço de autenticação responsável pelo registro, login e validação de tokens JWT.

## 📋 Índice

- [Arquitetura](#-arquitetura)
- [API Endpoints](#-api-endpoints)
- [Como Executar](#-como-executar)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Testes](#-testes)

---

## 🏗️ Arquitetura

Este serviço segue a **Arquitetura Hexagonal (Ports & Adapters)**:

```
src/auth_service/
├── domain/
│   └── entities/user.py         # Entidade User
├── application/
│   ├── ports/                   # Interfaces
│   │   ├── input/               # IAuthService
│   │   └── output/              # IUserRepository
│   └── use_cases/               # RegisterUser, LoginUser
└── infrastructure/
    ├── adapters/
    │   ├── input/api/           # FastAPI routes
    │   └── output/persistence/  # SQLAlchemy repository
    └── config/                  # Settings
```

---

## 📡 API Endpoints

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| POST | `/auth/register` | Registrar novo usuário | ❌ |
| POST | `/auth/login` | Fazer login | ❌ |
| GET | `/auth/me` | Obter dados do usuário | ✅ JWT |
| GET | `/health` | Health check | ❌ |

### Exemplos

#### Registrar

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "João Silva"
  }'
```

**Resposta:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "João Silva",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Login

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Me (Profile)

```bash
curl http://localhost:8001/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.11+
- PostgreSQL

### 1. Clone e instale

```bash
git clone https://github.com/morgadope/fiap-soat-video-auth.git
cd fiap-soat-video-auth
pip install -e ".[dev]"
```

### 2. Configure as variáveis

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/auth_db"
export JWT_SECRET="your-super-secret-key"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRATION_HOURS=1
```

### 3. Execute

```bash
uvicorn auth_service.infrastructure.adapters.input.api.main:app --reload --port 8001
```

### 4. Acesse

- **Swagger**: http://localhost:8001/docs
- **Health**: http://localhost:8001/health

---

## 🐳 Docker

```bash
# Build
docker build -t auth-service .

# Run
docker run -p 8001:8001 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e JWT_SECRET="your-secret" \
  auth-service
```

---

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL de conexão PostgreSQL | - |
| `JWT_SECRET` | Chave secreta para JWT | - |
| `JWT_ALGORITHM` | Algoritmo JWT | HS256 |
| `JWT_EXPIRATION_HOURS` | Tempo de expiração do token | 1 |

---

## 🧪 Testes

```bash
# Rodar testes
pytest tests/ -v

# Com cobertura
pytest tests/ -v --cov=auth_service --cov-report=html
```

---

## 📄 Licença

MIT License
