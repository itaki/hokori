from PySide6.QtWidgets import QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QLabel, QPushButton, QFormLayout, QLineEdit, QComboBox, QSpinBox

class HokoriMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Hokori Shop Manager')
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        # Gates Panel
        self.gates_label = QLabel("Gates")
        self.gates_view = QListView()  # Or QTreeView if hierarchical structure is needed
        self.main_layout.addWidget(self.gates_label)
        self.main_layout.addWidget(self.gates_view)

        # Tools Panel
        self.tools_label = QLabel("Tools")
        self.tools_view = QListView()
        self.main_layout.addWidget(self.tools_label)
        self.main_layout.addWidget(self.tools_view)

        # Dust Collector Panel
        self.collector_label = QLabel("Dust Collector")
        self.collector_status = QLabel("Status: OFF")  # Update this dynamically
        self.collector_button = QPushButton("Toggle Dust Collector")
        self.main_layout.addWidget(self.collector_label)
        self.main_layout.addWidget(self.collector_status)
        self.main_layout.addWidget(self.collector_button)

        # Detailed Configuration Panel
        self.detail_layout = QFormLayout()
        self.detail_label = QLabel("Details/Config")
        self.main_layout.addWidget(self.detail_label)
        self.main_layout.addLayout(self.detail_layout)

        # Example Fields for Editing
        self.gate_minimum = QSpinBox()
        self.gate_maximum = QSpinBox()
        self.detail_layout.addRow("Gate Minimum", self.gate_minimum)
        self.detail_layout.addRow("Gate Maximum", self.gate_maximum)

        self.tool_gate_prefs = QComboBox()  # This would be populated with actual gate options
        self.detail_layout.addRow("Tool Gate Preferences", self.tool_gate_prefs)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Connect signals (placeholders for now)
        self.gates_view.clicked.connect(self.edit_gate)
        self.tools_view.clicked.connect(self.edit_tool)
        self.collector_button.clicked.connect(self.toggle_collector)

    def edit_gate(self, index):
        # Load gate details into the form for editing
        pass

    def edit_tool(self, index):
        # Load tool details into the form for editing
        pass

    def toggle_collector(self):
        # Logic to toggle the dust collector status
        pass

if __name__ == '__main__':
    app = QApplication([])
    window = HokoriMainWindow()
    window.show()
    app.exec_()
