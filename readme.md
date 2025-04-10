# ICDC Cloud Telegram Bot

A Telegram bot that connects to ICDC cloud to manage virtual machines (VMs).

## Features
- Get list of VMs
- Start up VMs
- Shutdown VMs


## Prerequisites
- Docker
- Docker Compose
- Telegram Bot Token
- ICDC Cloud credentials

## Setup
1. Clone this repository
2. Copy `env-example.env` to `.env`
3. Fill in the required credentials in `.env` file

## Running the Bot
```bash
docker compose up --build -d
```

## Environment Variables
See `env-example.env` for required environment variables.

## Note
Make sure you have the necessary permissions and credentials for ICDC cloud access before running the bot.
