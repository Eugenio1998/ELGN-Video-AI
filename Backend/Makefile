# === 🔥 Dev ===
run:  ## Rodar o backend FastAPI local
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

celery:  ## Rodar o worker Celery
	PYTHONPATH=./backend celery -A app.celery_app worker --loglevel=info

# === 🧪 Testes ===
test:  ## Rodar os testes com Pytest
	PYTHONPATH=./backend pytest -v

test-watch:  ## Rodar testes automaticamente ao salvar
	ptw --onfail "notify-send '❌ Teste falhou'" --onpass "notify-send '✅ Todos os testes passaram!'"

# === 🐳 Docker ===
docker-up:  ## Subir containers com build
	docker-compose up --build

docker-down:  ## Derrubar os containers
	docker-compose down

docker-clean:  ## Limpar containers, imagens e volumes não utilizados
	docker system prune -a --volumes --force

# === 🐚 Acesso ===
shell:  ## Abrir terminal dentro do container backend
	docker exec -it elgn_backend /bin/bash

logs:  ## Ver logs do backend
	docker logs -f elgn_backend

celery-logs:  ## Ver logs do Celery
	docker logs -f elgn_celery
