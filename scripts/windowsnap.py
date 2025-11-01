import tkinter as tk
from pynput import keyboard

class Window1:
    def __init__(self):
        self.root = tk.Tk()
        self.label = tk.Label(self.root, text="Window 1")
        self.label.pack()

        # Create a keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        # Define the callback function to update the label in Window2
        def update_label(event):
            self.label['text'] = f"Window 1 pressed {event.char}"

        # Bind the update_label function to the root window's binding order
        self.root.bind('<KeyRelease>', update_label)

        # Start the Tkinter event loop
        self.root.mainloop()

    def on_press(self, key):
        print(f"Key pressed: {key.char}")

class Window2:
    def __init__(self):
        self.root = tk.Tk()
        self.label = tk.Label(self.root, text="Window 2")
        self.label.pack()

        # Create a keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        # Define the callback function to update the label in Window1
        def update_label(event):
            self.label['text'] = f"Window 2 pressed {event.char}"

        # Bind the update_label function to the root window's binding order
        self.root.bind('<KeyRelease>', update_label)

        # Start the Tkinter event loop
        self.root.mainloop()

    def on_press(self, key):
        print(f"Key pressed in Window 2: {key.char}")

def merge_windows():
    window1 = Window1()
    window2 = Window2()

# Run the function to create and merge the windows
merge_windows()