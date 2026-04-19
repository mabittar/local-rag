# Local RAG Makefile
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.PHONY: help install up down restart logs ps test clean shell-backend shell-db migrate

help:
	@echo "Local RAG - Comandos disponíveis:"
	@echo "  make install         - Instala dependências locais (backend e frontend)"
	@echo "  make up              - Sobe todos os serviços via Docker"
	@echo "  make down            - Para todos os serviços"
	@echo "  make restart         - Reinicia os containers"
	@echo "  make logs            - Mostra logs de todos os serviços"
	@echo "  make ps              - Lista os containers e status"
	@echo "  make test            - Executa os testes E2E (via container)"
	@echo "  make migrate         - Executa as migrations do banco de dados"
	@echo "  make shell-backend   - Abre um terminal no container do backend"
	@echo "  make shell-db        - Abre o psql no container do banco"
	@echo "  make clean           - Remove containers, volumes e limpa uploads"

install:
	@echo "Instalando backend..."
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	@echo "Instalando frontend..."
	cd frontend && pnpm install
	@echo "Instalando e2e-tests..."
	cd e2e-tests && pnpm install

up:
	docker-compose up -d --build

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

ps:
	docker-compose ps

test:
	docker-compose run --rm --env-file .env e2e-tests pnpm run test

migrate:
	docker-compose exec backend alembic upgrade head

shell-backend:
	docker-compose exec backend /bin/bash

shell-db:
	docker-compose exec postgres psql -U localrag -d localrag

clean:
	docker-compose down -v
	rm -rf backend/data/uploads/*
