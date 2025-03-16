import cv2
import face_recognition
import sqlite3
import numpy as np
import pickle
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, 
    QMessageBox, QInputDialog
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

# Database setup
db_path = 'face_recognition.db'

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    name TEXT,
                    age INTEGER,
                    email TEXT,
                    face_encoding BLOB
                 )''')
    conn.commit()
    conn.close()

def load_users_from_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name, face_encoding FROM users")
    users = {}
    for row in c.fetchall():
        name, encoding_blob = row
        encoding = pickle.loads(encoding_blob)
        users[name] = encoding
    conn.close()
    return users

def save_user_to_db(name, age, email, encoding):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    encoding_blob = pickle.dumps(encoding)
    c.execute("INSERT INTO users (name, age, email, face_encoding) VALUES (?, ?, ?, ?)", 
              (name, age, email, encoding_blob))
    conn.commit()
    conn.close()

def delete_user_from_db(name):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE name = ?", (name,))
    conn.commit()
    conn.close()

# Initialize the database
init_db()

class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition App")
        self.setGeometry(100, 100, 800, 600)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.recognition_loop)

        # Load users from database at startup
        self.users = load_users_from_db()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        layout.addWidget(self.video_label)

        register_button = QPushButton("Register Face", self)
        register_button.clicked.connect(self.register_user)
        layout.addWidget(register_button)

        recognize_button = QPushButton("Start Real-Time Recognition", self)
        recognize_button.clicked.connect(self.start_recognition)
        layout.addWidget(recognize_button)

        delete_button = QPushButton("Delete User", self)
        delete_button.clicked.connect(self.delete_user)
        layout.addWidget(delete_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def register_user(self):
        name, ok = QInputDialog.getText(self, "Register User", "Enter your name:")
        if not ok or not name:
            QMessageBox.warning(self, "Input Error", "Please enter a valid name.")
            return

        age, ok = QInputDialog.getInt(self, "Register User", "Enter your age:")
        if not ok:
            return

        email, ok = QInputDialog.getText(self, "Register User", "Enter your email:")
        if not ok or not email:
            return

        # Capture a single frame from the video
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        self.cap.release()

        if not ret:
            QMessageBox.warning(self, "Error", "Failed to capture image for registration.")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_frame)

        if encodings:
            encoding = encodings[0]
            save_user_to_db(name, age, email, encoding)
            self.users[name] = encoding
            QMessageBox.information(self, "Success", f"User '{name}' registered successfully.")
        else:
            QMessageBox.warning(self, "Error", "No face detected in the captured image.")

    def start_recognition(self):
        if not self.users:
            QMessageBox.warning(self, "Error", "No registered users found.")
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.warning(self, "Error", "Failed to open camera.")
            return

        self.timer.start(20)

    def recognition_loop(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding, (top, right, bottom, left) in zip(encodings, face_locations):
            name = "Unknown"
            for user_name, user_encoding in self.users.items():
                matches = face_recognition.compare_faces([user_encoding], encoding)
                if True in matches:
                    name = user_name
                    print(1)  # Print 1 when a registered user is detected
                    break

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        converted_frame = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(converted_frame))

    def delete_user(self):
        name, ok = QInputDialog.getText(self, "Delete User", "Enter the name of the user to delete:")
        if not ok or not name:
            return

        if name not in self.users:
            QMessageBox.warning(self, "Error", f"No user found with the name '{name}'.")
            return

        # Delete from database
        delete_user_from_db(name)
        del self.users[name]
        QMessageBox.information(self, "Success", f"User '{name}' has been deleted successfully.")

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec_())
