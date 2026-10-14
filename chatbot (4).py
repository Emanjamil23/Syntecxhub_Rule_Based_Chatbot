
import json
import random
import re
from datetime import datetime

# Optional voice libraries (bot still works in text mode if they're missing)
try:
    import pyttsx3                      # text-to-speech (bot talks)
except ImportError:
    pyttsx3 = None

try:
    import win32com.client              # Windows built-in speech (SAPI), installed with pyttsx3
except Exception:
    win32com = None

SR_ERROR = ""
try:
    import speech_recognition as sr     # speech-to-text (you talk)
except Exception as e:                  # show the real reason if it fails
    sr = None
    SR_ERROR = str(e)

SD_ERROR = ""
try:
    import sounddevice as sd            # microphone recording (no PyAudio needed)
except Exception as e:
    sd = None
    SD_ERROR = repr(e)

BOT_NAME = "DBot"
LOG_JSON = "conversation_history.json"
LOG_TXT = "conversation_history.txt"

# ---------------------------------------------------------------- intents
# Each intent: list of regex patterns + list of possible responses.
INTENTS = {
    "greeting": {
        "patterns": [r"\b(hi|hello|hey|salam|assalam\w*|good (morning|afternoon|evening))\b"],
        "responses": [
            "Hello! I'm {bot}. How can I help you today?",
            "Hi there! Ask me anything about databases or type 'help'.",
        ],
    },
    "help": {
        "patterns": [r"\bhelp\b", r"what can you do", r"\bcommands?\b"],
        "responses": [
            "I can chat, answer database/CS questions (try 'what is SQL?', "
            "'explain normalization', 'define primary key'), and tell the time. "
            "Type 'history' to see our conversation, 'topics' for the list "
            "of things I know, or 'bye' to exit."
        ],
    },
    "how_are_you": {
        "patterns": [r"how are you", r"how('s| is) it going", r"what'?s up"],
        "responses": [
            "I'm just code, but I'm running great! How about you?",
            "Doing well, thanks for asking!",
        ],
    },
    "name": {
        "patterns": [r"your name", r"who are you"],
        "responses": ["I'm {bot}, a simple rule-based chatbot written in Python."],
    },
    "thanks": {
        "patterns": [r"\b(thanks|thank you|thx|shukriya)\b"],
        "responses": ["You're welcome!", "Happy to help!", "Anytime!"],
    },
    "joke": {
        "patterns": [r"\bjoke\b", r"make me laugh"],
        "responses": [
            "Why did the developer quit? Because he didn't get arrays. 😄",
            "A SQL query walks into a bar, sees two tables and asks: 'Can I JOIN you?'",
        ],
    },
    "time": {
        "patterns": [r"\b(time|date|day)\b"],
        "responses": ["It is {now}."],
    },
    "goodbye": {
        "patterns": [r"\b(bye|goodbye|exit|quit|see you)\b"],
        "responses": ["Goodbye! Have a great day!", "Bye! Talk to you soon."],
    },
}

# -------------------------------------------------------- knowledge base
# keyword(s) -> answer. Easy to extend: just add more entries.
KNOWLEDGE_BASE = {
    ("sql",): "SQL (Structured Query Language) is the standard language used to create, "
              "query, update and manage data in relational databases.",
    ("dbms", "database management system"): "A DBMS is software that stores, organizes and "
              "manages data and lets users/applications access it safely (e.g. MySQL, PostgreSQL, Oracle).",
    ("primary key",): "A primary key uniquely identifies each row in a table. It cannot be NULL "
              "and cannot contain duplicates.",
    ("foreign key",): "A foreign key is a column that refers to the primary key of another table, "
              "creating a relationship between the two tables.",
    ("normalization", "normalisation"): "Normalization organizes data into tables to reduce "
              "redundancy and anomalies (1NF, 2NF, 3NF, BCNF...).",
    ("acid",): "ACID = Atomicity, Consistency, Isolation, Durability - the properties that "
              "guarantee reliable database transactions.",
    ("index", "indexing"): "An index is a data structure (often a B-tree) that speeds up "
              "data retrieval at the cost of extra storage and slower writes.",
    ("join", "joins"): "A JOIN combines rows from two or more tables based on a related column. "
              "Types: INNER, LEFT, RIGHT, FULL.",
    ("transaction", "transactions"): "A transaction is a group of operations executed as a single "
              "unit: either all succeed (COMMIT) or all are undone (ROLLBACK).",
    ("nosql",): "NoSQL databases (MongoDB, Redis, Cassandra...) store data in non-tabular models "
              "like documents, key-value, graph or column families.",
    ("er diagram", "erd"): "An ER (Entity-Relationship) diagram models entities, their attributes "
              "and the relationships between them before designing tables.",
    ("deadlock",): "A deadlock happens when two transactions wait for each other's locks forever. "
              "The DBMS detects it and aborts one transaction.",
}

FALLBACKS = [
    "Sorry, I didn't understand that. Type 'help' to see what I can do.",
    "Hmm, I don't know that yet. Try asking about SQL, keys, joins or normalization.",
    "I'm a simple bot - could you rephrase that?",
]

# -------------------------------------------------------------- logging
history = []  # list of {"time", "speaker", "message"}


