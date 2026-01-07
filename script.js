// =============================================================================
// CONFIGURATION - Customize these values for your setup
// =============================================================================
const CONFIG = {
    // Display name (shown at top of screen, leave empty to hide)
    displayName: '',

    // Your location for sunrise/sunset calculations
    // Find your coordinates at: https://www.latlong.net/
    latitude: 37.7749,   // Default: San Francisco, CA
    longitude: -122.4194,

    // YouTube video ID for background ambiance
    // Default: "STARKEEP - Ancient Space Sanctuary" (ambient sleep music)
    // Find video ID from URL: youtube.com/watch?v=VIDEO_ID_HERE
    youtubeVideoId: '4xVqlc-L9ok',

    // Sleep duration in hours (default: 6 hours = 4 x 90-min REM cycles)
    sleepDurationHours: 6,

    // Wake-up phrases (randomly displayed when alarm triggers)
    wakePhrases: [
        "Momentum starts now",
        "Secrets are left to be discovered",
        "Make it look effortless",
        "Great or nothing",
        "Future you is watching",
        "Outsized impact today",
        "The work will be astonishing",
        "Full ownership",
        "You define the rules",
        "Unstoppable",
        "Iconoclasm",
    ],

    // Backend API URL (change if running on different host/port)
    apiBaseUrl: 'http://localhost:5001',

    // Set to true to auto-detect location (requires HTTPS or localhost)
    autoDetectLocation: false,
};
// =============================================================================

// DOM Elements
const currentTimeEl = document.getElementById('currentTime');
const currentDateEl = document.getElementById('currentDate');
const sunriseInfoEl = document.getElementById('sunriseInfo');
const recoveryValueEl = document.getElementById('recoveryValue');
const sleepValueEl = document.getElementById('sleepValue');
const strainValueEl = document.getElementById('strainValue');
const recoveryScoreEl = document.getElementById('recoveryScore');
const strainScoreEl = document.getElementById('strainScore');

console.log('[INIT] DOM Elements found:');
console.log('  recoveryValueEl:', recoveryValueEl);
console.log('  sleepValueEl:', sleepValueEl);
console.log('  strainValueEl:', strainValueEl);

// Location coordinates (from config or auto-detected)
let LATITUDE = CONFIG.latitude;
let LONGITUDE = CONFIG.longitude;

// API Configuration
const API_BASE_URL = CONFIG.apiBaseUrl;

// Auto-detect location if enabled
function autoDetectLocation() {
    if (CONFIG.autoDetectLocation && navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                LATITUDE = position.coords.latitude;
                LONGITUDE = position.coords.longitude;
                console.log(`[LOCATION] Auto-detected: ${LATITUDE}, ${LONGITUDE}`);
            },
            (error) => {
                console.log('[LOCATION] Auto-detect failed, using default:', error.message);
            }
        );
    }
}

// YouTube Player
let player;
let playerReady = false;
let userInteracted = false;

// Load YouTube IFrame API
function loadYouTubeAPI() {
    console.log('[SOUND] Loading YouTube IFrame API...');
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    console.log('[SOUND] YouTube API script tag added');
}

// Called automatically by YouTube API when ready
function onYouTubeIframeAPIReady() {
    console.log('[SOUND] YouTube IFrame API Ready callback triggered');
    console.log('[SOUND] YT object available:', typeof YT !== 'undefined');

    try {
        player = new YT.Player('youtubePlayer', {
            events: {
                'onReady': onPlayerReady,
                'onStateChange': onPlayerStateChange
            }
        });
        console.log('[SOUND] YT.Player created successfully');
    } catch (e) {
        console.error('[SOUND] Error creating YT.Player:', e);
    }
}

// Player ready - wait for user interaction
function onPlayerReady(event) {
    playerReady = true;
    console.log('[SOUND] YouTube player ready');
    console.log('[SOUND] Player state:', event.target.getPlayerState());
    console.log('[SOUND] Is muted:', event.target.isMuted());
    console.log('[SOUND] Volume:', event.target.getVolume());

    // If user already clicked, unmute now
    if (userInteracted) {
        console.log('[SOUND] User already interacted, unmuting now');
        unmuteVideo();
    } else {
        console.log('[SOUND] Waiting for user interaction...');
    }
}

