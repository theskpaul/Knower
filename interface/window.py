# import subprocess
import os
import shutil

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from default import PATH
from interface.models import create_tables
from logger import log as l

create_tables()

from core.helper.config import load_config
from core.pipeline.model_manager import ModelManager, getOllamaModelList
from default import DEFAULT_CONFIG
from interface.chat import (
    add_message,
    create_conversation,
    get_conversations,
    get_messages,
    update_conversation_title,
)


@l("Get list of language models")
def get_language_models() -> dict:
    llms = {}
    model_list = getOllamaModelList()

    if model_list:
        for model in model_list:
            if (
                "completion" in model.capabilities
                and "embedding" not in model.capabilities
            ):
                llms[model.name] = model.model

    return llms


language_models = get_language_models()

config = load_config()
local_lm_entry: str = config.get("LANGUAGE_MODEL", DEFAULT_CONFIG["LANGUAGE_MODEL"])

local_em_entry = config.get("EMBEDDING_MODEL", DEFAULT_CONFIG["EMBEDDING_MODEL"])

model_manager = ModelManager(
    language_model=local_lm_entry, embedding_model=local_em_entry
)


class APPWindow(QWidget):
    @l("Load APPWindow __init__ function")
    def __init__(self):
        super().__init__()

        self.LLM_Models = get_language_models()
        self.current_chat = None  # <-- Add this line
        self.rank_search: bool = False
        self.setWindowTitle("Knower")
        self.setMinimumSize(400, 550)
        self.showMaximized()

        self.build_ui()

        self.load_chat_history()
        self.update_model_info(local_lm_entry)
        self._process_btn_original_style: str = str(self.process_btn.styleSheet)

    def update_model_info(self, model):
        model_name: str = self.LLM_Models.get(model, "")

        if model_name:
            self.model_box.setCurrentIndex(self.model_box.findText(model_name))
        else:
            self.model_box.setEnabled(False)
            self.send.setEnabled(False)
            self.input_box.setEnabled(False)
            self.search_mode.setEnabled(False)
            self.title.setText("No Connection Found!!!")

    def load_chat_history(self):
        from PySide6.QtWidgets import QListWidgetItem

        self.history.clear()
        chats = get_conversations()
        for chat in chats:
            item = QListWidgetItem(chat["title"])
            item.setData(Qt.ItemDataRole.UserRole, chat["id"])
            self.history.addItem(item)

    def open_chat(self, item):
        self.clear_chat()
        chat_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_chat = chat_id
        messages = get_messages(chat_id)
        for message in messages:
            self.add_message(message["role"], message["content"])

    def active_mode(self):
        self.process_btn.setText("Processing...")
        self.process_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                }
            """)

    def deactive_mode(self):
        self.process_btn.setText("Process Documents")
        self.process_btn.setStyleSheet(self._process_btn_original_style)

    @l("Upload documents")
    def upload_document(self):
        from PySide6.QtWidgets import QFileDialog

        file_list, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Document",
            "",
            "All Supported Files (*.txt *.pdf);;Text Files (*.txt);;PDF Files (*.pdf)",
        )

        for source in file_list:
            if source:
                # Create the upload folder if it doesn't exist
                upload_folder = PATH["sources"]
                upload_folder.mkdir(parents=True, exist_ok=True)

                name = os.path.basename(source)
                destination = upload_folder / name

                if os.path.exists(destination):
                    print(f"Skipped (Already in place): {source}")
                    continue

                shutil.copy2(source, destination)
                print(f"Original: {source}")
                print(f"Saved as: {destination}")

    @l("Process uploaded documents")
    def process_documents(self):
        from PySide6.QtCore import QThread

        from interface.worker import DocumentProcessor

        self.doc_thread = QThread()
        self.doc_worker = DocumentProcessor(model_manager=model_manager)

        self.doc_worker.moveToThread(self.doc_thread)

        self.doc_thread.started.connect(self.active_mode)
        self.doc_thread.started.connect(self.doc_worker.process)
        self.doc_worker.finished.connect(self.deactive_mode)
        self.doc_worker.error.connect(self.deactive_mode)

        self.doc_worker.finished.connect(self.doc_thread.quit)
        self.doc_worker.finished.connect(self.doc_worker.deleteLater)

        self.doc_thread.finished.connect(self.doc_thread.deleteLater)

        self.doc_thread.start()

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
        from PySide6.QtWidgets import QHBoxLayout, QLabel

        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(800)

        layout = QHBoxLayout()

        if sender == "user":
            bubble.setStyleSheet("""
                QLabel{
                    background:#3B82F6;
                    color:white;
                    border-radius:12px;
                    padding:10px;
                    font-size: 16px;
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
                    font-size: 16px;
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
        self.send.setEnabled(True)
        self.remove_last_message()  # remove "Thinking..."
        self.add_message("ai", reply)
        add_message(self.current_chat, "assistant", reply)

    def show_error(self, error):
        self.send.setEnabled(True)
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

    @l("Send message")
    def send_message(self):
        from PySide6.QtCore import QThread

        from core.helper.config import add_entry
        from interface.worker import ChatWorker

        query = self.input_box.toPlainText().strip()

        selected_type = self.model_box.currentText()
        add_entry("LANGUAGE_MODEL", selected_type)
        selected_model = self.LLM_Models.get(selected_type, "No Model Found")

        if not query:
            return

        self.send.setEnabled(False)

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
            self.load_chat_history()

        self.input_box.clear()

        # Show temporary AI message
        self.add_message("ai", "Thinking...")

        # Create thread
        self.chat_thread = QThread()

        model_manager.large_language_model = selected_model
        self.chat_worker = ChatWorker(
            query=query, model_manager=model_manager, rank_search=self.rank_search
        )

        # Move worker to thread
        self.chat_worker.moveToThread(self.chat_thread)

        # Connect signals
        self.chat_thread.started.connect(self.chat_worker.run)
        self.chat_worker.finished.connect(self.show_reply)
        self.chat_worker.error.connect(self.show_error)

        # Clean up
        self.chat_worker.finished.connect(self.chat_thread.quit)
        self.chat_worker.finished.connect(self.chat_worker.deleteLater)
        self.chat_thread.finished.connect(self.chat_thread.deleteLater)

        # Start
        self.chat_thread.start()

    def new_chat(self):
        self.clear_chat()
        self.current_chat = None

    def change_search_mode(self, checked):
        if checked:
            self.rank_search = True
            self.search_mode.setText("Think Longer")
        else:
            self.rank_search = False
            self.search_mode.setText("Normal Search")

    def show_uploaded_docs(self):
        import os

        from PySide6.QtWidgets import QDialog, QListWidget, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Uploaded Documents")
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)
        doc_list = QListWidget()

        for filename in os.listdir(PATH["sources"]):
            doc_list.addItem(filename)

        layout.addWidget(doc_list)
        dialog.exec()

    @l("Build a UI")
    def build_ui(self):
        from PySide6.QtWidgets import (
            QComboBox,
            QFrame,
            QHBoxLayout,
            QLabel,
            QListWidget,
            QPushButton,
            QScrollArea,
            QTextEdit,
            QVBoxLayout,
        )

        # ===== Main Layout =====
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =============== Sidebar creation  ==================
        sidebar = QFrame()
        sidebar.setFixedWidth(320)
        sidebar.setStyleSheet(
            """ QFrame{ background:#161B22; border-right:1px solid #374151;} """
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )  # All the element set to vertical alignments
        sidebar_layout.setContentsMargins(15, 15, 15, 15)

        logo = QLabel("Knower")  # add the title here; top of the side bar
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(""" color:white; font-size:24px; font-weight:bold; """)

        self.new_chat_btn = QPushButton("+ New Chat")
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

        list_documents_btn = QPushButton("Documents")
        list_documents_btn.clicked.connect(self.show_uploaded_docs)

        upload_btn = QPushButton("Upload Documents")
        upload_btn.clicked.connect(self.upload_document)

        self.process_btn = QPushButton("Process Documents")
        self.process_btn.clicked.connect(self.process_documents)

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

        # Document Label
        document_label = QLabel("Manage Documents")
        document_label.setStyleSheet("""
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

        sidebar_layout.addWidget(document_label)
        sidebar_layout.addWidget(list_documents_btn)
        sidebar_layout.addWidget(upload_btn)
        sidebar_layout.addWidget(self.process_btn)

        # =========== Right Side =============
        right = QFrame()
        right.setStyleSheet("""
            QFrame{
                background:#20252B;
            }
        """)

        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(25, 20, 25, 20)

        self.title = QLabel("How can I help you today?")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("""
            color:#F8FAFC;
            font-size:28px;
            font-weight:bold;
        """)

        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
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

        self.search_mode = QPushButton("Normal Search")
        self.search_mode.setCheckable(True)
        self.search_mode.setStyleSheet("""
            QPushButton:checked {
                background-color: #f44336;
                color: #FFFFFF;
            }
            QPushButton:!checked {
                background-color: #4CAF50;
                color: #000000;
            }
        """)

        self.search_mode.toggled.connect(self.change_search_mode)

        bottom = QHBoxLayout()
        self.model_box = QComboBox()
        added = False
        for display_name in self.LLM_Models:
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
        bottom.addWidget(self.search_mode)
        model_layout.addWidget(self.model_box)

        bottom.addLayout(model_layout)
        bottom.addWidget(self.send)
        bottom.addStretch()

        right_layout.addWidget(self.title)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.chat)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.input_box)
        right_layout.addLayout(bottom)

        # ==================================================
        main_layout.addWidget(sidebar)
        main_layout.addWidget(right)
