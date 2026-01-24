# 🔐 Video Processor - Auth Service

Microserviço de autenticação responsável pelo registro, login e validação de tokens JWT.

## 📐 Arquitetura

```
fiap-soat-video-auth/
├── src/auth_service/
│   ├── domain/entities/          # User entity
│   ├── application/
│   │   ├── ports/                # Interfaces (IUserRepository)
│   │   └── use_cases/            # RegisterUser, LoginUser
│   └── infrastructure/
│       ├── adapters/input/api/   # FastAPI routes
│       ├── adapters/output/      # PostgreSQL repository
│       └── config/               # Settings
├── Dockerfile
└── pyproject.toml
```

## 🚀 Rodar Localmente

### Pré-requisitos

- Python 3.11+
- PostgreSQL rodando na porta 5434

### 1. Clone e instale

```bash
git clone https://github.com/morgadope/fiap-soat-video-auth.git
cd fiap-soat-video-auth
pip install -e ".[dev]"
```

### 2. Configure variáveis de ambiente

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/auth_db"
export JWT_SECRET="your-secret-key"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRATION_HOURS=1
```

### 3. Execute

```bash
uvicorn auth_service.infrastructure.adapters.input.api.main:app --reload --port 8001
```

### 4. Acesse

- Swagger: http://localhost:8001/docs
- Health: http://localhost:8001/health

## 📖 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/register` | Registrar novo usuário |
| POST | `/auth/login` | Fazer login e obter token |
| GET | `/auth/me` | Obter dados do usuário logado |
| GET | `/health` | Health check |

### Exemplos

**Registrar:**
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Test1234!","full_name":"Test User"}'
```

**Login:**
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Test1234!"}'
```

## 🐳 Docker

```bash
docker build -t auth-service .
docker run -p 8001:8001 -e DATABASE_URL=... -e JWT_SECRET=... auth-service
```

## 🧪 Testes

```bash
pytest tests/ -v --cov=auth_service
```

## 📄 Licença

MIT License
