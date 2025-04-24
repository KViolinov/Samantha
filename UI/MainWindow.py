from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QSurfaceFormat
from UI.OpenGLWidget import OpenGLWidget
from Logic.LogicThread import LogicThread
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OS-1 - Samantha")
        self.setStyleSheet("background-color: #d1684e;")

        self.toend = False

        format = QSurfaceFormat()
        format.setDepthBufferSize(24)
        format.setSamples(4)
        QSurfaceFormat.setDefaultFormat(format)

        self.opengl_widget = OpenGLWidget(self)
        self.setCentralWidget(self.opengl_widget)

        self.resize(500, 500)
        self.setMinimumSize(500, 500)

        # Initialize LogicThread
        self.logic_thread = LogicThread()
        self.logic_thread.update_signal.connect(self.handle_algorithm_result)
        self.logic_thread.start()

        # Start with chill state, then activate after 10 seconds
        self.opengl_widget.chill()
        QTimer.singleShot(10000, self.start_active_and_algorithm)
        QTimer.singleShot(11000, self.logic_thread.play_startup_sound)

    def handle_algorithm_result(self, result):
        print(f"Algorithm result: {result}")

    def closeEvent(self, event):
        self.logic_thread.stop()
        self.logic_thread.wait()
        event.accept()

    def start_active_and_algorithm(self):
        self.opengl_widget.active()
        QTimer.singleShot(7000, self.logic_thread.trigger_algorithm)  # 10s + 7s = 17s

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())