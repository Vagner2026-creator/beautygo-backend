# BeautyGO — Checklist de Deploy em Produção

Use este documento antes de cada deploy para garantir que o ambiente de produção está configurado corretamente.

---

## Variáveis de Ambiente

- [ ] `DATABASE_URL` apontando para PostgreSQL de produção
- [ ] `REDIS_URL` apontando para Redis de produção
- [ ] `SECRET_KEY` gerada com 64+ caracteres aleatórios
  ```bash
  python -c "import secrets; print(secrets.token_hex(64))"
  ```
- [ ] `DEBUG=false`
- [ ] `ENVIRONMENT=production`
- [ ] `CORS_ORIGINS` configurado com o(s) domínio(s) real(is) do frontend (sem wildcard)
- [ ] `SENTRY_DSN` configurado com o projeto correto do Sentry
- [ ] `RATE_LIMIT_PER_MINUTE` ajustado para o tráfego esperado

---

## Banco de Dados

- [ ] PostgreSQL rodando em servidor dedicado (não no mesmo container da API)
- [ ] Usuário do banco com permissões mínimas necessárias (não usar superuser em prod)
- [ ] Migrations aplicadas: `alembic upgrade head`
- [ ] Backup automático do PostgreSQL configurado (diário, mínimo 7 dias de retenção)
- [ ] Restore testado pelo menos uma vez

---

## Redis

- [ ] Redis rodando em servidor dedicado
- [ ] Senha do Redis configurada (`requirepass`)
- [ ] `maxmemory-policy` configurado (ex: `allkeys-lru`)

---

## Infraestrutura

- [ ] HTTPS configurado (Cloudflare, nginx com Let's Encrypt, ou similar)
- [ ] Certificado SSL válido e renovação automática ativa
- [ ] Firewall: apenas portas 80 e 443 expostas publicamente
- [ ] Porta 8000 da API acessível apenas internamente (nginx/proxy reverso na frente)

---

## Aplicação

- [ ] Imagem Docker buildada com tag versionada (não usar `latest` em prod)
- [ ] Health check configurado no orquestrador: `GET /health`
- [ ] Número adequado de workers Uvicorn/Gunicorn para a carga esperada
- [ ] Política de restart automático configurada (ex: `restart: always`)

---

## Monitoramento e Logs

- [ ] Logs da aplicação direcionados para sistema centralizado (CloudWatch, Loki, Papertrail, etc.)
- [ ] Alertas configurados no Sentry para erros críticos
- [ ] Prometheus coletando métricas da API
- [ ] Dashboard Grafana configurado com alertas de latência e taxa de erro
- [ ] Alerta de disponibilidade (uptime monitor externo, ex: UptimeRobot, Better Uptime)

---

## Segurança

- [ ] `SECRET_KEY` nunca commitada no repositório
- [ ] `.env` de produção fora do repositório (usar secrets manager ou variáveis de CI/CD)
- [ ] Dependências verificadas: `pip audit` sem vulnerabilidades críticas
- [ ] Rate limiting validado em staging antes do deploy
- [ ] Headers de segurança validados (SecurityHeadersMiddleware ativo)

---

## Testes

- [ ] Suite de testes executada e passando: `pytest app/tests/ -v`
- [ ] Testes de integração executados em ambiente de staging
- [ ] Smoke test executado após deploy (health check + login + listagem básica)

---

## Pós-Deploy

- [ ] `/health` retornando `{"status": "ok"}` em produção
- [ ] Login funcional com usuário de teste
- [ ] Logs sem erros críticos nos primeiros 10 minutos
- [ ] Métricas de latência dentro do esperado (p95 < 500ms para endpoints principais)
- [ ] Rollback testado e documentado caso necessário
