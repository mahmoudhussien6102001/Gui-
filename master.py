import os
import socket
import threading
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QListWidget, QVBoxLayout, QWidget, QMessageBox

slave_connections = []
mutex = threading.Lock()

class MasterControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Master Control")
        self.setGeometry(100, 100, 400, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.conn_label = QLabel("")
        self.shutdown_all_button = QPushButton("Shutdown All Slaves")
        self.shutdown_all_button.clicked.connect(self.shutdown_all_slaves)

        self.slave_list_label = QLabel("Connected Slaves:")
        self.slave_list = QListWidget()

        self.shutdown_selected_button = QPushButton("Shutdown Selected")
        self.shutdown_selected_button.clicked.connect(self.shutdown_selected_slave)

        # Load the image
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        logo_label = QLabel(self)
        pixmap = QPixmap(logo_path)
        logo_label.setPixmap(pixmap)

        layout = QVBoxLayout()
        layout.addWidget(logo_label)
        layout.addWidget(self.conn_label)
        layout.addWidget(self.shutdown_all_button)
        layout.addWidget(self.slave_list_label)
        layout.addWidget(self.slave_list)
        layout.addWidget(self.shutdown_selected_button)

        self.central_widget.setLayout(layout)

        # Start listening on initialization
        self.listen_thread = threading.Thread(target=self.start_listening)
        self.listen_thread.start()

    def start_listening(self):
        port = 9000  # Default port
        try:
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.bind(("0.0.0.0", port))
            listener.listen(5)
            self.conn_label.setText(f"Master is listening on port {port}")

            while True:
                conn, addr = listener.accept()
                print("Connected to slave:", addr)

                mutex.acquire()
                slave_connections.append((conn, addr))
                self.update_slave_list()  # Update slave list
                mutex.release()

                conn_thread = threading.Thread(target=self.handle_connection, args=(conn,))
                conn_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start listening: {e}")

    def update_slave_list(self):
        self.slave_list.clear()
        for _, addr in slave_connections:
            self.slave_list.addItem(str(addr))

    def handle_connection(self, conn):
        try:
            while True:
                command = conn.recv(1024).decode().strip()
                if not command:
                    break
                print("Received command from slave:", command)
                # Execute commands
                # For demonstration, we simply print a message
                print("Unknown command:", command)
        except Exception as e:
            print("Error handling connection:", e)
        finally:
            mutex.acquire()
            for idx, (c, _) in enumerate(slave_connections):
                if c == conn:
                    del slave_connections[idx]
                    self.update_slave_list()  # Update slave list
                    break
            mutex.release()
            conn.close()

    def broadcast_shutdown(self):
        mutex.acquire()
        print("Broadcasting shutdown command to all slaves...")
        for conn, _ in slave_connections:
            try:
                conn.sendall(b"shutdown\n")
            except Exception as e:
                print(f"Failed to send shutdown command to {conn.getpeername()}: {e}")
        mutex.release()
        print("Shutdown command sent to all slaves")

    def shutdown_all_slaves(self):
        self.broadcast_shutdown()

    def shutdown_selected_slave(self):
        selected_slave = self.slave_list.currentItem()
        if selected_slave:
            conn, addr = selected_slave.data(0)
            try:
                conn.sendall(b"shutdown\n")
                print(f"Shutdown command sent to {addr}")
            except Exception as e:
                print(f"Failed to send shutdown command to {addr}: {e}")

def main():
    app = QApplication(sys.argv)

    # Set dark mode stylesheet
    app.setStyleSheet("QMainWindow {background-color: #333333;} "
                      "QLabel {color: #ffffff;} "
                      "QPushButton {color: #ffffff; background-color: #444444;} "
                      "QListWidget {color: #ffffff; background-color: #555555;} "
                      "QListWidget::item:selected {background-color: #666666;}")

    window = MasterControlWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
