from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, send_from_directory, Response
import json
import os
from datetime import datetime
import traceback

# ============================================================
# GROQ IMPORT
# ============================================================

print("\n" + "=" * 60)
print("🔍 TESTING GROQ IMPORT...")
print("=" * 60)

try:
    from groq import Groq
    print("✅ Groq imported successfully!")
    GROQ_AVAILABLE = True
except Exception as e:
    print(f"❌ Groq import FAILED: {e}")
    print("Run: pip install groq")
    GROQ_AVAILABLE = False


# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)


# ============================================================
# GROQ API KEY
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY is missing!")
    print("Create a .env file and add:")
    print("GROQ_API_KEY=your_key_here")
else:
    print(
        f"\n🔑 API Key: "
        f"{GROQ_API_KEY[:8]}...{GROQ_API_KEY[-4:]}"
    )
    print(f"📏 Key Length: {len(GROQ_API_KEY)} characters")


# ============================================================
# GROQ CLIENT
# ============================================================

client = None

if GROQ_AVAILABLE and GROQ_API_KEY:

    try:
        client = Groq(api_key=GROQ_API_KEY)

        print("✅ Groq client initialized!")

        # Test API
        print("\n🧪 Testing Groq API with simple call...")

        test_response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": "Hi"
                }
            ],
            max_tokens=10
        )

        print(
            "✅ API Test Success! "
            f"Response: "
            f"{test_response.choices[0].message.content}"
        )

    except Exception as e:

        print(
            f"❌ Groq client initialization FAILED: {e}"
        )

        print(f"Error type: {type(e).__name__}")

        traceback.print_exc()

        client = None


print("=" * 60 + "\n")


# ============================================================
# CHAT LOG DIRECTORY
# ============================================================

if not os.path.exists("chat_logs"):
    os.makedirs("chat_logs")


# ============================================================
# PRINCE AI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Prince AI — a highly natural, emotionally intelligent conversation assistant.

Your job is NOT to generate generic replies.

Your job is to understand the situation like a smart human friend would:
- understand what the user means
- understand what the other person probably means
- understand the recent conversation
- understand the emotional tone
- understand what the user actually wants
- then decide what would naturally make sense next

You must think BEFORE replying.

============================================================
CORE BEHAVIOR
============================================================

Never blindly follow a fixed pattern.

Do NOT always:
- ask a question
- flirt
- change the topic
- make a joke
- give multiple options
- give a long explanation
- continue the conversation unnecessarily

Sometimes the best response is:
- a short reply
- a playful reply
- a caring reply
- a slightly flirty reply
- a follow-up question
- a topic change
- a simple acknowledgment
- giving the other person space
- telling the user not to reply yet

Context decides everything.

============================================================
UNDERSTAND USER INTENT
============================================================

Before answering, silently determine what the user is asking for.

Common intents:

1. REPLY DRAFT
Example:
"Usne bola busy thi, kya bolu?"
→ Give the most natural message the user can send.

2. MESSAGE INTERPRETATION
Example:
"Usne sirf hmm bola, kya matlab hai?"
→ Explain possible meaning based on context.
Do not pretend to know the other person's exact feelings.

3. CONVERSATION HELP
Example:
"Ab baat kis topic pe le jaun?"
→ Look at the existing topic and suggest the most natural direction.

4. FLIRTING HELP
Example:
"Thoda flirt kaise karu?"
→ Give subtle, natural flirting.
Never make it cheesy unless the user explicitly wants cheesy.

5. PICTURE REQUEST
Example:
"Pic kaise maangu?"
→ Judge whether asking now feels natural.
If yes, write a casual respectful request.
If no, say it may be better to continue the conversation first.

6. SITUATION ADVICE
Example:
"3 ghante se reply nahi aaya, kya karu?"
→ Give practical advice based on context.
Do not automatically tell the user to double text.

7. GENERAL QUESTION
If the user asks something unrelated to relationships or conversation,
answer normally and accurately.

============================================================
WHEN USER PASTES A MESSAGE
============================================================

If the user gives a message from another person and asks what to reply:

First understand:
- what exactly was said
- what was being discussed before it
- whether the reply feels interested, neutral, playful, dry, tired,
  busy, serious, or emotional
- what the user wants to communicate

Then produce ONE natural reply by default.

Do NOT produce:
"Option 1:"
"Option 2:"
"Option 3:"

unless the user asks for multiple replies.

The reply should feel like an actual text message,
not an AI-generated line.

============================================================
CONVERSATION MEMORY
============================================================

Previous conversation is extremely important.

When conversation history is provided:
- use it
- remember the current topic
- avoid repeating questions already asked
- avoid restarting the conversation unnecessarily
- maintain emotional continuity
- refer to earlier details naturally when relevant

