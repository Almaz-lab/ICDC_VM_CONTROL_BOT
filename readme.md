# ICDC Cloud Telegram Bot 🤖

A powerful Telegram bot designed to seamlessly manage your virtual machines (VMs) on ICDC cloud platform.

## ✨ Features
- 📋 Get comprehensive list of VMs
- 🚀 Start up VMs instantly
- 🛑 Shutdown VMs safely

## 📋 Prerequisites
- Docker
- Docker Compose
- Telegram Bot Token
- ICDC Cloud credentials

## 🛠️ Setup
1. Clone this repository to your local machine
2. Create your environment file by copying `env-example.env` to `.env`
3. Configure your credentials in the `.env` file

## 🚀 Running the Bot
```bash
docker compose up --build -d
```

## ⚙️ Environment Variables
For a complete list of required environment variables, please refer to `env-example.env`.

## 📝 Important Notes
- Ensure you have proper permissions and valid credentials for ICDC cloud access
- The Compute platform is built on ManageIQ - you can refer to the [ManageIQ API documentation](https://www.manageiq.org/docs/api) for detailed information
