#!/bin/bash
# Launch the sleep projector on external display when connected

cd /Users/molly/sleep-projector

# Ensure server is running
./start-server.sh

# Wait a moment for server
sleep 2

# Open in Chrome/Safari in fullscreen on external display
if [ -d "/Applications/Google Chrome.app" ]; then
    # Use Chrome
    open -a "Google Chrome" --new --args \
        --new-window \
        --app="http://localhost:5001" \
        --start-fullscreen \
        --autoplay-policy=no-user-gesture-required
else
    # Use Safari
    open -a Safari "http://localhost:5001"

    # Make Safari fullscreen (requires user to press Cmd+Ctrl+F)
    osascript -e 'tell application "Safari"
        activate
        delay 1
        tell application "System Events"
            keystroke "f" using {control down, command down}
        end tell
    end tell'
fi

echo "✅ Sleep Projector launched! Drag window to projector and press Cmd+Ctrl+F for fullscreen"
