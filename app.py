import os
import cv2
import numpy as np
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import google.generativeai as genai
import tempfile
import threading
from queue import Queue
import base64

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global variables for processing
processing_status = {}
commentary_queue = Queue()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_frames_for_analysis(video_path, max_frames=10):
    """Extract key frames from video for AI analysis"""
    cap = cv2.VideoCapture(video_path)
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Extract frames at regular intervals
    frame_interval = max(1, total_frames // max_frames)
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            # Convert frame to base64 for API
            _, buffer = cv2.imencode('.jpg', frame)
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            timestamp = frame_count / fps
            frames.append({
                'frame': frame_b64,
                'timestamp': timestamp,
                'frame_number': frame_count
            })
            
        frame_count += 1
        
        if len(frames) >= max_frames:
            break
    
    cap.release()
    return frames

def analyze_basketball_video_with_gemini(api_key, frames, video_info):
    """Use Gemini to analyze basketball video and generate commentary"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        commentary_events = []
        
        for i, frame_data in enumerate(frames):
            try:
                # Decode base64 image
                import PIL.Image
                import io
                
                image_data = base64.b64decode(frame_data['frame'])
                image = PIL.Image.open(io.BytesIO(image_data))
                
                # Create comprehensive prompt for basketball analysis
                prompt = f"""
                You are an expert basketball coach analyzing a basketball video frame.
                
                Frame Details:
                - Frame {i+1} of {len(frames)}
                - Timestamp: {frame_data['timestamp']:.1f} seconds
                - Video duration: {video_info['duration']:.1f} seconds
                
                Please analyze this basketball frame and provide detailed coaching feedback:
                
                1. IDENTIFY: What basketball action/skill is being performed?
                2. TECHNIQUE: Analyze the form, posture, and execution
                3. IMPROVEMENT: What specific improvements can be made?
                4. ENCOURAGEMENT: Provide motivational coaching advice
                
                Focus on:
                - Shooting form (if applicable)
                - Footwork and balance
                - Body positioning
                - Ball handling technique
                - Defensive stance
                - Court awareness
                
                Respond in this exact JSON format:
                {{
                    "action": "Brief description of the basketball action",
                    "feedback": "Detailed coaching feedback with specific improvements",
                    "timestamp": {frame_data['timestamp']},
                    "commentary_type": "technical"
                }}
                
                Keep feedback professional, constructive, and actionable.
                """
                
                # Generate content with image
                response = model.generate_content([prompt, image])
                
                # Try to parse JSON response
                try:
                    import re
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                    if json_match:
                        response_json = json.loads(json_match.group())
                        response_json['timestamp'] = frame_data['timestamp']
                        commentary_events.append(response_json)
                    else:
                        # Fallback if JSON parsing fails
                        commentary_events.append({
                            "action": f"Basketball analysis at {frame_data['timestamp']:.1f}s",
                            "feedback": response.text[:200] + "...",
                            "timestamp": frame_data['timestamp'],
                            "commentary_type": "technical"
                        })
                except json.JSONDecodeError:
                    # Create structured response from raw text
                    commentary_events.append({
                        "action": f"Basketball action at {frame_data['timestamp']:.1f}s",
                        "feedback": response.text[:300],
                        "timestamp": frame_data['timestamp'],
                        "commentary_type": "technical"
                    })
                
            except Exception as e:
                print(f"Error analyzing frame {i}: {e}")
                # Add fallback commentary
                fallback_comments = [
                    {
                        "action": "Basketball fundamentals focus",
                        "feedback": "Keep your shooting form consistent - elbow under the ball, follow through with your wrist snap!",
                        "timestamp": frame_data['timestamp'],
                        "commentary_type": "technical"
                    },
                    {
                        "action": "Defensive positioning",
                        "feedback": "Stay low in your defensive stance, keep your feet moving and hands active!",
                        "timestamp": frame_data['timestamp'],
                        "commentary_type": "tactical"
                    },
                    {
                        "action": "Ball handling technique",
                        "feedback": "Great dribbling! Keep your head up to see the court and protect the ball with your off-hand.",
                        "timestamp": frame_data['timestamp'],
                        "commentary_type": "technical"
                    }
                ]
                commentary_events.append(fallback_comments[i % len(fallback_comments)])
                continue
        
        return commentary_events
        
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        # Return fallback commentary
        return [
            {
                "action": "Basketball shooting analysis",
                "feedback": "Focus on your shooting form - keep your elbow aligned and follow through completely!",
                "timestamp": 2.0,
                "commentary_type": "technical"
            },
            {
                "action": "Court movement",
                "feedback": "Great hustle! Keep moving your feet and stay ready for the next play.",
                "timestamp": 5.0,
                "commentary_type": "motivational"
            },
            {
                "action": "Ball control",
                "feedback": "Nice ball handling! Work on keeping your head up to see passing opportunities.",
                "timestamp": 8.0,
                "commentary_type": "technical"
            }
        ]

def process_video_with_commentary(video_path, api_key, session_id):
    """Process video and generate commentary"""
    try:
        processing_status[session_id] = {"status": "processing", "progress": 0}
        
        # Extract video info
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        cap.release()
        
        video_info = {
            'fps': fps,
            'width': width,
            'height': height,
            'duration': duration,
            'total_frames': total_frames
        }
        
        processing_status[session_id]["progress"] = 20
        
        # Extract frames for AI analysis
        frames = extract_frames_for_analysis(video_path, max_frames=8)
        processing_status[session_id]["progress"] = 40
        
        # Generate AI commentary
        commentary_events = []
        if api_key:
            commentary_events = analyze_basketball_video_with_gemini(api_key, frames, video_info)
        else:
            # Fallback commentary without API
            commentary_events = [
                {
                    "action": "Basketball shooting form analysis",
                    "feedback": "Focus on your shooting form - keep your elbow under the ball and follow through!",
                    "timestamp": 2.0,
                    "commentary_type": "technical"
                },
                {
                    "action": "Defensive positioning",
                    "feedback": "Great defensive stance! Stay low and keep your hands active.",
                    "timestamp": 5.0,
                    "commentary_type": "tactical"
                },
                {
                    "action": "Ball handling skills",
                    "feedback": "Nice dribbling! Try to keep your head up to see the court better.",
                    "timestamp": 8.0,
                    "commentary_type": "technical"
                }
            ]
        
        processing_status[session_id]["progress"] = 70
        
        # Process video with overlays
        output_path = process_video_with_overlays(video_path, commentary_events, session_id)
        
        processing_status[session_id] = {
            "status": "completed",
            "progress": 100,
            "output_path": output_path,
            "commentary": commentary_events,
            "video_info": video_info
        }
        
    except Exception as e:
        processing_status[session_id] = {"status": "error", "error": str(e)}

def process_video_with_overlays(video_path, commentary_events, session_id):
    """Add commentary overlays to video"""
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    output_filename = f"analyzed_{session_id}.mp4"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    current_commentary = None
    commentary_end_frame = 0
    
    # Convert commentary timestamps to frame numbers
    for event in commentary_events:
        event['frame_number'] = int(event['timestamp'] * fps)
        event['end_frame'] = event['frame_number'] + (3 * fps)  # Show for 3 seconds
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Check for new commentary
        for event in commentary_events:
            if event['frame_number'] == frame_count:
                current_commentary = event
                commentary_end_frame = event['end_frame']
        
        # Clear commentary if expired
        if frame_count > commentary_end_frame:
            current_commentary = None
        
        # Add commentary overlay
        if current_commentary:
            # Background for text
            overlay = frame.copy()
            cv2.rectangle(overlay, (20, height - 150), (width - 20, height - 20), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # Add commentary text
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_lines = [
                f"🏀 {current_commentary['action']}",
                f"💡 {current_commentary['feedback']}"
            ]
            
            y_offset = height - 120
            for line in text_lines:
                # Wrap long text
                if len(line) > 60:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + word) < 60:
                            current_line += word + " "
                        else:
                            cv2.putText(frame, current_line, (30, y_offset), font, 0.6, (255, 255, 255), 2)
                            y_offset += 25
                            current_line = word + " "
                    if current_line:
                        cv2.putText(frame, current_line, (30, y_offset), font, 0.6, (255, 255, 255), 2)
                        y_offset += 25
                else:
                    cv2.putText(frame, line, (30, y_offset), font, 0.6, (255, 255, 255), 2)
                    y_offset += 25
        
        # Add progress indicator
        progress_width = int((frame_count / int(cap.get(cv2.CAP_PROP_FRAME_COUNT))) * width)
        cv2.rectangle(frame, (0, 0), (progress_width, 5), (0, 255, 0), -1)
        
        out.write(frame)
        frame_count += 1
        
        # Update processing progress
        if session_id in processing_status:
            progress = 70 + (frame_count / int(cap.get(cv2.CAP_PROP_FRAME_COUNT))) * 30
            processing_status[session_id]["progress"] = min(100, progress)
    
    cap.release()
    out.release()
    
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    api_key = request.form.get('api_key', '')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        session_id = str(int(time.time()))
        filename = f"{session_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Start processing in background
        thread = threading.Thread(
            target=process_video_with_commentary,
            args=(filepath, api_key, session_id)
        )
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': 'Video uploaded successfully. Processing started.'
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/status/<session_id>')
def get_status(session_id):
    if session_id in processing_status:
        return jsonify(processing_status[session_id])
    return jsonify({'error': 'Session not found'}), 404

@app.route('/download/<session_id>')
def download_video(session_id):
    if session_id in processing_status and processing_status[session_id]['status'] == 'completed':
        output_path = processing_status[session_id]['output_path']
        filename = os.path.basename(output_path)
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)
    return jsonify({'error': 'Video not ready or session not found'}), 404

@app.route('/preview/<session_id>')
def preview_video(session_id):
    if session_id in processing_status and processing_status[session_id]['status'] == 'completed':
        output_path = processing_status[session_id]['output_path']
        filename = os.path.basename(output_path)
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    return jsonify({'error': 'Video not ready or session not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)