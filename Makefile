SHELL := /bin/zsh

BOT_HOST ?= 127.0.0.1
BOT_PORT ?= 1212
CLIENT_HOST ?= 127.0.0.1
CLIENT_PORT ?= 5100

.PHONY: dev server client install

dev:
	@$(MAKE) install
	@uv run bot.py -t webrtc --host $(BOT_HOST) --port $(BOT_PORT) & \
	bot_pid=$$!; \
	(cd client && BOT_PORT=$(BOT_PORT) npm run dev -- --host $(CLIENT_HOST) --port $(CLIENT_PORT)) & \
	client_pid=$$!; \
	cleanup() { kill -TERM $$bot_pid $$client_pid 2>/dev/null || true; wait $$bot_pid $$client_pid 2>/dev/null || true; }; \
	trap 'cleanup; exit 130' INT TERM; \
	trap cleanup EXIT; \
	wait $$bot_pid $$client_pid

server:
	uv run bot.py -t webrtc --host $(BOT_HOST) --port $(BOT_PORT)

client:
	cd client && BOT_PORT=$(BOT_PORT) npm run dev -- --host $(CLIENT_HOST) --port $(CLIENT_PORT)

install:
	uv sync
	cd client && npm install
