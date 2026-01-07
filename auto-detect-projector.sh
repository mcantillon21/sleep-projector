#!/bin/bash
# Automatically detect when projector is connected and launch app

cd /Users/molly/sleep-projector

echo "👀 Watching for external displays..."
echo "Plug in your projector to launch the app automatically"

# Function to check display count
check_displays() {
    system_profiler SPDisplaysDataType | grep -c "Resolution:"
}

INITIAL_DISPLAYS=$(check_displays)
echo "📺 Current displays: $INITIAL_DISPLAYS"

# Monitor for display changes
while true; do
    sleep 2
    CURRENT_DISPLAYS=$(check_displays)

    if [ "$CURRENT_DISPLAYS" -gt "$INITIAL_DISPLAYS" ]; then
        echo "🎬 External display detected! Launching sleep projector..."
        ./launch-on-projector.sh
        INITIAL_DISPLAYS=$CURRENT_DISPLAYS
        sleep 10  # Debounce
    elif [ "$CURRENT_DISPLAYS" -lt "$INITIAL_DISPLAYS" ]; then
        echo "📴 Display disconnected"
        INITIAL_DISPLAYS=$CURRENT_DISPLAYS
    fi
done
