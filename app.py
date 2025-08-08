import aiohttp
from aiohttp import web
import os
import json
import base64
from datetime import datetime
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store processing parameters (for later stage)
processing_params = {
    'fps': 30,
    'batch_size': 64
}

# WebRTC connections storage
webrtc_connections = {}

async def index(request):
    """Serve the main HTML page"""
    return web.FileResponse('templates/index.html')

async def update_params(request):
    """Update processing parameters via WebSocket or HTTP"""
    global processing_params
    try:
        data = await request.json()
        
        if data:
            processing_params.update({
                'fps': int(data.get('fps', processing_params['fps'])),
                'batch_size': int(data.get('batch_size', processing_params['batch_size']))
            })
            
            logger.info(f"Processing parameters updated: {processing_params}")
            return web.json_response({'status': 'success', 'params': processing_params})
        
        return web.json_response({'status': 'error', 'message': 'Invalid data'})
    
    except Exception as e:
        logger.error(f"Error updating processing parameters: {e}")
        return web.json_response({'status': 'error', 'message': str(e)})

async def save_recording(request):
    """Save recorded audio data"""
    try:
        data = await request.json()
        if not data or 'audio_data' not in data:
            return web.json_response({'status': 'error', 'message': 'No audio data received'})
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"recording_{timestamp}.json"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save audio data and processing parameters
        recording_data = {
            'audio_data': data['audio_data'],
            'processing_parameters': processing_params,
            'timestamp': timestamp,
            'duration': data.get('duration', 0),
            'webrtc_session_id': data.get('session_id', None)
        }
        
        with open(filepath, 'w') as f:
            json.dump(recording_data, f, indent=2)
        
        logger.info(f"Recording saved: {filename}")
        return web.json_response({
            'status': 'success', 
            'message': 'Recording saved successfully',
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Error saving recording: {e}")
        return web.json_response({'status': 'error', 'message': str(e)})

async def get_params(request):
    """Get current processing parameters"""
    return web.json_response(processing_params)

async def webrtc_offer(request):
    """Handle WebRTC offer from client"""
    try:
        data = await request.json()
        offer = data.get('offer')
        session_id = data.get('session_id')
        
        if not offer:
            return web.json_response({'status': 'error', 'message': 'No offer received'})
        
        # Store the WebRTC connection
        webrtc_connections[session_id] = {
            'offer': offer,
            'created_at': datetime.now(),
            'processing_parameters': processing_params.copy()
        }
        
        logger.info(f"WebRTC offer received for session: {session_id}")
        
        # Return the same offer for now (in a real implementation, you'd process it)
        return web.json_response({
            'status': 'success',
            'answer': offer,  # Echo back for testing
            'session_id': session_id,
            'processing_parameters': processing_params
        })
        
    except Exception as e:
        logger.error(f"Error handling WebRTC offer: {e}")
        return web.json_response({'status': 'error', 'message': str(e)})

async def webrtc_ice_candidate(request):
    """Handle ICE candidate from client"""
    try:
        data = await request.json()
        candidate = data.get('candidate')
        session_id = data.get('session_id')
        
        if session_id in webrtc_connections:
            if 'ice_candidates' not in webrtc_connections[session_id]:
                webrtc_connections[session_id]['ice_candidates'] = []
            webrtc_connections[session_id]['ice_candidates'].append(candidate)
            
            logger.info(f"ICE candidate received for session: {session_id}")
            return web.json_response({'status': 'success'})
        
        return web.json_response({'status': 'error', 'message': 'Session not found'})
        
    except Exception as e:
        logger.error(f"Error handling ICE candidate: {e}")
        return web.json_response({'status': 'error', 'message': str(e)})

async def webrtc_audio_data(request):
    """Handle real-time audio data from WebRTC"""
    try:
        data = await request.json()
        audio_data = data.get('audio_data')
        session_id = data.get('session_id')
        timestamp = data.get('timestamp')
        
        if not audio_data or not session_id:
            return web.json_response({'status': 'error', 'message': 'Missing audio data or session ID'})
        
        # Store audio data for later processing
        # FPS and batch size parameters will be applied in a later stage
        
        logger.info(f"Audio data received for session {session_id} at {timestamp}")
        
        # Echo back confirmation
        return web.json_response({
            'status': 'success',
            'stored': True,
            'processing_parameters': processing_params
        })
        
    except Exception as e:
        logger.error(f"Error processing audio data: {e}")
        return web.json_response({'status': 'error', 'message': str(e)})

async def list_recordings(request):
    """List all saved recordings"""
    try:
        recordings = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.json'):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    recordings.append({
                        'filename': filename,
                        'timestamp': data.get('timestamp'),
                        'duration': data.get('duration'),
                        'processing_parameters': data.get('processing_parameters')
                    })
        
        recordings.sort(key=lambda x: x['timestamp'], reverse=True)
        return web.json_response({'recordings': recordings})
        
    except Exception as e:
        logger.error(f"Error listing recordings: {e}")
        return web.json_response({'status': 'error', 'message': str(e)})

