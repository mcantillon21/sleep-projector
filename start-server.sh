#!/bin/bash
# Start the webhook server in the background

cd /Users/molly/sleep-projector

# Check if server is already running
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Webhook server already running on port 5001"
else
    echo "🚀 Starting webhook server..."
    python3 webhook_server.py > /tmp/sleep-projector-server.log 2>&1 &
    echo "✅ Server started (logs: /tmp/sleep-projector-server.log)"
fi
