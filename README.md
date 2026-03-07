# fiap-soat-video-auth

## Introdução
Microserviço de autenticação e identidade do ecossistema FIAP SOAT Video Processor. Ele gerencia cadastro, login, validação de token JWT e consulta de usuário para consumo interno pelos outros serviços.

## Sumário
- Explicação do projeto
- Objetivo
- Como funciona
- Repositórios relacionados
- Integrações com outros repositórios
- Como executar
- Como testar

## Repositórios relacionados
- [fiap-soat-video-local-dev](https://github.com/SOAT-264/fiap-soat-video-local-dev)
- [fiap-soat-video-service](https://github.com/SOAT-264/fiap-soat-video-service)
- [fiap-soat-video-notifications](https://github.com/SOAT-264/fiap-soat-video-notifications)
- [fiap-soat-video-shared](https://github.com/SOAT-264/fiap-soat-video-shared)
- [fiap-soat-video-obs](https://github.com/SOAT-264/fiap-soat-video-obs)

## Explicação do projeto
O projeto segue uma organização em camadas (`application`, `domain`, `infrastructure`) e expõe uma API FastAPI para autenticação. O serviço utiliza PostgreSQL para persistência de usuários e disponibiliza endpoint de métricas Prometheus em `/metrics`.

## Objetivo
Ser a fonte central de identidade da plataforma, garantindo autenticação consistente e suporte à autorização entre os microserviços.

## Como funciona
1. `POST /auth/register` cadastra novos usuários com validações de e-mail e senha.
2. `POST /auth/login` autentica o usuário e retorna JWT.
3. `GET /auth/me` valida o token bearer e retorna dados do usuário autenticado.
4. `GET /auth/users/{user_id}` expõe consulta interna de usuário (usado por outros serviços).
5. Endpoints de suporte:
`POST /auth/validate`, `GET /health`, `GET /ready`, `GET /metrics`.

## Integrações com outros repositórios
| Repositório integrado | Como integra | Para que serve |
| --- | --- | --- |
| `fiap-soat-video-local-dev` | Build/deploy local via `start.ps1`, infraestrutura (PostgreSQL/Redis) e roteamento `auth.localhost` | Executar e validar o serviço no ambiente integrado principal |
| `fiap-soat-video-service` | Chamada HTTP em `GET /auth/me` para validar token em operações de vídeo | Garantir que upload/listagem de vídeos seja autenticada |
| `fiap-soat-video-notifications` | Chamada HTTP em `GET /auth/users/{id}` para obter e-mail do destinatário | Resolver e-mail do usuário para envio de notificações |
| `fiap-soat-video-jobs` | Configuração de `AUTH_SERVICE_URL` no ambiente integrado | Manter contrato de identidade entre serviços no ambiente distribuído |
| `fiap-soat-video-shared` | Uso de value objects e exceções compartilhadas (`Email`, `Password`, erros de domínio) | Padronizar regras de domínio e contratos entre serviços |
| `fiap-soat-video-obs` | Exposição de `/health` e `/metrics` consumidos por Prometheus/Blackbox | Observabilidade de saúde e métricas do serviço |

## Como executar
### Pré-requisitos
- Python 3.11+
- Dependências de infraestrutura (recomendado subir via `fiap-soat-video-local-dev`)

### Execução local da API
```powershell
cd /fiap-soat-video-auth
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

$env:DATABASE_URL="postgresql+asyncpg://postgres:postgres123@localhost:5432/auth_db"
$env:REDIS_URL="redis://localhost:6379/0"
$env:JWT_SECRET="dev-jwt-secret-key-change-in-production"
$env:JWT_ALGORITHM="HS256"
$env:JWT_EXPIRY_HOURS="24"

uvicorn auth_service.infrastructure.adapters.input.api.main:app --host 0.0.0.0 --port 8001 --reload
```

### Execução integrada (recomendada)
Suba pelo repositório principal:
```powershell
cd /fiap-soat-video-local-dev
.\start.ps1
```

## Como testar
```powershell
cd /fiap-soat-video-auth
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

