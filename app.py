from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, send_from_directory, Response
import json
import os
from datetime import datetime
import traceback

# Test Groq import
print("\n" + "="*60)
print("🔍 TESTING GROQ IMPORT...")
print("="*60)

try:
    from groq import Groq
    print("✅ Groq imported successfully!")
    GROQ_AVAILABLE = True
except Exception as e:
    print(f"❌ Groq import FAILED: {e}")
    print("Run: pip install groq")
    GROQ_AVAILABLE = False

app = Flask(__name__, static_folder="frontend", static_url_path="")

# Test API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print(f"\n🔑 API Key: {GROQ_API_KEY[:20]}...{GROQ_API_KEY[-10:]}")
print(f"📏 Key Length: {len(GROQ_API_KEY)} characters")

# Initialize Groq
client = None
if GROQ_AVAILABLE:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq client initialized!")
        
        # Test API call
        print("\n🧪 Testing Groq API with simple call...")
        test_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        print(f"✅ API Test Success! Response: {test_response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Groq client initialization FAILED: {e}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        client = None

print("="*60 + "\n")

# Create logs directory
if not os.path.exists('chat_logs'):
    os.makedirs('chat_logs')

SYSTEM_PROMPT = SYSTEM_PROMPT = """
You are Prince Raj, a friendly buddy who talks naturally in Hinglish.

IMPORTANT IDENTITY:
- Your name is Prince Raj
- When asked "who are you" or "tum kaun ho", just say "Main Prince Raj hoon " 
- Keep it simple and natural
- Don't give long explanations about yourself

SPECIAL KNOWLEDGE:
- If someone named Nikhil asks "aaj kitne baje niklega" or similar timing questions, reply: "5:15 pe bhai! Kitni baar puchega? 😄 Hamesha same time pe hi nikalte hain!"
- Keep responses short, fun and natural

HOW YOU TALK:
- Talk like a close friend - casual and natural
- Mix Hindi and English naturally: yaar, dekh, haan, arre, bas, bilkul
- Keep it short and sweet (1-3 sentences usually)
- Use emojis sometimes 🚀💡✨
- Never introduce yourself unless asked
- Just chat normally like friends do
- Don't be too philosophical or give life advice unless asked
- Keep it light and fun

FOR CODING QUESTIONS:
- Give simple examples with brief explanations
- Use phrases like "Dekh", "Arre simple hai", "Bas yeh kar"
- Keep code examples clean and short

FOR CASUAL CHAT:
- Just respond naturally like a friend
- Don't overthink responses
- Be chill and supportive
- Use humor when appropriate

EXAMPLES:
User: "tum kaun ho"
You: "Main Prince Raj hoon! 😊"

User: "who are you"
You: "Prince Raj"

User: "hello"
You: "hello"

User: "what's up"
You: "Bas mast! Tu bata? 🔥"

User: "aaj kitne baje niklega" (if from Nikhil)
You: "5:15 pe bhai! Kitni baar puchega? 😄"

User: "bore ho raha"
You: "Arre yaar, kuch kar le - movie dekh ya game khel 😄"

User: "How to use loops?"
You: "Arre dekh, for loop simple hai. `for i in range(5):` likh, 0 se 4 tak print hoga. Bas! 💡"

Be natural, be friendly, be real! Don't overthink - just be a chill friend.
"""

@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")

@app.route("/logs")
def logs_page():
    return send_from_directory("frontend", "logs.html")

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "groq_available": GROQ_AVAILABLE,
        "client_initialized": client is not None
    })

@app.route("/chat", methods=["POST"])
def chat():
    print("\n" + "🔵"*30)
    print("📨 NEW CHAT REQUEST")
    print("🔵"*30)
    
    if not GROQ_AVAILABLE:
        error_msg = "Groq library not installed. Run: pip install groq"
        print(f"❌ {error_msg}")
        return jsonify({"error": error_msg}), 500
    
    if client is None:
        error_msg = "Groq client not initialized. Check API key."
        print(f"❌ {error_msg}")
        return jsonify({"error": error_msg}), 500
    
    try:
        data = request.get_json()
        user_msg = data.get("message", "")
        user_id = data.get("user_id", "anonymous")
        
        print(f"👤 User: {user_id}")
        print(f"💬 Message: {user_msg}")
        
        if not user_msg:
            print("❌ Empty message")
            return jsonify({"error": "No message provided"}), 400

        log_chat(user_id, "user", user_msg)

        def generate():
            bot_response = ""
            try:
                print("🤖 Starting Groq API call...")
                print(f"📡 Model: llama-3.1-8b-instant")
                
                stream = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg}
                    ],
                    stream=True,
                    temperature=0.7,
                    max_tokens=512
                )
                
                print("✅ Stream created, waiting for chunks...")
                chunk_count = 0
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        bot_response += content
                        chunk_count += 1
                        yield f"data: {json.dumps({'content': content})}\n\n"
                
                print(f"✅ Streaming complete! Chunks: {chunk_count}")
                print(f"📝 Response: {bot_response[:100]}...")
                
                log_chat(user_id, "bot", bot_response)
                yield f"data: {json.dumps({'done': True})}\n\n"
                            
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                print(f"\n❌ ERROR IN GENERATE:")
                print(f"Error: {error_msg}")
                traceback.print_exc()
                
                log_chat(user_id, "error", error_msg)
                yield f"data: {json.dumps({'error': error_msg})}\n\n"

        return Response(generate(), mimetype='text/event-stream')
    
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n❌ ERROR IN CHAT ROUTE:")
        print(f"Error: {error_msg}")
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500

@app.route("/models", methods=["GET"])
def get_models():
    return jsonify({
        "models": [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768"
        ]
    })

def log_chat(user_id, sender, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = f"chat_logs/chat_{date_str}.txt"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{user_id}] [{sender}]: {message}\n")
            f.write("-" * 80 + "\n")
    except Exception as e:
        print(f"❌ Log write failed: {e}")

@app.route("/view_logs", methods=["GET"])
def view_logs():
    try:
        date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
        log_file = f"chat_logs/chat_{date}.txt"
        
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                logs = f.read()
            return jsonify({"logs": logs, "date": date})
        else:
            return jsonify({"logs": "No logs found for this date", "date": date})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logs_list", methods=["GET"])
def logs_list():
    try:
        if os.path.exists('chat_logs'):
            files = [f for f in os.listdir('chat_logs') if f.endswith('.txt')]
            files.sort(reverse=True)
            return jsonify({"files": files})
        return jsonify({"files": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n" + "🚀"*30)
    print("STARTING PRINCE AI SERVER")
    print("🚀"*30)
    print(f"📍 URL: http://localhost:5000")
    print(f"🔧 Debug Mode: ON")
    print(f"✅ Groq: {'Available' if GROQ_AVAILABLE else 'Not Available'}")
    print(f"✅ Client: {'Initialized' if client else 'Not Initialized'}")
    print("🚀"*30 + "\n")
    
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)