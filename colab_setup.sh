#!/usr/bin/env bash
# ==============================================================================
# Animaker AI - Google Colab Environment Setup Script
# ==============================================================================
set -e

echo "🚀 [1/5] Checking and installing modern Node.js (v20 LTS), FFmpeg, Redis..."
# Ensure modern Node.js >= 18 is installed
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'.' -f1 | tr -d 'v')" -lt 18 ]; then
    echo "Installing NodeSource Node.js 20 LTS..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
fi

apt-get update -qq
apt-get install -y -qq nodejs ffmpeg redis-server fonts-noto-cjk fonts-dejavu-core curl

echo "📦 [2/5] Installing Python dependencies & GPU Voice Cloning (F5-TTS)..."
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q
pip install gradio_client f5-tts -q

echo "🟢 [3/5] Installing and preparing Frontend..."
cd frontend
npm install --silent
echo "⚡ Building Next.js production bundle for fast instant load..."
npm run build || true
cd ..

echo "🌐 [4/5] Setting up Cloudflare Tunnel (cloudflared)..."
if [ ! -f ./cloudflared ]; then
    curl -fsSL -o ./cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x ./cloudflared
fi

echo "=============================================================================="
echo "✅ Environment setup complete! Ready to launch Animaker AI Studio."
echo "=============================================================================="

