# How to Add Your Video

The app needs a video file named `video.mp4` in the sleep-projector directory.

## Option 1: Download Your Own Video (Recommended)

1. Find a shorter sunset/sunrise video on YouTube (ideally < 10 minutes)
2. Download it using:
   ```bash
   cd sleep-projector
   yt-dlp -o video.mp4 'YOUR_VIDEO_URL'
   ```

## Option 2: Use a Different Video

If that YouTube video won't embed, try searching for:
- "sunset timelapse"
- "sunrise timelapse"
- "relaxing nature video"

Look for shorter videos (5-10 min) that allow embedding

## Option 3: Use a Placeholder

For now, download any short video from your computer or use a solid color background:
1. Create a simple placeholder using ffmpeg:
   ```bash
   ffmpeg -f lavfi -i color=c=blue:s=1920x1080:d=10 -c:v libx264 video.mp4
   ```

## Current Status

The original video (Q-sZipetAEc) is too large (25+ GB).

Try this shorter sunset video instead:
```bash
yt-dlp -o video.mp4 'https://www.youtube.com/watch?v=Bey4XXJAqS8'
```

Once you have `video.mp4` in the directory, refresh your browser!
