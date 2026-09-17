from dotenv import load_dotenv
load_dotenv()

import json
import os
import traceback
from datetime import datetime

from flask import Flask, Response, jsonify, request, send_from_directory

# ============================================================
# GROQ IMPORT
# ============================================================

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception as exc:
    print(f"❌ Groq import failed: {exc}")
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
# GROQ CONFIG
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "openai/gpt-oss-20b"

client = None

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY is missing")
else:
    print(
        f"🔑 API Key loaded: "
        f"{GROQ_API_KEY[:8]}...{GROQ_API_KEY[-4:]}"
    )

if GROQ_AVAILABLE and GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq client initialized")
    except Exception as exc:
        print(f"❌ Groq client initialization failed: {exc}")
        traceback.print_exc()
        client = None


# ============================================================
# CHAT LOG DIRECTORY
# ============================================================

os.makedirs("chat_logs", exist_ok=True)


# ============================================================
# PRINCE AI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = r"""


You are not simply generating replies.
You are participating in an ongoing human conversation.

For every incoming message:

1. Read the latest message.
2. Read the relevant previous conversation.
3. Understand what the other person is actually trying to communicate.
4. Identify the current emotional state and conversational momentum.
5. Decide whether the best response should:
   - continue the topic
   - ask something
   - tease
   - flirt subtly
   - show care
   - joke
   - acknowledge
   - change the topic
   - or simply respond briefly.

NEVER choose a response style before understanding the situation.

------------------------------------------------------------
NATURAL RESPONSE SELECTION
------------------------------------------------------------

Do not always make the conversation more romantic.

If the conversation is already romantic:
    maintain the vibe without repeatedly escalating it.

If the conversation is casual:
    remain casual.

If the other person is giving short replies:
    don't automatically assume disinterest.

If the other person is enthusiastic:
    match their energy naturally.

If the other person asks a question:
    answer it first before asking another question.

If the other person shares something personal:
    respond to that instead of immediately changing the topic.

If there is no reason to ask a question:
    don't ask one just to keep the conversation alive.

------------------------------------------------------------
CONVERSATION MEMORY
------------------------------------------------------------

Treat the conversation as one continuous interaction.

Remember:
- what has already been discussed
- previous jokes
- previous questions
- emotional moments
- things the other person mentioned
- topics that were already exhausted
- promises or plans mentioned earlier

Never ask the same question again unless there is a natural reason.

Never behave as if the conversation has restarted after every message.

------------------------------------------------------------
MESSAGE GENERATION
------------------------------------------------------------

When the user asks "reply kya du?":

Return ONLY the message they can send.

Do not explain the reasoning unless explicitly asked.

Normally generate ONE strong reply.

The reply must sound like something a real person would actually type on WhatsApp.

Avoid overly perfect sentences.

Natural imperfections are okay, but do not intentionally create bad grammar.

------------------------------------------------------------
ANTI-REPETITION
------------------------------------------------------------

Do not repeatedly use the same patterns such as:

"Achhaaa..."
"yaarrr..."
"🫣❤️"
"tum bhi naaa"
"itni cute..."
"itni special..."

If a phrase has already been used several times,
find a different natural expression.

Do not recycle the same flirting structure.

------------------------------------------------------------
FLIRTING INTELLIGENCE
------------------------------------------------------------

Flirting must come from the context.

Do not flirt simply because the conversation involves a girl/boy.

Use subtle flirting when the conversation naturally supports it.

Prefer:
- playful teasing
- small compliments
- callbacks to previous conversation
- light curiosity
- natural affection

Avoid:
- pickup lines
- exaggerated romance
- constant compliments
- possessiveness
- pressure
- manipulation

------------------------------------------------------------
EXPECTED REPLY MODE
------------------------------------------------------------

If the user asks:
"Expected reply kya aayega?"

Do NOT claim to know exactly what the person will say.

Instead provide 3-5 realistic possibilities based on the conversation.

If one response seems particularly natural,
label it as the most likely possibility,
but make clear that it is only a guess.

------------------------------------------------------------
SOCIAL SIGNAL INTERPRETATION
------------------------------------------------------------

Never confidently claim:

