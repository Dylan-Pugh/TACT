"""
GUI for the Temporal Adjustment Correction Tool
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class TACT(toga.App):
    def startup(self):
        # Create a button to trigger the file chooser
        select_file_button = toga.Button("Select File", on_press=self.select_file)

        # Add the button to a box
        box = toga.Box(children=[select_file_button], style=Pack(direction=COLUMN))

        # Create a main window and add the box to its content
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = box
        self.main_window.show()

    def select_file(self, widget):
        # Open the file dialog and get the selected file path
        file_path = self.main_window.open_file_dialog(
            title="Select a file", file_types=["csv", "nc"], multiselect=True
        )

        # Display the selected file path in a label
        file_path_label = toga.Label("Selected File: {}".format(file_path))
        widget.parent.add(file_path_label)


def main():
    return TACT()
