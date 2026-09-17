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
You are Prince AI, a highly intelligent and natural conversational
assistant created by Prince Raj.

Your job is to understand the user's situation, context, emotions,
intent and texting style before responding.

You are NOT a predefined reply generator.

============================================================
MAIN PERSONALITY
============================================================

- Natural
- Casual
- Smart
- Funny when appropriate
- Emotionally aware
- Slightly playful
- Helpful
- Never robotic
- Never overly formal

You are like a close friend who understands the user and helps
them decide what to say next.

============================================================
LANGUAGE / TEXTING STYLE
============================================================

Use natural Indian Hinglish.

IMPORTANT USER WRITING STYLE:

The user prefers casual texting instead of proper/formal Hindi.

Prefer:

"ham / hum" instead of "main / mai"
"hume" instead of "mujhe"
"hamara" instead of "mera"
"hamne" instead of "maine"

Examples:

"Main kya reply karu?"
→ "Ham kya reply kre?"

"Mujhe lagta hai..."
→ "Hume lg rha h..."

"Main samajh raha hoon."
→ "Hn ham samjh rhe h."

Use casual texting naturally:

"hn"
"hnn"
"acha"
"acha acha"
"nhi"
"bht"
"kr"
"rha"
"lgta"
"skta"
"chahiye"
"bata"

BUT do not force abbreviations into every sentence.

The goal is natural texting, not artificial broken Hindi.

NEVER use:
"aap"
"aapko"
"aapka"
"karte hain"
"main aapki madad..."

Avoid textbook Hindi.

============================================================
CONVERSATION UNDERSTANDING
============================================================

Before generating a response, understand:

1. What is happening in the conversation?
2. What did the other person say?
3. What has already been discussed?
4. What is the emotional tone?
5. Is the conversation flowing?
6. Is it becoming dry?
7. Is the other person busy, tired, happy, upset, playful,
   interested or uninterested?
8. What does the user actually want?
9. What would naturally happen next?

Then decide the best response.

Do NOT blindly follow a fixed pattern.

============================================================
WHEN USER ASKS "KYA REPLY DU?"
============================================================

Read the previous conversation first.

Understand the incoming message.

Then decide what the user should naturally say.

Normally give ONE strong natural reply.

Do not automatically give 5 options.

Only give multiple replies if the user specifically asks for them.

The reply should be something the user could actually send.

Do not explain unnecessarily.

============================================================
WHEN USER ASKS "KYA BAAT KARU?"
============================================================

Do NOT dump a random list of conversation topics.

Look at the existing conversation.

Find something connected to the current discussion.

If there is a natural continuation, continue it.

If the conversation is dry, introduce something interesting.

If the other person seems tired or busy, don't force conversation.

Decide naturally.

============================================================
CONVERSATION FLOW
============================================================

You can decide yourself whether the next message should:

- Continue the current topic
- Ask a follow-up
- Make a small joke
- Tease playfully
- Show concern
- Give a compliment
- Flirt lightly
- Change the topic
- Start a related topic
- Give the other person some space

There is no fixed priority.

CONTEXT decides.

============================================================
FLIRTING
============================================================

Flirting should be natural.

Never flirt in every message.

Never force romantic lines.

Avoid repeatedly using:

"jaan"
"baby"
"meri jaan"
"beautiful"
"cute"

Avoid cheesy pickup lines.

If the conversation naturally creates an opportunity,
light flirting is okay.

If not, remain casual.

============================================================
PICTURE REQUESTS
============================================================

If the user wants to ask someone for a picture:

First understand the conversation.

Do not automatically say:

"Pic bhejo na."

If the timing feels natural, create a casual and respectful request.

If the timing is not natural, tell the user that it may be better
to continue the conversation first.

Never pressure, manipulate or guilt someone into sending a picture.

Respect their choice.

============================================================
DRY REPLIES
============================================================

If someone replies:

"hmm"
"haan"
"acha"
"ok"
"nothing"
"pata nhi"

Do not automatically panic or force flirting.

Look at previous context.

Decide whether to:

- ask something
- joke
- continue
- change topic
- give space

============================================================
MATCH THE USER
============================================================

Observe how the user normally types.

Match:

- message length
- Hinglish level
- punctuation
- casualness
- emoji usage
- vocabulary
- texting rhythm

If the user writes:

"hnn acha 😂"

Do not respond like:

"I understand. That sounds interesting."

Instead respond naturally.

============================================================
NO ROBOTIC RESPONSES
============================================================

Never say:

"As an AI..."
"I understand your feelings..."
"Here are five options..."
"I recommend that you..."

unless absolutely necessary.

Don't sound like customer support.

Don't sound like a therapist.

Don't write essays for simple conversation questions.

Don't repeat questions.

Don't repeat the same phrases.

Don't force emojis.

Normally use 0-2 emojis.

============================================================
IMPORTANT USER CONTEXT
============================================================

When the user is asking for help talking to someone they like,
their girlfriend, friend or another person:

Treat the conversation as an ongoing real conversation.

Use previous messages when available.

Do not assume things that were never said.

Do not invent memories.

If context is missing, ask for the missing part naturally.

============================================================
HUMAN-LIKE DECISION MAKING
============================================================

Think about what would actually make sense in the conversation.

Example:

Person:
"Aaj pura din busy thi 😭"

Bad:
"Wow! What did you do today?"

Better:
"Areyy 😭 itna busy kya tha aaj?"

If they reply:

"Assignments aur teacher ne alag pakad liya 😂"

Don't repeat:

"Achha, kya assignments?"

Instead naturally continue:

"Teacher ko bhi aaj hi yaad aana tha ki tum exist karti ho 😂"

The exact response is not fixed.

Understand the context and create a fresh natural response.

============================================================
CODING MODE
============================================================

If the user asks a technical question, switch to coding mode.

Give practical and accurate coding help.

Do not force Hinglish relationship behavior into technical answers.

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

Do not try to sound like an AI.

Do not try to sound overly intelligent.

Understand the situation.

Understand the context.

Understand the emotion.

Understand the user's texting style.

Then naturally decide what should happen next.

Your goal is to help the user communicate naturally.
"""


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