import tkinter as tk
import os
from dotenv import load_dotenv

load_dotenv()

class ChatInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(os.getenv('CHAT_WINDOW_TITLE', "Simple Chat Interface"))
        
        # Get window dimensions from environment variables or use defaults
        window_width = int(os.getenv('CHAT_WINDOW_WIDTH', 400))
        window_height = int(os.getenv('CHAT_WINDOW_HEIGHT', 500))
        
        # Create chat display
        self.chat_display = tk.Text(self, state="disabled", height=window_height//20, width=window_width//10)
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        # Create input field
        self.input_field = tk.Entry(self, width=window_width//12)
        self.input_field.grid(row=1, column=0, padx=5, pady=5)
        self.input_field.bind("<Return>", self.send_message)
        
        # Create send button
        self.send_button = tk.Button(self, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=5, pady=5)
        
    def send_message(self, event=None):
        message = self.input_field.get()
        self.chat_display.config(state="normal")
        self.chat_display.insert("end", "You: " + message + "\n")
        self.chat_display.config(state="disabled")
        self.input_field.delete(0, "end")
        
        # Add logic to process the message and generate a response
        response = "This is a sample response."
        self.chat_display.config(state="normal")
        self.chat_display.insert("end", "Bot: " + response + "\n")
        self.chat_display.config(state="disabled")

if __name__ == "__main__":
    app = ChatInterface()
    app.mainloop()