async def get_recording(request):
    """Get a specific recording by filename"""
    try:
        filename = request.match_info['filename']
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return web.json_response({'status': 'error', 'message': 'Recording not found'}, status=404)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return web.json_response(data)
        
    except Exception as e:
        logger.error(f"Error getting recording: {e}")
        return web.json_response({'status': 'error', 'message': str(e)})

async def websocket_handler(request):
    """WebSocket handler for real-time communication"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    session_id = None
    
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                msg_type = data.get('type')
                
                if msg_type == 'init':
                    session_id = data.get('session_id')
                    logger.info(f"WebSocket connection established for session: {session_id}")
                    await ws.send_json({
                        'type': 'init_ack',
                        'session_id': session_id,
                        'processing_parameters': processing_params
                    })
                
                elif msg_type == 'audio_data':
                    # Handle real-time audio data
                    audio_data = data.get('audio_data')
                    if audio_data and session_id:
                        # Process audio with current parameters
                        processed = await process_audio_data(audio_data, recording_params)
                        await ws.send_json({
                            'type': 'audio_processed',
                            'processed': processed,
                            'parameters_applied': recording_params
                        })
                
                elif msg_type == 'update_params':
                    # Update parameters in real-time
                    new_params = data.get('params', {})
                    recording_params.update(new_params)
                    await ws.send_json({
                        'type': 'params_updated',
                        'parameters': recording_params
                    })
                
                elif msg_type == 'ping':
                    await ws.send_json({'type': 'pong'})
            
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"WebSocket error: {ws.exception()}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        if session_id and session_id in webrtc_connections:
            del webrtc_connections[session_id]
        logger.info(f"WebSocket connection closed for session: {session_id}")
    
    return ws

async def process_audio_data(audio_data, params):
    """Process audio data with given parameters"""
    # This is where you would apply FPS and batch size processing
    # For now, just return a simple confirmation
    return {
        'fps_applied': params['fps'],
        'batch_size_applied': params['batch_size'],
        'sample_rate': 44100,  # Fixed sample rate
        'channels': 1,         # Fixed mono channel
        'processed_at': datetime.now().isoformat()
    }

def create_app():
    """Create and configure the aiohttp application"""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/', index)
    app.router.add_post('/update_params', update_params)
    app.router.add_post('/save_recording', save_recording)
    app.router.add_get('/get_params', get_params)
    app.router.add_post('/webrtc/offer', webrtc_offer)
    app.router.add_post('/webrtc/ice-candidate', webrtc_ice_candidate)
    app.router.add_post('/webrtc/audio-data', webrtc_audio_data)
    app.router.add_get('/recordings', list_recordings)
    app.router.add_get('/recordings/{filename}', get_recording)
    app.router.add_get('/ws', websocket_handler)
    
    # Static file serving removed - not needed for this application
    
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info("Starting WebRTC Audio Recorder server...")
    logger.info("Server will be available at http://localhost:8080")
    web.run_app(app, host='0.0.0.0', port=8080)
