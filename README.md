# Sleep Projector

A ceiling projector display wired to WHOOP that wakes you after exactly 6 hours of sleep with ambient visuals and your favorite phrases.

![Sleep Projector](screenshot.png)

## What It Does

Project this onto your ceiling before bed. It displays your real-time WHOOP stats (recovery, sleep score, strain), a countdown to sunrise, and plays ambient background music. After 6 hours (4 complete 90-minute sleep cycles), it gently wakes you at the optimal point in your sleep cycle.

## Features

- **6-Hour Sleep Timer**: Wakes you after exactly 4 REM cycles for optimal rest
- **WHOOP Integration**: Live recovery score, sleep performance, and daily strain
- **Sunrise Countdown**: Know exactly when the sun rises at your location
- **Ambient Background**: Customizable YouTube video/audio for relaxation
- **Projector-Optimized**: High contrast, fullscreen display for ceiling projection
- **Personalized Wake-Up**: Configure your own motivational phrases

## Quick Start

### Basic Setup (Clock + Sunrise Only)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sleep-projector.git
   cd sleep-projector
   ```

2. Configure your location in `script.js`:
   ```javascript
   const CONFIG = {
       latitude: 37.7749,    // Your latitude
       longitude: -122.4194, // Your longitude
       // ...
   };
   ```
   Find your coordinates at [latlong.net](https://www.latlong.net/)

3. Open `index.html` in your browser, or run a local server:
   ```bash
   python3 -m http.server 8000
   # Then open http://localhost:8000
   ```

### Full Setup (with WHOOP Integration)

1. Complete the basic setup above

2. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Get WHOOP API credentials:
   - Go to [developer.whoop.com](https://developer.whoop.com/)
   - Create a developer account
   - Create a new application
   - Note your Client ID and Client Secret

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Add your Client ID and Secret to `.env`, then get your tokens:
   ```bash
   python3 get_whoop_token.py
   ```
   Follow the OAuth flow and add the tokens to `.env`.

5. Start the backend server:
   ```bash
   python3 webhook_server.py
   ```

6. Open http://localhost:5001 in your browser

## Configuration

### Display Settings (`script.js`)

```javascript
const CONFIG = {
    // Display name (shown at top of screen, leave empty to hide)
    displayName: 'YOUR NAME',

    // Your coordinates for sunrise/sunset calculations
    // Find yours at: https://www.latlong.net/
    latitude: 37.7749,
    longitude: -122.4194,

    // YouTube video ID for background ambiance
    // Default: "STARKEEP - Ancient Space Sanctuary" (ambient sleep music)
    youtubeVideoId: '4xVqlc-L9ok',

    // Sleep duration in hours (default: 6 = 4 x 90-min REM cycles)
    sleepDurationHours: 6,

    // Wake-up phrases (randomly shown when alarm triggers)
    wakePhrases: [
        "Momentum starts now",
        "Make it look effortless",
        "Great or nothing",
    ],

    // Backend API URL
    apiBaseUrl: 'http://localhost:5001',
};
```

### Environment Variables (`.env`)

| Variable | Description |
|----------|-------------|
| `WHOOP_CLIENT_ID` | Your WHOOP API client ID |
| `WHOOP_CLIENT_SECRET` | Your WHOOP API client secret |
| `WHOOP_ACCESS_TOKEN` | OAuth access token |
| `WHOOP_REFRESH_TOKEN` | OAuth refresh token |

## Project Structure

```
sleep-projector/
├── index.html          # Main HTML page
├── styles.css          # Styling
├── script.js           # Frontend JavaScript
├── webhook_server.py   # Flask backend for WHOOP API
├── get_whoop_token.py  # OAuth helper to get WHOOP tokens
├── start-server.sh     # Start the backend server
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Running on a Projector

For the best experience:

1. Connect a projector to your computer
2. Point it at your ceiling
3. Run the app in fullscreen mode (click anywhere to activate)
4. The display will show:
   - Current time and date
   - Time until sunrise
   - Your WHOOP stats (if configured)

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Backend**: Python Flask
- **APIs**: WHOOP Developer API, YouTube IFrame API
- **Libraries**: SunCalc (sunrise/sunset calculations)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Troubleshooting

### WHOOP data not showing
1. Check that the backend server is running (`python3 webhook_server.py`)
2. Verify your `.env` file has valid credentials
3. Check browser console for API errors

### Sunrise time is wrong
1. Verify your latitude/longitude in `script.js`
2. Make sure your computer's timezone is correct

### Video/audio not playing
1. Click anywhere on the screen to enable audio (browser autoplay policy)
2. Check that the YouTube video ID is valid

## License

MIT License - feel free to use and modify!

## Contributing

Contributions welcome! Please open an issue or PR.
