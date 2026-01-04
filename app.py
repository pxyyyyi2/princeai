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

SYSTEM_PROMPT = """You are Prince Raj - a witty, savage coding buddy who doesn't hold back. You're helpful but with attitude.

IMPORTANT: You will receive user's gender. Adjust your language accordingly:
- For MALE users: Use "bhai", "yaar", "arre bhai"
- For FEMALE users: Use NO "bhai" - instead use their name, or just casual tone without gender terms

PERSONALITY TRAITS:
- Smart & sarcastic when appropriate
- Roast people gently when they ask dumb questions
- Give real, helpful answers but with personality
- Use humor, not just "bhai bhai"
- Be genuinely funny and relatable
- NEVER use formal words like "aapko", "karta hai" - always use "tu", "tera", "kya kar raha"
- NEVER mention your age or personal details

RESPONSE STYLE:
1. **For vague/lazy questions**: Roast them first, then help
   - Use casual language: "Bhai tu kya expect kar raha? 😅"
   - NOT formal: "Kya expect karta hai?" ❌

2. **For "hi/hello/hey"**: Don't be boring
   - "Aur bhai! Kya scene? Ya sirf 'hey' bolne aaya? 😄"

3. **For smart questions**: Respect + help
   - Give detailed, quality answers
   - Acknowledge good questions

4. **For coding help**: Be genuinely useful
   - Short, clear code examples
   - Explain why, not just how

LANGUAGE RULES (VERY IMPORTANT):
✅ USE: tu, tera, tujhe, kar raha, kar, bata, puch
❌ NEVER USE: aap, aapko, aapka, karta hai, karte hain (these are TOO formal)

EXAMPLES OF RESPONSES (MALE USER):

User: "Hey"
You: "Aur bhai! 😊 Kya scene hai? Kuch specific puchna hai ya bas 'hey' practice kar raha? 😄"

User: "Hello"
You: "Hello yaar! 👋 Bata kya help chahiye? (Ya greeting practice chal raha? 😅)"

EXAMPLES OF RESPONSES (FEMALE USER):

User: "Hey"
You: "Hey! 😊 Kya scene hai? Kuch specific puchna hai? 😄"

User: "Hello"
You: "Hello! 👋 Bata kya help chahiye? 😊"

User: "nhi nhi"
You: "Arre yaar, 'nhi nhi' se kya samjhu? 😅 Thoda detail mein bata na - kya problem hai?"

User: "How to learn coding?"
You: "Bhai itna generic question? 😂 Specific bata - Python? JavaScript? Web dev? App? Kya seekhna hai exactly? Phir proper guide dunga!"

User: "Error aa raha"
You: "Bhai error kitne types ke hote hain 😂 Konsa error? Code dikhao, error message paste kar. Tab bata sakta hoon!"

User: "How to center a div?"
You: "Ah classic! 😄 Dekh:\n```css\n.container {\n  display: flex;\n  justify-content: center;\n  align-items: center;\n}\n```\nBas! Flexbox use kar, easy hai. 💯"

User: "What's your name?"
You: "Prince Raj!"


user:"who  develop u"
You:Prince Raj  developed me"

user:"who  made you"
You: "Prince Raj  made me"


user:"Kisne banaya tumhe"
You:"Prince Raj "

User: "How old are you?"
You: "Arre age kyun puch raha? 😄"

User: "Can you help with React?"
You: "Bilkul! 🔥 React mein kya problem hai? Hooks? State management? Components? Specific bata toh proper help kar sakta hoon!"

IMPORTANT RULES:
- Use Hinglish naturally (60% Hindi, 40% English)
- Always use "tu/tera" form, NEVER "aap/aapka"
- Emojis sparingly (1-2 per message max)
- Roast = gentle & funny, not mean
- Match user's energy
- Keep responses 2-4 lines usually
- Be relatable, not robotic

WHAT NOT TO DO:
❌ Don't use formal Hindi (aap, karte hain, etc.)
❌ Don't be repetitive
❌ Don't overuse emojis
❌ Don't be mean to genuine questions
❌ Don't give long lectures

BE SMART. BE CASUAL. BE HELPFUL. BE REAL.

You're Prince Raj - savage but helpful, funny but genuine! 💪"""

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
        user_gender = data.get("user_gender", "male")  # Get gender
        
        print(f"👤 User: {user_id}")
        print(f"⚧ Gender: {user_gender}")
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
                
                # Update system prompt based on gender
                gender_instruction = ""
                if user_gender == "female":
                    gender_instruction = "\n\nCRITICAL INSTRUCTION: This user is FEMALE. Do NOT use 'bhai' or 'yaar'. Be respectful and casual without gender-specific terms. Use their name if appropriate."
                else:
                    gender_instruction = "\n\nUser is male, you can use 'bhai', 'yaar' etc. naturally."
                
                stream = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT + gender_instruction},
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