"She definitely likes you."
"She is giving a green signal."
"She is in love."
"She wants you."

Instead say things like:

"Is context mein ye positive/casual/playful lag raha hai."
"Isse interest possible hai, but exact intention confirm nahi hoti."

Base interpretations only on the actual conversation.

------------------------------------------------------------
TOPIC TRANSITIONS
------------------------------------------------------------

When the user wants a new topic:

Do not randomly introduce an unrelated question.

Look for something already mentioned in the conversation
and use it as a bridge.

Example:

If they discussed food:
"Waise tumhari favourite dessert kya hai?"

If they discussed travelling:
"Waise tumhe mountains zyada pasand hain ya beaches?"

If they discussed clothes:
"Waise shopping mein tum zyada time kis cheez pe laga deti ho? 😂"

The transition should feel spontaneous, not scripted.

------------------------------------------------------------
IMPORTANT
------------------------------------------------------------

Your goal is NOT to keep the conversation going at any cost.

Your goal is to make the NEXT message feel natural.

A short natural reply is better than a clever long reply.

A genuine question is better than a forced romantic line.

Context is more important than style.

The best response is the one that a socially aware human friend
would genuinely suggest sending at that exact moment.
"""


# ============================================================
# HELPERS
# ============================================================

def safe_history(raw_history):
    """Return only valid recent user/assistant messages."""

    if not isinstance(raw_history, list):
        return []

    cleaned = []

    for item in raw_history[-20:]:

        if not isinstance(item, dict):
            continue

        role = item.get("role")
        content = item.get("content")

        if role not in {"user", "assistant"}:
            continue

        if not content:
            continue

        cleaned.append({
            "role": role,
            "content": str(content).strip()
        })

    return cleaned


def log_chat(user_id, sender, message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    date_str = datetime.now().strftime(
        "%Y-%m-%d"
    )

    log_file = os.path.join(
        "chat_logs",
        f"chat_{date_str}.txt"
    )

    try:

        with open(
            log_file,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"[{timestamp}] "
                f"[{user_id}] "
                f"[{sender}]: "
                f"{message}\n"
            )

            file.write(
                "-" * 80 + "\n"
            )

    except Exception as exc:

        print(
            f"❌ Log write failed: {exc}"
        )


# ============================================================
# FRONTEND ROUTES
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        "frontend",
        "index.html"
    )


@app.route("/logs")
def logs_page():

    return send_from_directory(
        "frontend",
        "logs.html"
    )


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "groq_available": GROQ_AVAILABLE,
        "client_initialized": client is not None,
        "model": MODEL_NAME
    })


# ============================================================
# CHAT
# ============================================================

@app.route("/chat", methods=["POST"])
def chat():

    if not GROQ_AVAILABLE:

        return jsonify({
            "error":
                "Groq library not installed. "
                "Run: pip install groq"
        }), 500


    if client is None:

        return jsonify({
            "error":
                "Groq client not initialized. "
                "Check GROQ_API_KEY."
        }), 500


    try:

        data = request.get_json(
            silent=True
        ) or {}


        user_msg = str(
            data.get(
                "message",
                ""
            )
        ).strip()


        user_id = str(
            data.get(
                "user_id",
                "anonymous"
            )
        )


        user_gender = str(
            data.get(
                "user_gender",
                "male"
            )
        ).lower()


        conversation_history = safe_history(
            data.get(
                "conversation_history",
                []
            )
        )


        if not user_msg:

            return jsonify({
                "error":
                    "No message provided"
            }), 400


        print(
            "\n" + "🔵" * 25
        )

        print(
            "📨 NEW CHAT REQUEST"
        )

        print(
            f"👤 User: {user_id}"
        )

        print(
            f"⚧ Gender: {user_gender}"
        )

        print(
            f"💬 Message: {user_msg}"
        )

        print(
            f"🧠 History messages: "
            f"{len(conversation_history)}"
        )


        log_chat(
            user_id,
            "user",
            user_msg
        )


        # ====================================================
        # GENDER INSTRUCTION
        # ====================================================

        if user_gender == "female":

            gender_instruction = """
The current user is female.

Do not call her "bhai".

Use natural casual language.
"""

        else:

            gender_instruction = """
The current user is male.

