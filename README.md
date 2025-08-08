# WebRTC Audio Recorder

A modern web application that allows users to record audio using WebRTC technology with real-time parameter processing and customizable settings like FPS and batch size.

## Features

- 🎤 **Real-time Audio Recording**: Record audio directly in the browser using WebRTC
- 🔄 **WebRTC & MediaRecorder**: Choose between WebRTC (real-time) or MediaRecorder (traditional) recording
- ⚙️ **Customizable Parameters**: Adjust FPS, batch size, sample rate, and channels in real-time
- 📊 **Audio Visualization**: Real-time frequency spectrum visualization
- 💾 **Save Recordings**: Save recordings with metadata to the server
- 🌐 **WebSocket Communication**: Real-time parameter updates and audio processing
- 🎨 **Modern UI**: Beautiful, responsive design with smooth animations
- 📱 **Mobile Friendly**: Works on desktop and mobile devices

## Parameters

- **FPS (Frames Per Second)**: Controls the frame rate for processing (1-60)
- **Batch Size**: Number of samples processed together (16-256)
- **Sample Rate**: Audio sampling frequency (8kHz - 48kHz)
- **Channels**: Mono (1) or Stereo (2) recording

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:8080
   ```

## Usage

### Recording Modes

1. **Traditional Recording (MediaRecorder)**:
   - Click "Record" to start recording audio
   - Watch the visualization to see real-time audio frequency data
   - Click "Stop" when you're done recording
   - Click "Save" to save the recording to the server

2. **WebRTC Recording (Real-time)**:
   - Click "WebRTC" to start real-time WebRTC recording
   - Audio is processed in real-time with current parameters
   - WebSocket connection provides live parameter updates
   - Click "Stop" to end the WebRTC session
   - Click "Save" to save the WebRTC recording

### Parameter Management

1. **Adjust Parameters**: Use the sliders and dropdowns in the "Recording Parameters" section
2. **Click "Update Parameters"** to save your settings
3. **Real-time Updates**: Parameters are updated via both HTTP and WebSocket for immediate effect

## File Structure

```
AvatarWebServer/
├── app.py                 # Main aiohttp application with WebRTC support
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template with WebRTC functionality
└── uploads/              # Directory where recordings are saved (created automatically)
```

## Technical Details

### Backend (Python/aiohttp)
- **aiohttp**: Async web framework for handling HTTP and WebSocket requests
- **WebRTC Support**: Real-time audio processing with session management
- **WebSocket**: Real-time communication for parameter updates and audio data
- **JSON Storage**: Recordings are saved as JSON files with base64-encoded audio data
- **Parameter Management**: Server-side storage and validation of recording parameters

### Frontend (HTML/JavaScript)
- **WebRTC MediaRecorder API**: For traditional audio recording
- **RTCPeerConnection**: For real-time WebRTC audio streaming
- **Web Audio API**: For real-time audio analysis and visualization
- **WebSocket API**: For real-time communication with the server
- **Canvas API**: For drawing the frequency spectrum visualization
- **Fetch API**: For communicating with the aiohttp backend

### Audio Processing
- **Sample Rates**: 8kHz, 16kHz, 22.05kHz, 44.1kHz, 48kHz
- **Channels**: Mono (1 channel) or Stereo (2 channels)
- **Audio Effects**: Echo cancellation, noise suppression, and auto gain control
- **Real-time Processing**: FPS and batch size parameters applied in real-time
- **Format**: WAV format for compatibility

### WebRTC Features
- **Peer-to-Peer**: Direct audio streaming between client and server
- **ICE Candidates**: NAT traversal support with STUN servers
- **Session Management**: Unique session IDs for multiple connections
- **Real-time Stats**: Live connection statistics and processing metrics

## API Endpoints

### HTTP Endpoints
- `GET /` - Main application page
- `POST /update_params` - Update recording parameters
- `POST /save_recording` - Save recorded audio data
- `GET /get_params` - Get current recording parameters
- `GET /recordings` - List all saved recordings
- `GET /recordings/{filename}` - Get specific recording

### WebRTC Endpoints
- `POST /webrtc/offer` - Handle WebRTC offer from client
- `POST /webrtc/ice-candidate` - Handle ICE candidate from client
- `POST /webrtc/audio-data` - Handle real-time audio data

### WebSocket Endpoints
- `GET /ws` - WebSocket connection for real-time communication

## Browser Compatibility

This application requires a modern browser with support for:
- WebRTC RTCPeerConnection API
- WebRTC MediaRecorder API
- Web Audio API
- WebSocket API
- Canvas API
- Fetch API

**Supported browsers**:
- Chrome 47+
- Firefox 44+
- Safari 14+
- Edge 79+

## Security Notes

- The application runs on `localhost` by default
- Audio data is stored locally in the `uploads` directory
- WebRTC connections use STUN servers for NAT traversal
- HTTPS is recommended for production use to ensure secure audio transmission
- WebSocket connections are established over the same protocol as the main connection

## Customization

You can customize the application by modifying:

- **Recording parameters** in `app.py` (default values)
- **WebRTC configuration** in the RTCPeerConnection setup
- **UI styling** in the `<style>` section of `index.html`
- **Audio processing** in the JavaScript `WebRTCAudioRecorder` class
- **File storage** format and location in the aiohttp routes

## Troubleshooting

### Common Issues

1. **"Error starting recording"**
   - Make sure your browser supports WebRTC
   - Check that microphone permissions are granted
   - Try refreshing the page

2. **"WebSocket connection error"**
   - Check that the aiohttp server is running
   - Verify the WebSocket endpoint is accessible
   - Check browser console for connection errors

3. **"No audio detected"**
   - Check your microphone is working
   - Verify microphone permissions in browser settings
   - Try a different browser

4. **"Error saving recording"**
   - Check that the `uploads` directory exists and is writable
   - Verify the aiohttp server is running
   - Check browser console for network errors

### Development

To run in development mode with auto-reload:
```bash
python app.py
```

The application will be available at `http://localhost:8080` with debug mode enabled.

## Performance Considerations

- **WebRTC Mode**: Provides real-time audio processing but may use more bandwidth
- **MediaRecorder Mode**: More efficient for longer recordings
- **Parameter Updates**: Real-time via WebSocket, immediate effect on processing
- **Memory Usage**: Audio data is processed in chunks to manage memory efficiently

## License

This project is open source and available under the MIT License.