// Handle player state changes
function onPlayerStateChange(event) {
    const states = {
        '-1': 'UNSTARTED',
        '0': 'ENDED',
        '1': 'PLAYING',
        '2': 'PAUSED',
        '3': 'BUFFERING',
        '5': 'CUED'
    };
    console.log('[SOUND] Player state changed to:', states[event.data] || event.data);

    // Keep video unmuted when playing
    if (event.data === YT.PlayerState.PLAYING && userInteracted) {
        console.log('[SOUND] Video playing, ensuring unmuted');
        event.target.unMute();
        console.log('[SOUND] Is muted after unmute:', event.target.isMuted());
    }
}

// Unmute the video
function unmuteVideo() {
    console.log('[SOUND] unmuteVideo() called');
    console.log('[SOUND] player exists:', !!player);
    console.log('[SOUND] playerReady:', playerReady);

    if (player && playerReady) {
        try {
            console.log('[SOUND] Before unmute - isMuted:', player.isMuted());
            console.log('[SOUND] Before unmute - volume:', player.getVolume());

            player.unMute();
            player.setVolume(100);

            console.log('[SOUND] After unmute - isMuted:', player.isMuted());
            console.log('[SOUND] After unmute - volume:', player.getVolume());
            console.log('[SOUND] Video unmuted successfully - volume set to 100%');
        } catch (e) {
            console.error('[SOUND] Error unmuting video:', e);
        }
    } else {
        console.warn('[SOUND] Cannot unmute - player not ready');
    }
}

// Handle sound overlay click
function enableSound() {
    console.log('[SOUND] ===== enableSound() called =====');
    userInteracted = true;
    const overlay = document.getElementById('soundOverlay');
    console.log('[SOUND] Overlay element:', overlay);

    if (overlay) {
        overlay.classList.add('hidden');
        console.log('[SOUND] Overlay hidden');
    }

    console.log('[SOUND] User clicked to enable sound');
    unmuteVideo();

    // Also request fullscreen
    requestFullscreen();
}

// Request fullscreen mode
function requestFullscreen() {
    const elem = document.documentElement;
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) {
        elem.webkitRequestFullscreen();
    } else if (elem.mozRequestFullScreen) {
        elem.mozRequestFullScreen();
    } else if (elem.msRequestFullscreen) {
        elem.msRequestFullscreen();
    }
    console.log('[FULLSCREEN] Fullscreen requested');
}

// Make functions available globally for YouTube API
window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;

// Initialize
function init() {
    console.log('[INIT] Sleep Projector starting...');
    console.log(`[INIT] Location: ${LATITUDE}, ${LONGITUDE}`);
    console.log(`[INIT] API URL: ${API_BASE_URL}`);

    // Set up display name
    const nameEl = document.querySelector('.name');
    if (nameEl) {
        if (CONFIG.displayName) {
            nameEl.textContent = CONFIG.displayName;
        } else {
            // Hide name section if no name configured
            const nameSection = document.querySelector('.name-section');
            if (nameSection) nameSection.style.display = 'none';
        }
    }

    // Set up YouTube video with configured video ID
    const youtubePlayer = document.getElementById('youtubePlayer');
    if (youtubePlayer && CONFIG.youtubeVideoId) {
        const videoId = CONFIG.youtubeVideoId;
        youtubePlayer.src = `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&mute=1&controls=0&loop=1&playlist=${videoId}&modestbranding=1&showinfo=0&rel=0&disablekb=1&fs=0&iv_load_policy=3&enablejsapi=1`;
        console.log(`[INIT] YouTube video set to: ${videoId}`);
    }

    // Try to auto-detect location if enabled
    autoDetectLocation();

    updateClock();
    setInterval(updateClock, 1000);

    // Fetch Whoop data immediately
    fetchWhoopData();

    // Refresh Whoop data every 5 minutes
    setInterval(fetchWhoopData, 5 * 60 * 1000);

    // Load YouTube API to control video
    loadYouTubeAPI();

    // Add click handler for sound overlay
    const soundOverlay = document.getElementById('soundOverlay');
    console.log('[SOUND] Sound overlay element:', soundOverlay);
    if (soundOverlay) {
        soundOverlay.addEventListener('click', enableSound);
        console.log('[SOUND] Click event listener added to overlay');
    } else {
        console.error('[SOUND] Sound overlay element not found!');
    }
}

