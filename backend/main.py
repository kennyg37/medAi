from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import asyncio
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MedAI Chatbot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/medai_chatbot")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class ConversationDB(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MessageDB(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class Message(BaseModel):
    role: str
    content: str
    timestamp: str

class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    disclaimer: str

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BioMedLMModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = os.getenv("MODEL_DEVICE", "auto")
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()

    def load_model(self):
        try:
            logger.info("Loading medical AI model...")
            # Using a reliable model for medical Q&A
            model_name = os.getenv("MODEL_NAME", "microsoft/DialoGPT-medium")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            )
            self.model.to(self.device)
            logger.info(f"Medical model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Fallback to a simpler approach
            self.model = None

    def generate_response(self, prompt: str, max_length: int = None) -> str:
        if not max_length:
            max_length = int(os.getenv("MODEL_MAX_LENGTH", "200"))

        if not self.model or not self.tokenizer:
            return self._fallback_response(prompt)

        try:
            # Simple conversational prompt format
            medical_prompt = f"""You are a helpful medical AI assistant. Answer medical questions clearly and informatively.

User: {prompt}
Assistant:"""
            
            inputs = self.tokenizer.encode(medical_prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=max_length,
                    temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")),
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    attention_mask=torch.ones_like(inputs)
                )
            
            # Decode the generated tokens (only the new ones)
            generated_tokens = outputs[0][len(inputs[0]):]
            response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
            
            # If response is empty or too short, use fallback
            if not response or len(response) < 10:
                return self._fallback_response(prompt)
            
            # Return response without medical disclaimer
            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when model is not available"""
        responses = {
            "cancer": "The main causes of cancer include genetic factors, environmental exposures (like tobacco, radiation, chemicals), lifestyle factors (diet, physical inactivity), and infections. Risk factors vary by cancer type. Early detection through screening is important.",
            "diabetes": "Diabetes is caused by insufficient insulin production (Type 1) or insulin resistance (Type 2). Risk factors include genetics, obesity, poor diet, physical inactivity, and age. Type 2 diabetes is largely preventable through lifestyle changes.",
            "depression": "Depression can be caused by biological factors (brain chemistry, genetics), psychological factors (trauma, stress), and environmental factors (life events, social isolation). It's a treatable medical condition.",
            "symptoms": "I understand you're asking about symptoms. While I can provide general information, it's important to consult with a healthcare professional for proper diagnosis and treatment.",
            "medication": "For medication questions, please consult with a pharmacist or healthcare provider as they can provide personalized advice based on your specific situation.",
            "emergency": "If you're experiencing a medical emergency, please call emergency services immediately (911 in the US).",
            "general": "I'm here to provide general medical information, but please remember to consult with healthcare professionals for personalized medical advice."
        }
        
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["cancer", "tumor", "malignant"]):
            return responses["cancer"]
        elif any(word in prompt_lower for word in ["diabetes", "blood sugar", "insulin"]):
            return responses["diabetes"]
        elif any(word in prompt_lower for word in ["depression", "mental health", "mood"]):
            return responses["depression"]
        elif any(word in prompt_lower for word in ["symptom", "pain", "hurt", "ache"]):
            return responses["symptoms"]
        elif any(word in prompt_lower for word in ["medication", "drug", "pill", "medicine"]):
            return responses["medication"]
        elif any(word in prompt_lower for word in ["emergency", "urgent", "critical"]):
            return responses["emergency"]
        else:
            return responses["general"]

class ChatGPTModel:
    def __init__(self):
        self.client = None
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.load_client()

    def load_client(self):
        try:
            if not self.api_key:
                logger.error("OpenAI API key not found")
                return
            
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"ChatGPT client initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing ChatGPT client: {e}")
            self.client = None

    def generate_response(self, prompt: str, max_length: int = None) -> str:
        if not self.client:
            return self._fallback_response(prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical AI assistant. Provide brief, concise medical information. Keep responses short - 1-2 sentences maximum. Be direct and to the point. Always remind users to consult healthcare professionals for serious concerns."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=50,  # Very short responses
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating ChatGPT response: {e}")
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when ChatGPT is not available"""
        return "I'm sorry, I'm having trouble connecting right now. Please consult a healthcare professional for medical advice."

# Initialize models
biomedlm = BioMedLMModel()
chatgpt = ChatGPTModel()

# Check which model to use
USE_OPENAI = os.getenv("OPENAI_ENABLED", "false").lower() == "true"

def get_active_model():
    """Get the active model based on environment configuration"""
    if USE_OPENAI and chatgpt.client:
        logger.info("Using ChatGPT model")
        return chatgpt
    else:
        logger.info("Using local BioMedLM model")
        return biomedlm

# Database functions
def save_conversation(conversation: Conversation, db: Session):
    # Save conversation
    conv_db = ConversationDB(
        id=conversation.id,
        title=conversation.title,
        created_at=datetime.fromisoformat(conversation.created_at.replace('Z', '+00:00')),
        updated_at=datetime.fromisoformat(conversation.updated_at.replace('Z', '+00:00'))
    )
    db.merge(conv_db)
    
    # Save messages
    for message in conversation.messages:
        msg_db = MessageDB(
            conversation_id=conversation.id,
            role=message.role,
            content=message.content,
            timestamp=datetime.fromisoformat(message.timestamp.replace('Z', '+00:00'))
        )
        db.add(msg_db)
    
    db.commit()

def get_conversation(conversation_id: str, db: Session) -> Optional[Conversation]:
    conv_db = db.query(ConversationDB).filter(ConversationDB.id == conversation_id).first()
    if not conv_db:
        return None
    
    messages_db = db.query(MessageDB).filter(MessageDB.conversation_id == conversation_id).order_by(MessageDB.timestamp).all()
    
    messages = [
        Message(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp.isoformat()
        )
        for msg in messages_db
    ]
    
    return Conversation(
        id=conv_db.id,
        title=conv_db.title,
        messages=messages,
        created_at=conv_db.created_at.isoformat(),
        updated_at=conv_db.updated_at.isoformat()
    )

def get_all_conversations(db: Session) -> List[Conversation]:
    conversations_db = db.query(ConversationDB).order_by(ConversationDB.updated_at.desc()).all()
    conversations = []
    
    for conv_db in conversations_db:
        messages_db = db.query(MessageDB).filter(MessageDB.conversation_id == conv_db.id).order_by(MessageDB.timestamp).all()
        
        messages = [
            Message(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp.isoformat()
            )
            for msg in messages_db
        ]
        
        conversations.append(Conversation(
            id=conv_db.id,
            title=conv_db.title,
            messages=messages,
            created_at=conv_db.created_at.isoformat(),
            updated_at=conv_db.updated_at.isoformat()
        ))
    
    return conversations

# API endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Get the active model
        active_model = get_active_model()
        
        # Generate response
        response_text = active_model.generate_response(request.message)
        
        # Create conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create or update conversation
        conversation = get_conversation(conversation_id, db)
        
        user_message = Message(
            role="user",
            content=request.message,
            timestamp=datetime.now().isoformat()
        )
        
        assistant_message = Message(
            role="assistant",
            content=response_text,
            timestamp=datetime.now().isoformat()
        )
        
        if conversation:
            # Update existing conversation
            conversation.messages.extend([user_message, assistant_message])
            conversation.updated_at = datetime.now().isoformat()
        else:
            # Create new conversation
            conversation = Conversation(
                id=conversation_id,
                title=request.message[:50] + ("..." if len(request.message) > 50 else ""),
                messages=[user_message, assistant_message],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        
        save_conversation(conversation, db)
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            disclaimer="" # Removed disclaimer
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/conversations", response_model=List[Conversation])
async def get_conversations(db: Session = Depends(get_db)):
    try:
        return get_all_conversations(db)
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation_endpoint(conversation_id: str, db: Session = Depends(get_db)):
    try:
        conversation = get_conversation(conversation_id, db)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    try:
        # Delete messages first
        db.query(MessageDB).filter(MessageDB.conversation_id == conversation_id).delete()
        # Delete conversation
        db.query(ConversationDB).filter(ConversationDB.id == conversation_id).delete()
        db.commit()
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "openai_enabled": USE_OPENAI}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 