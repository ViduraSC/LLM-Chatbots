import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Define the template for the chatbot conversation
template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer:
"""

# Instantiate the language model and create a prompt template
model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

class ChatBubble(QFrame):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        
        # Set up layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet("background-color: transparent;")  

        # Create a label for the icon
        icon_label = QLabel(self)
        if is_user:
            icon_label.setPixmap(QPixmap("./images/user1.png").scaled(60, 60, Qt.KeepAspectRatio))
            text_align = Qt.AlignLeft
            bubble_color = "#D5F5E3" 
        else:
            icon_label.setPixmap(QPixmap("./images/bot1.png").scaled(60, 60, Qt.KeepAspectRatio))
            text_align = Qt.AlignRight
            bubble_color = "#FDEDEC"

        # Create a label for the chat text
        text_label = QLabel(text, self)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"background-color: {bubble_color}; border-radius: 10px; padding: 10px; color: #333333; font-family: 'Poppins'; font-size: 18px;")
        text_label.setMaximumWidth(1800)  # Set a maximum width to make the bubbles consistent
        text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)  # Adjusted size policy for proper resizing
        
        # Adjust maximum width to control the size of the bubbles
        text_label.setMaximumWidth(1800)  

        # Adjust minimum height to ensure text visibility
        text_label.setMinimumHeight(text_label.sizeHint().height() + 20)
        
        # Add the widgets to the layout
        if is_user:
            self.layout.addWidget(icon_label)
            self.layout.addWidget(text_label, 1, text_align)
        else:
            self.layout.addWidget(text_label, 1, text_align)
            self.layout.addWidget(icon_label)
        
        # Align the layout
        self.setLayout(self.layout)

class ChatBotUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set up the layout
        self.layout = QVBoxLayout()

        # Title area
        self.title_label = QLabel("Vidura's Chat Assistant", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            font-family: 'Poppins';
            font-size: 32px;
            font-weight: bold;
            padding: 15px;
            border-radius: 15px;
            border-bottom: 2px solid #388E3C;
            margin: 10px;
        """)

        # Scroll area for the chat display with rounded corners
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            border: none;
            border-radius: 15px;
            background-color: #f2f5f5;
            margin: 10px;
        """)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)

        # Horizontal layout for input field and send button
        self.input_layout = QHBoxLayout()

        # Input field for the user's message (85% of the width)
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Hi Vidura, ask anything...")
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setStyleSheet("""
            background-color: #FFFFFF;
            color: #333333;
            font-family: 'Poppins';
            font-size: 20px;
            padding: 10px;
            border-radius: 15px;
            margin: 10px;
            border: 2px solid #4CAF50;
        """)
        self.input_layout.addWidget(self.input_field, 85)  # Set the width to 85%

        # Send button (15% of the width)
        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: black;
                font-family: 'Poppins';
                font-size: 20px;
                padding: 10px;
                border-radius: 10px;
                border: none;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        self.input_layout.addWidget(self.send_button, 15)  # Set the width to 15%

        # Add widgets to the layout
        self.layout.addWidget(self.title_label)  # Add the title at the top
        self.layout.addWidget(self.scroll_area)
        self.layout.addLayout(self.input_layout)

        # Set layout for the main window
        self.setLayout(self.layout)

        # Set main window properties
        self.setWindowTitle("Vidura's AI ChatBot")
        self.setGeometry(100, 100, 600, 900)
        self.setStyleSheet("background-color: #ffffff;") ## Main Window Color
        self.show()

        # Initialize conversation context
        self.context = ""

    def send_message(self):
        user_input = self.input_field.text()
        if user_input.strip() == "":
            return

        # Add user's message bubble
        user_bubble = ChatBubble(user_input, is_user=True)
        self.scroll_layout.addWidget(user_bubble)

        self.input_field.clear()

        # Get the chatbot's response by invoking the chain
        result = chain.invoke({"context": self.context, "question": user_input})

        # Add bot's response bubble
        bot_bubble = ChatBubble(result, is_user=False)
        self.scroll_layout.addWidget(bot_bubble)

        # Scroll to the bottom
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

        # Update the context
        self.context += f"\nUser: {user_input}\nAI: {result}"

def main():
    app = QApplication(sys.argv)
    chatbot_ui = ChatBotUI()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
