Syntecxhub_Rule_Based_Chatbot

A simple rule-based chatbot written in Python, built as Project 1 of the Syntecxhub internship. The bot uses pattern matching (regular expressions) to understand what you type or say, answers from a small knowledge base, can talk back using text-to-speech, and can listen to your voice through the microphone.

Features
Pattern matching with Python's re module
Intents: greeting, help, small talk (how are you, name, thanks, jokes, time/date) and goodbye
Rule-based responses: several possible replies per intent, chosen at random
Knowledge base: answers domain questions about databases (SQL, DBMS, primary key, foreign key, joins, normalization, ACID, indexing, transactions, NoSQL, ER diagrams, deadlock)
Interactive console: chat directly in the terminal
Conversation history: every message is saved to conversation_history.txt and conversation_history.json (type history to see it in the chat)
Voice output: the bot speaks its replies (Windows built-in voice / pyttsx3)
Voice input: speak to the bot through your microphone (Google speech recognition)
Works in plain text mode if the voice libraries are not installed
Requirements
Python 3.9 or newer
Optional (for voice): pyttsx3, SpeechRecognition, sounddevice
Internet connection for voice input (speech recognition uses Google's free web service)
Installation
bash
git clone https://github.com/<your-username>/Syntecxhub_Rule_Based_Chatbot.git
cd Syntecxhub_Rule_Based_Chatbot
pip install pyttsx3 SpeechRecognition sounddevice

The voice libraries are optional. Without them the chatbot still works with typing.

How to Run
bash
python chatbot.py

At the start the bot asks two questions:

Enable bot voice (it talks)? (y/n):
Enable microphone (you talk)? (y/n):
Answer y to the first to hear the bot's replies.
Answer y to the second to speak to the bot. At the prompt, press Enter and speak for about 6 seconds, or simply type your message instead.
Commands
Input	What it does
help	Shows what the bot can do
topics	Lists the topics in the knowledge base
history	Shows the conversation so far
bye / exit / quit	Ends the chat
Sample Conversation
DBot: Hi! I'm DBot. Type or say help for options, and bye to quit.
You: hello
DBot: Hello! I'm DBot. How can I help you today?
You: what is a primary key
DBot: A primary key uniquely identifies each row in a table. It cannot be NULL and cannot contain duplicates.
You: explain normalization
DBot: Normalization organizes data into tables to reduce redundancy and anomalies (1NF, 2NF, 3NF, BCNF...).
You: tell me a joke
DBot: A SQL query walks into a bar, sees two tables and asks: 'Can I JOIN you?'
You: bye
DBot: Goodbye! Have a great day!
Project Structure
Syntecxhub_Rule_Based_Chatbot/
├── chatbot.py                    # the chatbot
├── README.md                     # this file
├── conversation_history.txt      # created automatically (readable log)
└── conversation_history.json     # created automatically (structured log)
How It Works
The user's message (typed or spoken) is converted to lowercase.
The bot first checks the knowledge base for a matching keyword.
If nothing matches, it checks the intent patterns (regular expressions).
If still nothing matches, it gives a fallback reply.
Both the user's message and the bot's reply are written to the history files.
Customizing the Bot
Add knowledge: add a new entry to the KNOWLEDGE_BASE dictionary in chatbot.py.
Add an intent: add a new item to the INTENTS dictionary with its patterns and responses.
Change the domain: replace the database topics with any subject you like (for example, a university or a shop).
Troubleshooting
Problem	Solution
Bot does not ask about voice	You are running an old copy of the file. Use the latest chatbot.py.
pip install pyaudio fails on newer Python versions	Not needed. This project uses sounddevice instead of PyAudio.
Microphone does not work	Allow microphone access in Windows: Settings → Privacy & security → Microphone.
"Couldn't understand that"	Speak clearly, right after "Listening", in a quiet room, and make sure you are online.
Bot is silent	Check your volume. Any (Voice error: ...) message printed in the console shows the cause.
Author

Eman Jamil — BS Computer Science Syntecxhub Internship, Project 1: Simple Rule-Based Chatbot