// Calculate time until sunrise
function getTimeUntilSunrise() {
    const now = new Date();
    const times = SunCalc.getTimes(now, LATITUDE, LONGITUDE);
    let sunrise = times.sunrise;

    // If sunrise already passed today, get tomorrow's sunrise
    if (now > sunrise) {
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const tomorrowTimes = SunCalc.getTimes(tomorrow, LATITUDE, LONGITUDE);
        sunrise = tomorrowTimes.sunrise;
    }

    const diffMs = sunrise - now;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

    if (diffHours === 0) {
        return `${diffMins}m to sunrise`;
    } else if (diffMins === 0) {
        return `${diffHours}h to sunrise`;
    } else {
        return `${diffHours}h ${diffMins}m to sunrise`;
    }
}

// Update clock display
function updateClock() {
    const now = new Date();

    // Time (with timezone)
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');

    // Get timezone abbreviation
    const timezone = now.toLocaleTimeString('en-US', { timeZoneName: 'short' }).split(' ')[2];

    currentTimeEl.textContent = `${hours}:${minutes} ${timezone}`;

    // Date (Day of week, Month Day, Year)
    const dayOfWeek = now.toLocaleDateString('en-US', { weekday: 'long' });
    const month = now.toLocaleDateString('en-US', { month: 'long' });
    const day = now.getDate();
    const year = now.getFullYear();

    currentDateEl.textContent = `${dayOfWeek}, ${month} ${day}, ${year}`;

    // Sunrise info
    if (typeof SunCalc !== 'undefined') {
        sunriseInfoEl.textContent = getTimeUntilSunrise();
    }
}

// Fetch Whoop data from the backend
async function fetchWhoopData() {
    try {
        console.log('[WHOOP] ===== Fetching Whoop data... =====');
        console.log('[WHOOP] API Base URL:', API_BASE_URL);

        // Fetch all data in parallel
        const [recoveryRes, sleepRes, workoutRes, cycleRes] = await Promise.all([
            fetch(`${API_BASE_URL}/api/recovery`).catch(e => {
                console.error('[WHOOP] Recovery fetch error:', e);
                return null;
            }),
            fetch(`${API_BASE_URL}/api/sleep`).catch(e => {
                console.error('[WHOOP] Sleep fetch error:', e);
                return null;
            }),
            fetch(`${API_BASE_URL}/api/workout`).catch(e => {
                console.error('[WHOOP] Workout fetch error:', e);
                return null;
            }),
            fetch(`${API_BASE_URL}/api/cycle`).catch(e => {
                console.error('[WHOOP] Cycle fetch error:', e);
                return null;
            })
        ]);

        console.log('[WHOOP] Recovery response:', recoveryRes?.status, recoveryRes?.ok);
        console.log('[WHOOP] Sleep response:', sleepRes?.status, sleepRes?.ok);
        console.log('[WHOOP] Workout response:', workoutRes?.status, workoutRes?.ok);
        console.log('[WHOOP] Cycle response:', cycleRes?.status, cycleRes?.ok);

        // Parse responses
        const recoveryData = recoveryRes && recoveryRes.ok ? await recoveryRes.json() : null;
        const sleepData = sleepRes && sleepRes.ok ? await sleepRes.json() : null;
        const workoutData = workoutRes && workoutRes.ok ? await workoutRes.json() : null;
        const cycleData = cycleRes && cycleRes.ok ? await cycleRes.json() : null;

        console.log('[WHOOP] Recovery data:', recoveryData);
        console.log('[WHOOP] Sleep data:', sleepData);
        console.log('[WHOOP] Workout data:', workoutData);
        console.log('[WHOOP] Cycle data:', cycleData);

        // Update UI with fetched data
        updateRecoveryUI(recoveryData);
        updateSleepUI(sleepData);
        updateStrainUI(workoutData, cycleData);

        console.log('[WHOOP] Whoop data updated successfully');
    } catch (error) {
        console.error('[WHOOP] Error fetching Whoop data:', error);
        showError();
    }
}