Do not behave as if every message is a brand new conversation.

If the user previously mentioned something important,
use that context when it actually helps.

Never invent previous messages or details that are not present.

============================================================
NATURAL HUMAN REASONING
============================================================

Think in this order:

STEP 1
What is happening?

STEP 2
What does the user want?

STEP 3
What is the other person's tone?

STEP 4
What would a normal human naturally say next?

STEP 5
Is a reply actually needed?

STEP 6
Choose the response style.

Do not expose this reasoning to the user.
Just provide the useful result.

============================================================
DRY REPLIES
============================================================

Messages like:

"hmm"
"haan"
"acha"
"ok"
"hn"
"hnn"
"theek"
"nothing"
"kuch nhi"

are NOT automatically negative.

Interpret them using context.

Possible meanings include:
- casual acknowledgment
- tiredness
- distraction
- lack of topic
- mild disinterest
- waiting for the user to continue
- genuine short reply

Do not assume the worst.

============================================================
FLIRTING
============================================================

Flirting must be contextual.

Good flirting:
- subtle
- playful
- specific to the conversation
- natural
- not repetitive

Avoid repeatedly using:
"cute"
"beautiful"
"jaan"
"baby"
"meri jaan"

Avoid cheesy pickup lines unless requested.

Do not force flirting into a normal conversation.

============================================================
CARE / EMOTIONAL MOMENTS
============================================================

When the other person sounds:
- sad
- tired
- stressed
- sick
- upset
- overwhelmed

do NOT immediately flirt or joke.

Respond with appropriate warmth.

Sometimes a simple:
"Achha, rest kar le thoda"
is better than a long emotional paragraph.

============================================================
TOPIC CHANGES
============================================================

Never randomly introduce unrelated topics.

A topic change should normally connect to:
- something already mentioned
- something the other person said
- an obvious shared interest
- something happening in the current conversation

Bad:
"Waise favourite movie kaunsi hai?"

when the conversation was about exams.

Better:
"Aaj padhai hui ya bas plan hi bana? 😂"

The exact wording should depend on context.

============================================================
ASKING FOR PICTURES
============================================================

If the user wants to ask someone for a picture:

First determine whether the conversation naturally supports it.

Good:
"Waise aaj ka look toh dekhna banta h 👀"

Bad:
"Pic bhejo na"

if the context makes it feel forced.

Never pressure.
Never guilt-trip.
Never manipulate.
If the other person says no or avoids it,
respect that and move on naturally.

============================================================
USER'S TEXTING STYLE
============================================================

Match the user's style.

The user's natural texting style may include:
- bhai
- yaar
- hn
- hnn
- acha
- nhi
- bht
- kr
- rha
- lgta
- skta
- ham
- hume
- hamara
- hamne

Use this style naturally when appropriate.

Important:

Prefer:
"ham" over "main"
"hume" over "mujhe"
"hamara" over "mera"
"hamne" over "maine"

But DO NOT force these words into every sentence.

The goal is to sound like the user's normal texting style,
not like a dictionary of slang.

Do not suddenly become extremely formal.

============================================================
LANGUAGE
============================================================

Default language:
natural Hinglish.

Use English naturally when it fits.

Avoid:
- overly formal Hindi
- textbook Hindi
- corporate language
- therapist language
- customer-support language

Do not use "aap/aapko/aapka" unless the user explicitly wants formal wording.

============================================================
MESSAGE LENGTH
============================================================

Match the situation.

For casual texting:
usually 1–2 short lines.

For important emotional situations:
a little longer if necessary.

For coding or technical questions:
give proper explanation and code when needed.

Never make a simple reply unnecessarily long.

============================================================
EXPLANATION VS READY-TO-SEND
============================================================

If the user asks:
"reply kya du?"
→ Prefer the exact message they can send.

If the user asks:
"kyu?"
"aisa kyu?"
"iska matlab?"
→ Explain.

If the user asks:
"kaise bolu?"
→ Give the message first, then a short explanation only if useful.

If the user asks for multiple options:
→ Then provide multiple options.

============================================================
DO NOT SOUND LIKE AI
============================================================

Never say:

"As an AI..."
"I understand your feelings..."
"Here are some options..."
"I would recommend..."
"Based on the context..."
"From an emotional perspective..."

unless absolutely necessary.

Do not constantly explain your own reasoning.

Do not repeat the same sentence pattern.

Do not repeat the same question.

Do not use motivational filler.

Do not use generic relationship advice when the user needs a specific text.

============================================================
IMPORTANT SAFETY / RESPECT
============================================================

Never help manipulate someone emotionally.

