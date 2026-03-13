#!/usr/bin/env python3
"""Minimal PyQt viewer that forwards JSON trees to the embedded web app."""

import json
import pathlib
import sys
import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


TREE_TEMPLATE = {
    "behaviours": {
        "1": {
            "id": "1",
            "status": "RUNNING",
            "name": "Root",
            "colour": "#00FFFF",
            "children": ["2", "3"],
            "data": {"Type": "Selector", "Feedback": "Choosing"},
        },
        "2": {
            "id": "2",
            "status": "SUCCESS",
            "name": "Check",
            "colour": "#00FF00",
            "data": {"Type": "Condition", "Feedback": "Ready"},
        },
        "3": {
            "id": "3",
            "status": "RUNNING",
            "name": "Work",
            "colour": "#FFA500",
            "data": {"Type": "Action", "Feedback": "Executing"},
        },
    },
    "visited_path": ["1", "3"],
    "blackboard": {
        "behaviours": {
            "3": {
                "/state/worker": "running",
            }
        },
        "data": {
            "/state/worker": "running",
            "/task/id": "demo",
        },
    },
    "activity": [
        "<text style='color: green;'>Check succeeded</text>",
        "<text style='color: orange;'>Work is running</text>",
    ],
}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PyTrees JS - PyQt Example")
        self.resize(1200, 800)

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)

        self.button = QtWidgets.QPushButton("Send tree to web view")
        self.button.clicked.connect(self.send_tree)

        self.web_view = QWebEngineView()
        index_path = pathlib.Path(__file__).with_name("index.html").resolve()
        self.web_view.load(QUrl.fromLocalFile(str(index_path)))

        layout.addWidget(self.button)
        layout.addWidget(self.web_view, stretch=1)
        self.setCentralWidget(central)

        self.tick = 0
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1500)
        self.timer.timeout.connect(self.send_tree)
        self.timer.start()

    def _make_tree(self) -> dict:
        tree = json.loads(json.dumps(TREE_TEMPLATE))
        tree["timestamp"] = int(time.time())
        tree["behaviours"]["3"]["status"] = "RUNNING" if self.tick % 2 == 0 else "SUCCESS"
        tree["visited_path"] = ["1", "3"] if self.tick % 2 == 0 else ["1", "2"]
        self.tick += 1
        return tree

    def send_tree(self) -> None:
        payload = json.dumps(self._make_tree(), ensure_ascii=False)
        command = f"render_tree({{tree: {payload}}})"
        self.web_view.page().runJavaScript(command)


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
