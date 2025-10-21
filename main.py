# --- main.py ---
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
import datetime
import random
import threading

# We need to install googlesearch-python in Colab, so we try to import it
try:
    from googlesearch import search
    GOOGLE_SEARCH_ENABLED = True
except ImportError:
    GOOGLE_SEARCH_ENABLED = False

kivy.require('2.0.0')

# --- THE PROTO-JARVIS BRAIN ---
def understand_intent(command):
    command = command.lower()
    if "hello" in command or "hi" in command: return "greeting"
    elif "what time is it" in command: return "get_time"
    elif "tell me a joke" in command: return "tell_joke"
    elif "search for" in command and GOOGLE_SEARCH_ENABLED: return "search_web"
    else: return "unknown"

def skill_greeting():
    return "Hello! How can I assist you today?"

def skill_get_time():
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."

def skill_tell_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What do you call a fake noodle? An Impasta!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!"
    ]
    return random.choice(jokes)

def skill_search_web(command):
    try:
        query = command.split("search for", 1)[1].strip()
        results = list(search(query, num_results=3))
        response = f"Here are the top 3 results for '{query}':\n"
        for i, url in enumerate(results):
            response += f"{i+1}. {url}\n"
        return response
    except Exception as e:
        return f"I'm sorry, my web search module encountered an error: {e}"

# --- THE KIVY GUI APPLICATION ---
class JarvisApp(App):
    def build(self):
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.chat_history = ScrollView(size_hint_y=1)
        self.chat_log = Label(
            size_hint_y=None, markup=True, font_size='16sp',
            text="[color=00ff00]Jarvis: Hello! How can I help?[/color]",
            halign='left', valign='top', padding=(10, 10)
        )
        self.chat_log.bind(texture_size=self.chat_log.setter('size'))
        self.chat_history.add_widget(self.chat_log)
        self.main_layout.add_widget(self.chat_history)

        input_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.text_input = TextInput(multiline=False, on_text_validate=self.send_message)
        self.send_button = Button(text="Send", size_hint_x=None, width=100)
        self.send_button.bind(on_press=self.send_message)
        
        input_layout.add_widget(self.text_input)
        input_layout.add_widget(self.send_button)
        self.main_layout.add_widget(input_layout)

        return self.main_layout

    def send_message(self, instance):
        user_command = self.text_input.text
        if not user_command: return

        self.add_message(f"[color=ffffff]You: {user_command}[/color]")
        self.text_input.text = ""

        # Run the AI logic in a separate thread to prevent the app from freezing during a web search
        threading.Thread(target=self.process_command, args=(user_command,)).start()

    def process_command(self, command):
        intent = understand_intent(command)
        if intent == "greeting": response = skill_greeting()
        elif intent == "get_time": response = skill_get_time()
        elif intent == "tell_joke": response = skill_tell_joke()
        elif intent == "search_web": response = skill_search_web(command)
        else: response = "I'm sorry, I don't understand that command yet."
        
        # We need to schedule the UI update on the main Kivy thread
        Clock.schedule_once(lambda dt: self.add_message(f"[color=00ff00]Jarvis: {response}[/color]"))

    def add_message(self, message):
        self.chat_log.text += f"\n{message}"
        # Scroll to the bottom
        self.chat_history.scroll_y = 0

if __name__ == '__main__':
    JarvisApp().run()