You may naturally use "bhai" and "yaar"
when it fits.
"""


        # ====================================================
        # BUILD MESSAGES
        # ====================================================

        messages = [

            {
                "role": "system",
                "content":
                    SYSTEM_PROMPT
                    + gender_instruction
            }

        ]


        # ====================================================
        # ADD HISTORY
        # ====================================================

        if conversation_history:

            last_item = conversation_history[-1]

            current_already_in_history = (

                last_item.get("role") == "user"

                and

                last_item.get("content") == user_msg

            )


            if current_already_in_history:

                messages.extend(
                    conversation_history[:-1]
                )

            else:

                messages.extend(
                    conversation_history
                )


        # ====================================================
        # CURRENT USER MESSAGE
        # ====================================================

        messages.append({

            "role": "user",

            "content": user_msg

        })


        print(
            f"🧠 Total model messages: "
            f"{len(messages)}"
        )


        # ====================================================
        # STREAM GENERATOR
        # ====================================================

        def generate():

            bot_response = ""

            try:

                stream = client.chat.completions.create(

                    model=MODEL_NAME,

                    messages=messages,

                    stream=True,

                    temperature=0.85,

                    max_tokens=512

                )


                print(
                    "✅ Groq stream started"
                )


                chunk_count = 0


                # ============================================
                # STREAM RESPONSE
                # ============================================

                for chunk in stream:

                    if not chunk.choices:
                        continue


                    delta = (
                        chunk.choices[0].delta
                    )


                    if not delta:
                        continue


                    content = delta.content


                    if not content:
                        continue


                    bot_response += content

                    chunk_count += 1


                    yield (

                        "data: "

                        + json.dumps({

                            "content":
                                content

                        })

                        + "\n\n"

                    )


                print(
                    f"✅ Streaming complete: "
                    f"{chunk_count} chunks"
                )


                log_chat(
                    user_id,
                    "bot",
                    bot_response
                )


                yield (

                    "data: "

                    + json.dumps({

                        "done":
                            True

                    })

                    + "\n\n"

                )


            except Exception as exc:

                error_msg = (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )


                print(
                    f"❌ Chat generation error: "
                    f"{error_msg}"
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

                        "error":
                            error_msg

                    })

                    + "\n\n"

                )


        # ====================================================
        # SSE RESPONSE
        # ====================================================

        return Response(

            generate(),

            mimetype="text/event-stream",

            headers={

                "Cache-Control":
                    "no-cache",

                "X-Accel-Buffering":
                    "no"

            }

        )


    except Exception as exc:

        error_msg = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )


        print(
            f"❌ Chat route error: "
            f"{error_msg}"
        )


        traceback.print_exc()


        return jsonify({

            "error":
                error_msg

        }), 500


# ============================================================
# MODELS
# ============================================================

@app.route(
    "/models",
    methods=["GET"]
)
def get_models():

    return jsonify({

        "models": [
            MODEL_NAME
        ]

    })


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


        log_file = os.path.join(

            "chat_logs",

            f"chat_{date}.txt"

        )


        if os.path.exists(
            log_file
        ):

            with open(
                log_file,
                "r",
                encoding="utf-8"
            ) as file:

                logs = file.read()


        else:

            logs = (
                "No logs found for this date"
            )


        return jsonify({

            "logs":
                logs,

            "date":
                date

        })


    except Exception as exc:

        return jsonify({

            "error":
                str(exc)

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

        if not os.path.exists(
            "chat_logs"
        ):

            return jsonify({
                "files": []
            })


        files = [

            name

            for name
            in os.listdir(
                "chat_logs"
            )

            if name.endswith(".txt")

        ]


        files.sort(
            reverse=True
        )


        return jsonify({

            "files":
                files

        })


    except Exception as exc:

        return jsonify({

            "error":
                str(exc)

        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print(
        "\n" + "🚀" * 25
    )

    print(
        "STARTING PRINCE AI SERVER"
    )

    print(
        "🚀" * 25
    )

    print(
        "📍 URL: http://localhost:5000"
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
        f"🤖 Model: {MODEL_NAME}"
    )

    print(
        "🚀" * 25
        + "\n"
    )


    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000,

        threaded=True

    )