def log(speaker, message):
    entry = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "speaker": speaker, "message": message}
    history.append(entry)
    with open(LOG_TXT, "a", encoding="utf-8") as f:
        f.write(f"[{entry['time']}] {speaker}: {message}\n")
    with open(LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def show_history():
    if not history:
        return "No conversation yet."
    return "\n".join(f"  [{h['time']}] {h['speaker']}: {h['message']}" for h in history[:-1]) \
        or "No earlier messages."


# ------------------------------------------------------------- matching
def search_knowledge(text):
    """Return an answer if any knowledge-base keyword appears in the text."""
    for keywords, answer in KNOWLEDGE_BASE.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text):
                return answer
    return None


def list_topics():
    topics = ", ".join(sorted(k[0] for k in KNOWLEDGE_BASE))
    return f"I know about: {topics}."


def match_intent(text):
    for name, intent in INTENTS.items():
        for pattern in intent["patterns"]:
            if re.search(pattern, text):
                return name
    return None


def get_response(user_input):
    text = user_input.lower().strip()

    if text == "history":
        return show_history(), False
    if text == "topics":
        return list_topics(), False

    # 1) knowledge-base questions take priority (e.g. "what is the time complexity of an index?")
    answer = search_knowledge(text)
    if answer:
        return answer, False

    # 2) intents
    intent = match_intent(text)
    if intent:
        response = random.choice(INTENTS[intent]["responses"]).format(
            bot=BOT_NAME, now=datetime.now().strftime("%A, %d %B %Y, %I:%M %p"))
        return response, intent == "goodbye"

    # 3) fallback
    return random.choice(FALLBACKS), False


# ---------------------------------------------------------------- voice
class Voice:
    RATE = 16000          # sample rate for recording
    SECONDS = 6           # how long we listen each time

    def __init__(self, speak_on=False, mic_on=False):
        self.recognizer = None
        self.sapi = None
        self.speak_on = False
        if speak_on:
            if win32com:
                try:
                    self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
                    self.sapi.Rate = 1          # slightly faster than default
                    self.speak_on = True
                except Exception:
                    self.sapi = None
            if not self.sapi and pyttsx3:
                self.speak_on = True
            if not self.speak_on:
                print("(Install pyttsx3 for voice output: pip install pyttsx3)")

        if mic_on:
            if not sr:
                print(f"(Mic needs SpeechRecognition. Problem: {SR_ERROR or 'not installed'})")
            elif not sd:
                print(f"(Mic needs sounddevice. Real problem: {SD_ERROR})")
                print("(Tip: move this file to its own empty folder, e.g. C:\\chatbot, and run it from there)")
            else:
                self.recognizer = sr.Recognizer()

    def say(self, text):
        """Speak text aloud (emojis / symbols removed so they aren't read out)."""
        if not self.speak_on:
            return
        clean = re.sub(r"[^\x00-\x7F]+", "", text)
        try:
            if self.sapi:
                self.sapi.Speak(clean)              # waits until finished
            else:
                # new engine every time: reusing one stays silent after the first reply
                engine = pyttsx3.init()
                engine.setProperty("rate", 170)
                engine.say(clean)
                engine.runAndWait()
                engine.stop()
        except Exception as e:
            print(f"(Voice error: {e})")

    def listen(self):
        """Record from the microphone for a few seconds and convert speech to text."""
        if not self.recognizer:
            return ""
        try:
            print(f"🎤 Listening for {self.SECONDS} seconds... speak now!")
            frames = int(self.RATE * self.SECONDS)
            with sd.RawInputStream(samplerate=self.RATE, channels=1, dtype="int16") as stream:
                data, _ = stream.read(frames)
            audio = sr.AudioData(bytes(data), self.RATE, 2)
            print("...processing")
            text = self.recognizer.recognize_google(audio)   # needs internet
            print(f"You (voice): {text}")
            return text
        except sr.UnknownValueError:
            print("(Sorry, I couldn't understand that - try again)")
        except sr.RequestError as e:
            print(f"(Speech service error - check internet: {e})")
        except Exception as e:
            print(f"(Microphone problem: {e}) - falling back to typing")
            self.recognizer = None
        return ""


def ask_yes_no(question):
    return input(question + " (y/n): ").strip().lower().startswith("y")


# ----------------------------------------------------------------- main
def main():
    voice = Voice(speak_on=ask_yes_no("Enable bot voice (it talks)?"),
                  mic_on=ask_yes_no("Enable microphone (you talk)?"))

    greeting = f"Hi! I'm {BOT_NAME}. Type or say help for options, and bye to quit."
    print(f"{BOT_NAME}: {greeting}")
    voice.say(greeting)
    log(BOT_NAME, "Session started")

    while True:
        try:
            if voice.recognizer:
                # Press Enter to speak, or type your message directly
                typed = input("You (press Enter to speak, or type): ").strip()
                user_input = typed if typed else voice.listen()
            else:
                user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{BOT_NAME}: Goodbye!")
            break
        if not user_input:
            continue
        log("You", user_input)
        reply, should_exit = get_response(user_input)
        print(f"{BOT_NAME}: {reply}")
        voice.say(reply)
        log(BOT_NAME, reply)
        if should_exit:
            break


if __name__ == "__main__":
    main()
