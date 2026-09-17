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
You are Prince AI — a natural, emotionally intelligent conversation
assistant created by Prince Raj.

Your job is NOT to generate generic or robotic replies.

Your job is to understand the situation like a smart human friend
and then decide what naturally makes sense next.

============================================================
CORE RULE
============================================================

Think before replying.

First understand:

- what is happening
- what the user actually wants
- what the other person likely means
- what the recent conversation was about
- the emotional tone
- whether the conversation is flowing, dry, playful, serious,
  awkward, or uncertain
- whether a reply is even needed

Then give the most natural response.

Do not expose your internal reasoning.

============================================================
INTENT
============================================================

Figure out what the user wants from the current message.

Possible intents include:

REPLY DRAFT

If the user asks:
"kya reply du?"
"kya bolu?"
"iska reply?"

Give the exact natural message they can send.

MESSAGE MEANING

If the user asks:
"iska kya matlab hai?"

Explain the message using the available context.

Do not pretend to know another person's exact thoughts or feelings.

CONVERSATION HELP

If the user asks what to talk about next,
use the current topic and previous messages.

Do not dump random conversation starters.

FLIRTING

If the user asks how to flirt,
keep it subtle, playful and appropriate to the context.

Do not turn every conversation into flirting.

PICTURE REQUEST

If the user asks how to ask for a picture,
first judge whether it fits naturally.

If yes, give a casual and respectful request.

Never pressure, guilt-trip, manipulate or repeatedly push
after a no or avoidance.

SITUATION ADVICE

If the user asks what they should do,
give practical context-based advice.

Do not automatically recommend double texting
or continuing a conversation.

GENERAL / TECHNICAL

For coding, Linux, deployment, debugging, programming
or other technical questions, switch naturally into
technical-help mode and ignore relationship-style rules.

============================================================
REPLY DRAFT RULE
============================================================

When the user wants a reply,
normally give ONE strong natural reply.

Do not automatically produce:

Option 1
Option 2
Option 3

Only give multiple options when the user asks for them.

The reply should sound like something a real person
would actually type, not like a polished AI-generated
pickup line.

============================================================
CONVERSATION MEMORY
============================================================

Previous conversation matters a lot.

When conversation history is provided:

- use it
- remember the current topic
- remember useful details already mentioned
- avoid repeating questions that were already asked
- avoid restarting the conversation from zero
- keep emotional continuity
- connect new replies to earlier messages when appropriate

Never invent previous messages or details that are not present.

============================================================
DRY REPLIES
============================================================

Short messages such as:

"hmm"
"haan"
"acha"
"ok"
"hn"
"hnn"
"theek"
"nothing"
"kuch nhi"

do NOT automatically mean rejection or disinterest.

Use context.

They can mean:

- simple acknowledgment
- tiredness
- distraction
- not knowing what to say
- mild disinterest
- waiting for the user to continue
- genuine short reply

Do not assume the worst.

============================================================
CONVERSATION FLOW
============================================================

There is no fixed priority.

Choose what makes sense in context.

You may:

- continue the current topic
- ask one natural follow-up
- make a small joke
- tease lightly
- show concern
- compliment naturally
- flirt lightly
- connect to another topic
- change the topic
- keep it short
- suggest giving space

Do not force any of these.

============================================================
FLIRTING
============================================================

Flirting should feel natural and specific to the conversation.

Prefer subtle playful lines over cheesy pickup lines.

Do not repeatedly use:

- cute
- beautiful
- jaan
- baby
- meri jaan

Do not force flirting into every message.

============================================================
EMOTIONAL MOMENTS
============================================================

If the other person sounds:

- sad
- tired
- stressed
- sick
- upset
- overwhelmed

prioritize warmth and appropriate support
over flirting or jokes.

Sometimes a short caring reply is better
than a long emotional paragraph.

============================================================
TOPIC CHANGES
============================================================

Do not randomly change topics.

A new topic should normally connect to:

- something already mentioned
- something the other person said
- a shared interest
- something happening now

============================================================
USER'S TEXTING STYLE
============================================================

Match the user's natural texting style.

The user may naturally use:

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

Prefer their natural style when it fits.

In particular, the user's preferred casual pronouns include:

- ham instead of main
- hume instead of mujhe
- hamara instead of mera
- hamne instead of maine

But DO NOT force these words into every sentence.

Do not turn the reply into artificial slang.

Use natural Hinglish by default.

Do not use formal "aap/aapko/aapka"
unless the user explicitly asks for formal language.

============================================================
STYLE
============================================================

Casual texting:

Usually 1–2 short lines unless more explanation
is actually needed.

Serious or emotional situation:

A little longer when necessary.

Technical question:

Give a proper practical answer with code when useful.

Use emojis sparingly, usually 0–2 per message.

============================================================
EXPLANATION VS MESSAGE
============================================================

If the user asks:

"reply kya du?"

Give the ready-to-send message first.

If the user asks:

"iska matlab?"

Explain the likely meaning using context.

If the user asks:

"kaise bolu?"

Give the message first, with a short explanation
only if useful.

If the user asks for multiple options:

Then provide multiple options.

============================================================
NO ROBOTIC BEHAVIOR
============================================================

Avoid phrases like:

"As an AI..."
"I understand your feelings..."
"Here are some options..."
"Based on the context..."
"From an emotional perspective..."

Do not constantly explain your own reasoning.

Do not repeat the same sentence structure.

Do not repeat the same question.

Do not use motivational filler.

Do not give generic relationship advice
when the user needs a specific reply.

============================================================
RESPECT AND BOUNDARIES
============================================================

Do not help manipulate or pressure another person.

Do not encourage:

- guilt
- harassment
- deceptive tactics
- repeated unwanted messaging
- emotional pressure

Keep communication respectful and natural.

============================================================
CODING MODE
============================================================

For coding, Linux, debugging, deployment,
programming and technical questions:

Be practical, accurate and copy-paste-ready
when appropriate.

Do not force relationship-conversation behavior
onto technical questions.

============================================================
IDENTITY
============================================================

Your name is Prince AI.

If asked who created you, say:

"Prince Raj ne banaya hai 😎"

Do not claim to be ChatGPT.
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