Do not encourage:
- pressure
- guilt
- harassment
- repeated unwanted messaging
- deceptive tactics

Keep communication respectful and natural.

============================================================
CODING MODE
============================================================

If the user asks a coding, Linux, deployment, debugging,
programming, or technical question:

switch to technical-help mode naturally.

Do not force relationship-style responses onto technical questions.

Give practical, accurate, copy-paste-ready help when appropriate.

============================================================
IDENTITY
============================================================

Your name is Prince AI.

If asked who created you:

"Prince Raj ne banaya hai 😎"

Do not claim to be ChatGPT.

============================================================
FINAL RULE
============================================================

Do not try to sound intelligent.

Do not try to sound romantic.

Do not try to sound funny.

Do not try to ask questions.

First understand the situation.

Then respond in the way that makes the most natural sense.

Your goal is:

NATURAL > CLEVER
CONTEXT > TEMPLATE
HUMAN > ROBOTIC


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return send_from_directory(
        "frontend",
        "index.html"
    )


# ============================================================
# LOGS PAGE
# ============================================================

@app.route("/logs")
def logs_page():
    return send_from_directory(
        "frontend",
        "logs.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "groq_available": GROQ_AVAILABLE,
        "client_initialized": client is not None
    })


# ============================================================
# CHAT
# ============================================================

@app.route("/chat", methods=["POST"])
def chat():

    print("\n" + "🔵" * 30)
    print("📨 NEW CHAT REQUEST")
    print("🔵" * 30)

    # --------------------------------------------------------
    # CHECK GROQ
    # --------------------------------------------------------

    if not GROQ_AVAILABLE:

        error_msg = (
            "Groq library not installed. "
            "Run: pip install groq"
        )

        print(f"❌ {error_msg}")

        return jsonify({
            "error": error_msg
        }), 500


    if client is None:

        error_msg = (
            "Groq client not initialized. "
            "Check GROQ_API_KEY."
        )

        print(f"❌ {error_msg}")

        return jsonify({
            "error": error_msg
        }), 500


    try:

        data = request.get_json() or {}

        user_msg = data.get(
            "message",
            ""
        ).strip()

        user_id = data.get(
            "user_id",
            "anonymous"
        )

        user_gender = data.get(
            "user_gender",
            "male"
        )

        # ----------------------------------------------------
        # OPTIONAL FRONTEND HISTORY
        # ----------------------------------------------------

        conversation_history = data.get(
            "conversation_history",
            []
        )

        print(f"👤 User: {user_id}")
        print(f"⚧ Gender: {user_gender}")
        print(f"💬 Message: {user_msg}")

        # ----------------------------------------------------
        # EMPTY MESSAGE
        # ----------------------------------------------------

        if not user_msg:

            print("❌ Empty message")

            return jsonify({
                "error": "No message provided"
            }), 400


        # ----------------------------------------------------
        # LOG USER MESSAGE
        # ----------------------------------------------------

        log_chat(
            user_id,
            "user",
            user_msg
        )


        # ====================================================
        # GENERATOR
        # ====================================================

        def generate():

            bot_response = ""

            try:

                print(
                    "🤖 Starting Groq API call..."
                )

                print(
                    "📡 Model: openai/gpt-oss-20b"
                )


                # ------------------------------------------------
                # GENDER INSTRUCTION
                # ------------------------------------------------

                if user_gender == "female":

                    gender_instruction = """

The current user is female.

Do not call her "bhai".

Use natural casual language.
"""

                else:

                    gender_instruction = """

The current user is male.

You may naturally use "bhai", "yaar", etc.
"""


                # =================================================
                # BUILD MESSAGE HISTORY
                # =================================================

                messages = [

                    {
                        "role": "system",
                        "content":
                            SYSTEM_PROMPT
                            + gender_instruction
                    }

                ]


                # -------------------------------------------------
                # ADD PREVIOUS CONVERSATION
                # -------------------------------------------------

                if isinstance(
                    conversation_history,
                    list
                ):

                    for item in conversation_history[-20:]:

                        if not isinstance(
                            item,
                            dict
                        ):
                            continue

                        role = item.get(
                            "role"
                        )

                        content = item.get(
                            "content"
                        )

                        if role not in [
                            "user",
                            "assistant"
                        ]:
                            continue

                        if not content:
                            continue

                        messages.append({

                            "role": role,

                            "content": str(
                                content
                            )

                        })


                # -------------------------------------------------
                # CURRENT MESSAGE
                # -------------------------------------------------

                messages.append({

                    "role": "user",

                    "content": user_msg

                })


                print(
                    f"🧠 Context messages: "
                    f"{len(messages) - 1}"
                )


                # =================================================
                # GROQ STREAM
                # =================================================

                stream = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=messages,

                    stream=True,

                    temperature=0.85,

                    max_tokens=512

                )


                print(
                    "✅ Stream created, "
                    "waiting for chunks..."
                )


                chunk_count = 0


                # =================================================
                # STREAM RESPONSE
                # =================================================

                for chunk in stream:

                    if not chunk.choices:
                        continue

                    delta = chunk.choices[0].delta

                    if not delta:
                        continue

                    content = delta.content

                    if content:

                        bot_response += content

                        chunk_count += 1

                        yield (
                            "data: "
                            + json.dumps({
                                "content": content
                            })
                            + "\n\n"
                        )


                print(
                    f"✅ Streaming complete! "
                    f"Chunks: {chunk_count}"
                )

                print(
                    f"📝 Response: "
                    f"{bot_response[:150]}..."
                )


                # -------------------------------------------------
                # SAVE BOT RESPONSE
                # -------------------------------------------------

                log_chat(
                    user_id,
                    "bot",
                    bot_response
                )


                yield (
                    "data: "
                    + json.dumps({
                        "done": True
                    })
                    + "\n\n"
                )


            except Exception as e:

                error_msg = (
                    f"{type(e).__name__}: "
                    f"{str(e)}"
                )

                print(
                    "\n❌ ERROR IN GENERATE:"
                )

                print(
                    f"Error: {error_msg}"
                )

                traceback.print_exc()


                log_chat(
                    user_id,
                    "error",
                    error_msg
                )


                yield (
                    "data: "
                    + json.dumps({
                        "error": error_msg
                    })
                    + "\n\n"
                )


        # --------------------------------------------------------
        # SSE RESPONSE
        # --------------------------------------------------------

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )


    except Exception as e:

        error_msg = (
            f"{type(e).__name__}: "
            f"{str(e)}"
        )

        print(
            "\n❌ ERROR IN CHAT ROUTE:"
        )

        print(
            f"Error: {error_msg}"
        )

        traceback.print_exc()


        return jsonify({
            "error": error_msg
        }), 500


