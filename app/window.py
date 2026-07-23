# import subprocess
import os
import shutil
from datetime import datetime

from PySide6.QtCore import Qt, QThread  # , QObject, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QListWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.worker import ChatWorker
from app.models import create_tables

create_tables()

from app.chat import (
    add_message,
    create_conversation,
    get_conversations,
    get_messages,
    update_conversation_title,
)


class APPWindow(QWidget):
    def __init__(self, LLM_Models: dict, Embedding_Model: dict):
        super().__init__()
        self.LLM_Models = LLM_Models
        self.Embedding_Model = Embedding_Model
        self.current_chat = None  # <-- Add this line
        self.setWindowTitle("Knower")
        self.setMinimumSize(400, 550)
        self.showMaximized()

        self.build_ui()

        self.load_chat_history()
        def update_model_info(self, model):
            model_name = LLM_Models.get(model, "❓ Unknown")
            self.model_info.setText(model_name)

    def load_chat_history(self):
        self.history.clear()
        chats = get_conversations()
        for chat in chats:
            item = QListWidgetItem(chat["title"])
            item.setData(Qt.UserRole, chat["id"])
            self.history.addItem(item)

    def open_chat(self, item):
        self.clear_chat()
        chat_id = item.data(Qt.UserRole)
        self.current_chat = chat_id
        messages = get_messages(chat_id)
        for message in messages:
            self.add_message(
                message["role"],
                message["content"]
            )

    # Upload data sheet to increase compalibility
    def upload_document(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Document",
            "",
            "Documents (*.pdf *.doc *.docx);;PDF Files (*.pdf);;Word Files (*.doc *.docx)",
        )

        if file_name:
            # Create the upload folder if it doesn't exist
            upload_folder = "documents"
            os.makedirs(upload_folder, exist_ok=True)

            # Get original filename and extension
            base = os.path.splitext(os.path.basename(file_name))[0]
            ext = os.path.splitext(file_name)[1]

            # Add timestamp to the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{base}_{timestamp}{ext}"

            # Destination path
            destination = os.path.join(upload_folder, new_name)

            # Copy the file
            shutil.copy2(file_name, destination)  # copy2 preserves metadata

            print(f"Original: {file_name}")
            print(f"Saved as: {destination}")

    # Upload supportin material
    def upload_attachment(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Document",
            "",
            "Documents (*.pdf *.doc *.docx);;PDF Files (*.pdf);;Word Files (*.doc *.docx)",
        )
        if file_name:
            print(file_name)

    def clear_chat(self):
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)

            # Remove widget
            if item.widget():
                item.widget().deleteLater()

            # Remove nested layout (your QHBoxLayout)
            elif item.layout():
                row = item.layout()
                while row.count():
                    child = row.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                row.deleteLater()
            # Clear the input box
        self.input_box.clear()

        # If you store conversation history, clear it too
        self.messages = []

    def add_message(self, sender, message):
        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(500)

        layout = QHBoxLayout()

        if sender == "user":
            bubble.setStyleSheet("""
                QLabel{
                    background:#3B82F6;
                    color:white;
                    border-radius:12px;
                    padding:10px;
                }
            """)

            layout.addStretch()
            layout.addWidget(bubble)

        else:
            bubble.setStyleSheet("""
                QLabel{
                    background:#2A3038;
                    color:white;
                    border-radius:12px;
                    padding:10px;
                }
            """)

            layout.addWidget(bubble)
            layout.addStretch()

        self.chat_layout.addLayout(layout)

    def clear_last_message(self):
        if self.chat_layout.count():
            item = self.chat_layout.takeAt(self.chat_layout.count() - 1)

            if item.layout():
                row = item.layout()
                while row.count():
                    child = row.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                row.deleteLater()

    def show_reply(self, reply):
        self.remove_last_message()      # remove "Thinking..."
        self.add_message("ai", reply)
        add_message(
            self.current_chat,
            "assistant",
            reply
        )

    def show_error(self, error):
        self.remove_last_message()
        self.add_message("ai", f"Error: {error}")

    def remove_last_message(self):
        if self.chat_layout.count() == 0:
            return

        item = self.chat_layout.takeAt(self.chat_layout.count() - 1)

        if item.layout():
            row = item.layout()

            while row.count():
                child = row.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            row.deleteLater()

    def send_message(self):
        query = self.input_box.toPlainText().strip()
        selected_type = self.model_box.currentText()
        selected_model = self.LLM_Models[selected_type]

        if not query:
            return

        new_chat = False
        if self.current_chat is None:
            self.current_chat = create_conversation("New Chat")
            new_chat = True

        # Show user message immediately
        self.add_message("user", query)
        # this add function used for database
        add_message(self.current_chat, "user", query)
        if new_chat:
            update_conversation_title(self.current_chat, query[:40])
            # self.load_chat_history()

        self.input_box.clear()
        # Show temporary AI message
        self.add_message("ai", "Thinking...")

        # Create thread
        self.thread = QThread()

        # Create worker
        self.worker = ChatWorker(
            selected_model,
            embedding_model=self.Embedding_Model["BGE-Base-en-v1.5-GGUF"],
            query=query,
        )

        # Move worker to thread
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.show_reply)
        self.worker.error.connect(self.show_error)

        # Clean up
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start
        self.thread.start()

    def new_chat(self):
        self.clear_chat()
        self.current_chat = None

    def build_ui(self):

        # ===== Main Layout =====
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =============== Sidebar creation  ==================
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet(
            """ QFrame{ background:#161B22; border-right:1px solid #374151;} """
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )  # All the element set to vertical alignments
        sidebar_layout.setContentsMargins(15, 15, 15, 15)

        logo = QLabel("Knower")  # add the title here; top of the side bar
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(""" color:white; font-size:24px; font-weight:bold; """)

        self.new_chat_btn = QPushButton(
            "+ New Chat"
        )  # add abutton that create new chat
        self.new_chat_btn.clicked.connect(self.new_chat)
        self.history = QListWidget()  # crearte the history section
        self.history.itemClicked.connect(self.open_chat)
        self.history.setStyleSheet("""
            QListWidget {
                background-color: #2B2B2B;
                color: white;
                font-size: 15px;
                border: none;
                outline: 0;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #3A6EA5;
                color: white;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
        """)
        self.history.setWordWrap(True)

        upload_btn = QPushButton("📄 Upload Document")  # add a button that take dataset
        upload_btn.clicked.connect(self.upload_document)

        # Logo
        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(15)

        # New Chat Button
        sidebar_layout.addWidget(self.new_chat_btn)
        sidebar_layout.addSpacing(20)

        # Recent Chats Label
        recent_label = QLabel("Recent Chats")
        recent_label.setStyleSheet("""
            QLabel{
                color: #B0B3B8;
                font-size: 14px;
                font-weight: bold;
                padding-left: 5px;
            }
        """)

        sidebar_layout.addWidget(recent_label)
        sidebar_layout.addSpacing(8)

        # Chat History
        sidebar_layout.addWidget(self.history)

        # Push Upload Button to Bottom
        sidebar_layout.addStretch()

        sidebar_layout.addWidget(upload_btn)

        # =========== Right Side =============
        right = QFrame()
        right.setStyleSheet("""
            QFrame{
                background:#20252B;
            }
        """)

        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("How can I help you today?")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color:#F8FAFC;
            font-size:28px;
            font-weight:bold;
        """)

        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)

        chat_container = QWidget()
        chat_container.setLayout(self.chat_layout)

        self.chat = QScrollArea()
        self.chat.setWidgetResizable(True)
        self.chat.setWidget(chat_container)

        self.chat.setStyleSheet("""
            QScrollArea{
                background:#0D1117;
                border:1px solid #374151;
                border-radius:10px;
            }
        """)

        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(90)
        self.input_box.setStyleSheet("""
            QTextEdit{
                background:#161B22;
                color:#FFFFFF;
                border:2px solid #374151;
                border-radius:12px;
                padding:10px;
                font-size:14px;
            }

            QTextEdit:focus{
                border:2px solid #3B82F6;
            }
        """)
        self.input_box.setPlaceholderText("Message Knower AI...")

        attach = QPushButton("📎")
        attach.clicked.connect(self.upload_attachment)
        bottom = QHBoxLayout()
        self.model_box = QComboBox()
        added = False
        for display_name, model_name in self.LLM_Models.items():
            # if model_name in installed_models:
                self.model_box.addItem(display_name)
                added = True
        if not added:
            self.model_box.addItem("No Models Found")

        self.send = QPushButton("Send")
        self.send.clicked.connect(self.send_message)
        self.send.setStyleSheet("""
            QPushButton{
                background:#3B82F6;
                color:white;
                border:none;
                border-radius:8px;
                padding:8px 18px;
                font-weight:bold;
            }

            QPushButton:hover{
                background:#2563EB;
            }

            QPushButton:pressed{
                background:#1D4ED8;
            }
        """)

        model_layout = QVBoxLayout()
        bottom.addWidget(attach)
        model_layout.addWidget(self.model_box)

        bottom.addLayout(model_layout)
        bottom.addWidget(self.send)
        bottom.addStretch()

        right_layout.addWidget(title)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.chat)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.input_box)
        right_layout.addLayout(bottom)

        # ==================================================
        main_layout.addWidget(sidebar)
        main_layout.addWidget(right)