// Update Recovery UI
function updateRecoveryUI(data) {
    console.log('[WHOOP] updateRecoveryUI called with:', data);
    console.log('[WHOOP] data type:', typeof data);
    console.log('[WHOOP] data keys:', data ? Object.keys(data) : 'null');

    if (!data || !data.score) {
        console.log('[WHOOP] No recovery data available - data:', data);
        recoveryValueEl.textContent = '--';
        return;
    }

    console.log('[WHOOP] data.score:', data.score);
    console.log('[WHOOP] data.score.recovery_score:', data.score.recovery_score);

    const recoveryScore = Math.round(data.score.recovery_score);
    console.log('[WHOOP] Recovery score (rounded):', recoveryScore);
    console.log('[WHOOP] Setting recoveryValueEl.textContent to:', recoveryScore);
    console.log('[WHOOP] recoveryValueEl element:', recoveryValueEl);
    recoveryValueEl.textContent = recoveryScore;
    console.log('[WHOOP] After setting, recoveryValueEl.textContent is:', recoveryValueEl.textContent);

    // Update color based on score
    recoveryScoreEl.classList.remove('low', 'medium');
    if (recoveryScore < 33) {
        recoveryScoreEl.classList.add('low');
    } else if (recoveryScore < 67) {
        recoveryScoreEl.classList.add('medium');
    }
}

// Update Sleep UI
function updateSleepUI(data) {
    console.log('[WHOOP] updateSleepUI called with:', data);

    if (!data || !data.score) {
        console.log('[WHOOP] No sleep data available');
        sleepValueEl.textContent = '--';
        return;
    }

    // Sleep performance percentage
    if (data.score.sleep_performance_percentage !== undefined) {
        const sleepScore = Math.round(data.score.sleep_performance_percentage);
        console.log('[WHOOP] Sleep score:', sleepScore);
        console.log('[WHOOP] sleepValueEl element:', sleepValueEl);
        sleepValueEl.textContent = sleepScore;
        console.log('[WHOOP] After setting, sleepValueEl.textContent is:', sleepValueEl.textContent);
    }
}

// Update Strain UI
function updateStrainUI(workoutData, cycleData) {
    console.log('[WHOOP] updateStrainUI called');
    console.log('[WHOOP] Workout data:', workoutData);
    console.log('[WHOOP] Cycle data:', cycleData);

    let strain = 0;

    // Get strain from cycle data (preferred)
    if (cycleData && cycleData.score && cycleData.score.strain) {
        strain = cycleData.score.strain;
        console.log('[WHOOP] Strain from cycle data:', strain);
    }
    // Fallback to workout data
    else if (workoutData && workoutData.score && workoutData.score.strain) {
        strain = workoutData.score.strain;
        console.log('[WHOOP] Strain from workout data:', strain);
    }

    if (strain > 0) {
        console.log('[WHOOP] Setting strain value:', strain.toFixed(1));
        console.log('[WHOOP] strainValueEl element:', strainValueEl);
        strainValueEl.textContent = strain.toFixed(1);
        console.log('[WHOOP] After setting, strainValueEl.textContent is:', strainValueEl.textContent);

        // Update color based on strain level
        strainScoreEl.classList.remove('high');
        if (strain >= 18) {
            strainScoreEl.classList.add('high');
        }
    } else {
        console.log('[WHOOP] No strain data available');
        strainValueEl.textContent = '--';
    }
}

// Show error state
function showError() {
    console.error('[WHOOP] Error loading data');
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', init);