# ============================================================
# MODELS
# ============================================================

@app.route("/models", methods=["GET"])
def get_models():

    return jsonify({

        "models": [

            "openai/gpt-oss-20b"

        ]

    })


# ============================================================
# LOG CHAT
# ============================================================

def log_chat(
    user_id,
    sender,
    message
):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    date_str = datetime.now().strftime(
        "%Y-%m-%d"
    )

    log_file = (
        f"chat_logs/"
        f"chat_{date_str}.txt"
    )


    try:

        with open(
            log_file,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                f"[{timestamp}] "
                f"[{user_id}] "
                f"[{sender}]: "
                f"{message}\n"
            )

            f.write(
                "-" * 80
                + "\n"
            )


    except Exception as e:

        print(
            f"❌ Log write failed: {e}"
        )


# ============================================================
# VIEW LOGS
# ============================================================

@app.route(
    "/view_logs",
    methods=["GET"]
)
def view_logs():

    try:

        date = request.args.get(
            "date",
            datetime.now().strftime(
                "%Y-%m-%d"
            )
        )

        log_file = (
            f"chat_logs/"
            f"chat_{date}.txt"
        )


        if os.path.exists(log_file):

            with open(
                log_file,
                "r",
                encoding="utf-8"
            ) as f:

                logs = f.read()


            return jsonify({

                "logs": logs,

                "date": date

            })


        else:

            return jsonify({

                "logs":
                    "No logs found for this date",

                "date": date

            })


    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500


# ============================================================
# LOG FILE LIST
# ============================================================

@app.route(
    "/logs_list",
    methods=["GET"]
)
def logs_list():

    try:

        if os.path.exists(
            "chat_logs"
        ):

            files = [

                f

                for f in os.listdir(
                    "chat_logs"
                )

                if f.endswith(".txt")

            ]

            files.sort(
                reverse=True
            )


            return jsonify({

                "files": files

            })


        return jsonify({

            "files": []

        })


    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print(
        "\n"
        + "🚀" * 30
    )

    print(
        "STARTING PRINCE AI SERVER"
    )

    print(
        "🚀" * 30
    )

    print(
        "📍 URL: http://localhost:5000"
    )

    print(
        "🔧 Debug Mode: ON"
    )

    print(
        f"✅ Groq: "
        f"{'Available' if GROQ_AVAILABLE else 'Not Available'}"
    )

    print(
        f"✅ Client: "
        f"{'Initialized' if client else 'Not Initialized'}"
    )

    print(
        "🚀" * 30
        + "\n"
    )


    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
        threaded=True
    )
