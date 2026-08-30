#!/usr/bin/env bash

# Pastikan skrip berhenti jika ada ralat
set -e

# Lokasi direktori fail tempatan
DOWNLOAD_DIR="./downloads"
RPC_PORT=6800
RPC_SECRET=${ARIA2_RPC_SECRET:-"seedr_aria2_rahsia_din"}

# Memastikan folder downloads/ wujud
mkdir -p "$DOWNLOAD_DIR"

# Semak sama ada aria2c sudah berjalan di dalam sistem
if pgrep -x "aria2c" > /dev/null; then
    echo "ℹ️ Perkhidmatan aria2c daemon sudah sedia berjalan."
else
    echo "🚀 Memulakan daemon aria2c (RPC Mode)..."
    aria2c \
        --daemon=true \
        --enable-rpc=true \
        --rpc-listen-all=false \
        --rpc-listen-port=$RPC_PORT \
        --rpc-secret="$RPC_SECRET" \
        --dir="$DOWNLOAD_DIR" \
        --max-connection-per-server=16 \
        --min-split-size=10M \
        --split=16 \
        --max-concurrent-downloads=5 \
        --seed-time=0 \
        --quiet=true

    echo "✅ aria2c daemon berjaya dihidupkan di port $RPC_PORT!"
fi