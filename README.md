# AI Basketball Coach - Web Application

🏀 **Professional basketball video analysis powered by AI and computer vision**

Transform your basketball videos into professional coaching sessions with real-time AI commentary, technique analysis, and actionable feedback.

## ✨ Features

- **🎥 Video Upload**: Easy drag-and-drop video upload interface
- **🤖 AI Analysis**: Powered by Google Gemini AI for intelligent basketball analysis
- **📊 Real-time Processing**: Live progress tracking with visual feedback
- **💡 Smart Commentary**: Professional coaching insights overlaid on your video
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🔧 Technical Analysis**: Detailed form analysis for shooting, dribbling, and defense
- **🎯 Actionable Feedback**: Specific improvements and coaching tips

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenCV (cv2)
- Flask
- Google Generative AI (Gemini)

### Installation

1. **Install Dependencies**
```bash
pip install flask flask-cors google-generativeai opencv-python pillow numpy
```

2. **Run the Application**
```bash
python app.py
```

3. **Open Your Browser**
Navigate to: `http://localhost:5000`

## 🔑 API Key Setup

### Option 1: With Gemini API Key (Recommended)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a free API key
3. Enter your API key in the web interface
4. Get enhanced AI-powered basketball analysis

### Option 2: Without API Key
- The app works without an API key using fallback commentary
- You'll still get video processing and basic feedback
- Consider getting an API key for the full AI experience

## 🎬 How It Works

### 1. Upload Your Video
- **Supported formats**: MP4, AVI, MOV, MKV
- **Max file size**: 100MB
- **Drag & drop** or click to browse

### 2. AI Analysis Process
1. **Frame Extraction**: Key frames are extracted from your video
2. **AI Processing**: Gemini AI analyzes basketball techniques and form
3. **Commentary Generation**: Professional coaching feedback is generated
4. **Video Enhancement**: Commentary is overlaid on your original video

### 3. Get Your Results
- **Enhanced Video**: Download your video with AI commentary overlays
- **Coaching Insights**: View detailed feedback and improvement tips
- **Technical Analysis**: Get specific advice on form and technique

## 🏀 What Gets Analyzed

### Shooting Form
- Elbow alignment
- Follow-through technique
- Balance and footwork
- Release point consistency

### Ball Handling
- Dribbling technique
- Ball protection
- Court vision
- Hand positioning

### Defense
- Defensive stance
- Footwork
- Hand activity
- Positioning

### Movement
- Court awareness
- Hustle and effort
- Transition play
- Team positioning

## 🛠️ Technical Details

### Architecture
- **Backend**: Flask web framework
- **AI Engine**: Google Gemini 1.5 Flash
- **Video Processing**: OpenCV (cv2)
- **Frontend**: Modern HTML5/CSS3/JavaScript
- **File Handling**: Secure upload with validation

### Processing Pipeline
1. **Upload Validation**: File type and size checking
2. **Frame Sampling**: Intelligent frame extraction (8-10 key frames)
3. **AI Analysis**: Each frame analyzed by Gemini AI
4. **Commentary Synthesis**: Coaching feedback generated
5. **Video Overlay**: Professional text overlays added
6. **Output Generation**: Final MP4 video created

### Security Features
- File type validation
- Size limits (100MB max)
- Secure filename handling
- Session-based processing
- CORS protection

## 📱 User Interface

### Modern Design
- **Clean Interface**: Professional basketball-themed design
- **Progress Tracking**: Real-time processing updates
- **Responsive Layout**: Works on all devices
- **Drag & Drop**: Intuitive file upload
- **Visual Feedback**: Clear status indicators

### Processing Steps
1. 🏀 **Video Upload** - Secure file transfer
2. 👁️ **Frame Analysis** - AI examines key moments
3. 💬 **AI Commentary** - Professional feedback generation
4. 🎥 **Video Processing** - Final video creation

## 🔧 Configuration

### Environment Variables (Optional)
```bash
export GEMINI_API_KEY="your-api-key-here"
export FLASK_ENV="development"
export MAX_CONTENT_LENGTH="104857600"  # 100MB
```

### File Structure
```
basketball-ai-coach/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── app.js        # Frontend logic
├── uploads/              # Temporary video storage
├── outputs/              # Processed video output
└── README_webapp.md      # This file
```

## 🚀 Deployment

### Local Development
```bash
python app.py
# Access at http://localhost:5000
```

### Production Deployment
For production deployment, consider:
- **Gunicorn** or **uWSGI** as WSGI server
- **Nginx** as reverse proxy
- **SSL certificate** for HTTPS
- **Environment variables** for API keys
- **File cleanup** for temporary uploads

## 🎯 Use Cases

### For Players
- **Skill Development**: Get professional feedback on your technique
- **Form Analysis**: Identify and correct shooting/dribbling issues
- **Progress Tracking**: Compare videos over time
- **Self-Coaching**: Learn without needing a human coach

### For Coaches
- **Player Analysis**: Detailed breakdown of player performance
- **Teaching Tool**: Visual feedback for instruction
- **Team Development**: Analyze team plays and positioning
- **Recruitment**: Evaluate player potential

### For Teams
- **Game Analysis**: Break down game footage
- **Training Enhancement**: Supplement practice with AI insights
- **Skill Assessment**: Objective performance evaluation
- **Development Planning**: Data-driven improvement strategies

## 🔍 Troubleshooting

### Common Issues

**Video Upload Fails**
- Check file size (max 100MB)
- Verify file format (MP4, AVI, MOV, MKV)
- Ensure stable internet connection

**Processing Stuck**
- Refresh the page and try again
- Check browser console for errors
- Verify API key if using Gemini

**Poor Analysis Quality**
- Use well-lit videos
- Ensure clear view of player
- Avoid shaky camera work
- Use higher resolution when possible

## 📊 Performance

### Processing Times
- **Small videos** (< 10MB): 30-60 seconds
- **Medium videos** (10-50MB): 1-3 minutes
- **Large videos** (50-100MB): 3-5 minutes

### Optimization Tips
- **Trim videos** to key moments for faster processing
- **Good lighting** improves AI analysis accuracy
- **Stable camera** work provides better results
- **Close-up shots** allow more detailed analysis

## 🤝 Contributing

This basketball AI coach represents the future of sports training technology. The combination of computer vision and AI provides unprecedented insights into basketball performance.

## 📄 License

Built with ❤️ for the basketball community. Powered by Google Gemini AI and OpenCV.

---

**Ready to revolutionize your basketball training? Upload your first video and experience AI-powered coaching!** 🏀🚀
