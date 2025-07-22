# MedAI - Medical AI Chatbot

A responsive medical AI chatbot built with React, TypeScript, and FastAPI, featuring conversation storage and support for both local AI models and ChatGPT.

## 🚀 Features

- **🤖 Dual AI Models**: Support for both local BioMedLM and ChatGPT
- **💬 Conversation Storage**: Persistent chat history with PostgreSQL
- **📱 Responsive Design**: Works perfectly on mobile, tablet, and desktop
- **🎨 Modern UI**: Clean, intuitive interface with Tailwind CSS
- **⚡ Real-time Chat**: Instant responses with loading indicators
- **🔒 Environment-based Configuration**: Easy switching between models

## 🏗️ Architecture

### Frontend

- **React 18** with TypeScript
- **Tailwind CSS** for responsive styling
- **Axios** for API communication
- **Lucide React** for icons

### Backend

- **FastAPI** with Python
- **PostgreSQL** for conversation storage
- **SQLAlchemy** ORM
- **Transformers** for local AI models
- **OpenAI API** for ChatGPT integration

### AI Models

- **Local Model**: Microsoft DialoGPT-medium (default)
- **ChatGPT**: OpenAI GPT-3.5-turbo (optional)

## 🛠️ Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Docker (for PostgreSQL)
- OpenAI API key (optional, for ChatGPT)

### 1. Clone and Install

```bash
git clone <repository-url>
cd medAi
npm install
cd backend
pip install -r requirements.txt
```

### 2. Set Up Database

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Wait for database to be ready, then run setup
python setup_db.py
```

### 3. Configure Environment

```bash
# Copy configuration
cp config.env backend/.env

# Edit backend/.env to customize settings
```

### 4. Start the Application

```bash
# From project root
npm start
```

The app will be available at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

#### Database Configuration

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/medai_chatbot
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=medai_chatbot
```

#### AI Model Configuration

```env
# Local Model Settings
MODEL_NAME=microsoft/DialoGPT-medium
MODEL_MAX_LENGTH=200
MODEL_TEMPERATURE=0.7
MODEL_DEVICE=auto

# OpenAI/ChatGPT Settings (Optional)
OPENAI_ENABLED=false
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### Switching Between Models

#### Using Local Model (Default)

```env
OPENAI_ENABLED=false
```

#### Using ChatGPT

```env
OPENAI_ENABLED=true
OPENAI_API_KEY=your_actual_api_key
OPENAI_MODEL=gpt-3.5-turbo
```

## 🤖 AI Model Features

### Local Model (BioMedLM/DialoGPT)

- ✅ **No API costs** - runs completely locally
- ✅ **Privacy-focused** - no data sent to external services
- ✅ **Offline capability** - works without internet
- ✅ **Customizable** - can be fine-tuned for specific medical domains

### ChatGPT Integration

- ✅ **Advanced responses** - more sophisticated medical knowledge
- ✅ **Better context understanding** - improved conversation flow
- ✅ **Latest medical information** - up-to-date knowledge base
- ✅ **Professional medical tone** - appropriate for healthcare context

## 📱 Responsive Design

The application is fully responsive and optimized for:

### Mobile (< 640px)

- Slide-out sidebar with overlay
- Touch-friendly buttons and inputs
- Compact message layout
- Auto-close sidebar on conversation selection

### Tablet (641px - 1024px)

- Hybrid layout with responsive sidebar
- Balanced spacing and typography
- Optimized for touch and mouse interaction

### Desktop (> 1024px)

- Fixed sidebar always visible
- Maximum content area utilization
- Enhanced typography and spacing
- Full desktop experience

## 🔄 API Endpoints

### Chat

- `POST /chat` - Send a message and get AI response

### Conversations

- `GET /conversations` - Get all conversations
- `GET /conversations/{id}` - Get specific conversation
- `DELETE /conversations/{id}` - Delete conversation

### Health

- `GET /health` - Check API health and model status

## 🛡️ Security & Privacy

### Data Protection

- All conversations stored locally in PostgreSQL
- No data sent to external services (unless using ChatGPT)
- Environment-based configuration for sensitive data

### Medical Disclaimer

- All responses include appropriate medical disclaimers
- Users are reminded to consult healthcare professionals
- Educational purposes only

## 🚀 Development

### Frontend Development

```bash
npm start          # Start development server
npm run build      # Build for production
npm test           # Run tests
```

### Backend Development

```bash
cd backend
python start.py    # Start with auto-reload
```

### Database Management

```bash
python setup_db.py # Initialize database
```

## 🐛 Troubleshooting

### Common Issues

#### Port Conflicts

```bash
# Check what's using ports 3000 and 8000
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

#### Database Connection Issues

```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check database status
docker-compose ps
```

#### Model Loading Issues

```bash
# Clear model cache
rm -rf ~/.cache/huggingface/

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### OpenAI Configuration

```bash
# Run setup script
./setup_openai.sh  # Linux/Mac
setup_openai.bat   # Windows
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:

- Check the troubleshooting section
- Review the API documentation at `/docs`
- Open an issue on GitHub

---

**⚠️ Medical Disclaimer**: This application provides general medical information for educational purposes only. Always consult with qualified healthcare professionals for medical advice, diagnosis, and treatment.
