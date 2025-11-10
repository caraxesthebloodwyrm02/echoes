import tkinter as tk
import math
import json
import os
from datetime import datetime


class SmartWindow:
    # Class variables for shared state
    windows = []
    memory_file = "window_layout.json"
    snap_threshold = 80
    reviews_file = "community_reviews.json"

    def __init__(self, name, content, x=100, y=100, width=300, height=150):
        self.name = name
        self.content = content
        self.position = [x, y]
        self.size = [width, height]
        self.is_dragging = False
        self.active = False

        # Create main window
        self.window = tk.Tk()
        self.window.title(name)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.configure(bg="#1e1e1e", relief="raised", bd=1)

        # Title bar with custom styling
        self.title_bar = tk.Frame(self.window, bg="#333333", height=25)
        self.title_bar.pack(fill="x")

        # Title bar elements
        self.title_label = tk.Label(
            self.title_bar,
            text=name,
            bg="#333333",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
        )
        self.title_label.pack(side="left", padx=10)

        # Minimize and close buttons
        self.btn_frame = tk.Frame(self.title_bar, bg="#333333")
        self.btn_frame.pack(side="right")

        self.min_btn = tk.Label(
            self.btn_frame,
            text="─",
            bg="#333333",
            fg="#ffffff",
            font=("Arial", 10),
            cursor="hand2",
        )
        self.min_btn.pack(side="left", padx=5)

        self.close_btn = tk.Label(
            self.btn_frame,
            text="✕",
            bg="#333333",
            fg="#ffffff",
            font=("Arial", 10),
            cursor="hand2",
        )
        self.close_btn.pack(side="left", padx=5)

        # Content area
        self.content_frame = tk.Frame(self.window, bg="#2d2d2d")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Add content based on window type
        if name == "Code Editor":
            self.setup_editor()
        elif name == "Terminal":
            self.setup_terminal()
        elif name == "Browser":
            self.setup_browser()
        elif name == "Docs":
            self.setup_docs()
        elif name == "Settings":
            self.setup_settings()
        elif name == "Community Review":
            self.setup_community_review()

        # Visual feedback frame for snapping
        self.snap_preview = tk.Frame(self.window, bg="#0066cc", relief="ridge", bd=2)

        # Bind events
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.on_drag)
        self.title_bar.bind("<ButtonRelease-1>", self.end_drag)
        self.window.bind("<Button-1>", self.activate)
        self.close_btn.bind("<Button-1>", self.close_window)

        # Add to global windows list
        SmartWindow.windows.append(self)

    def setup_editor(self):
        # Code editor interface
        text_frame = tk.Frame(self.content_frame, bg="#1e1e1e")
        text_frame.pack(fill="both", expand=True)

        # Line numbers
        line_numbers = tk.Text(
            text_frame,
            width=4,
            bg="#252526",
            fg="#858585",
            state="disabled",
            wrap="none",
        )
        line_numbers.pack(side="left", fill="y")

        # Code area
        self.code_text = tk.Text(
            text_frame, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10), wrap="none"
        )
        self.code_text.pack(side="left", fill="both", expand=True)

        # Sample code
        sample_code = """def hello_world():
    print("Hello, magnetic windows!")
    return "This is persistent memory"

if __name__ == "__main__":
    hello_world()"""

        for i, line in enumerate(sample_code.split("\n"), 1):
            line_numbers.config(state="normal")
            line_numbers.insert("end", f"{i}\n")
            line_numbers.config(state="disabled")
            self.code_text.insert("end", line + "\n")

    def setup_terminal(self):
        # Terminal interface
        self.terminal_text = tk.Text(
            self.content_frame,
            bg="#000000",
            fg="#00ff00",
            font=("Consolas", 10),
            state="disabled",
        )
        self.terminal_text.pack(fill="both", expand=True)

        # Sample terminal output
        terminal_output = """>> python magnetic_windows.py
Starting window manager...
Snap threshold: 80px
Windows loaded: 3
Loading previous layout...
Snap activated between "Code Editor" and "Terminal"
Layout saved successfully
>> _"""

        self.terminal_text.config(state="normal")
        self.terminal_text.insert("1.0", terminal_output)
        self.terminal_text.config(state="disabled")

    def setup_browser(self):
        # Browser interface
        self.browser_frame = tk.Frame(self.content_frame, bg="#ffffff")
        self.browser_frame.pack(fill="both", expand=True)

        # Address bar
        address_bar = tk.Frame(self.browser_frame, bg="#f0f0f0", height=30)
        address_bar.pack(fill="x", pady=2)

        address_entry = tk.Entry(address_bar, font=("Arial", 9))
        address_entry.pack(fill="x", padx=5, pady=5)
        address_entry.insert(0, "https://docs.python.org/3/library/tkinter.html")

        # Web content area
        web_content = tk.Label(
            self.browser_frame,
            text="🕸️ Python Tkinter Documentation\n\nWindow Management Demo\n\nMagnetic Snapping System Active",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#333333",
            justify="center",
        )
        web_content.pack(expand=True)

    def setup_docs(self):
        # Documentation interface
        self.docs_text = tk.Text(
            self.content_frame,
            bg="#ffffff",
            fg="#333333",
            font=("Segoe UI", 10),
            state="disabled",
        )
        self.docs_text.pack(fill="both", expand=True)

        docs_content = """📚 Window Management API

SmartWindow class:
- start_drag(): Begin window movement
- snap_to_target(): Magnetic attraction
- save_layout(): Persist positions
- load_layout(): Restore memory

Features:
✅ Visual snap preview
✅ Persistent positioning  
✅ Multi-snap points
✅ Active window highlighting

API Reference:
    SmartWindow.snap_threshold = 80
    SmartWindow.windows = []
    SmartWindow.save_layout()
    SmartWindow.load_layout()"""

        self.docs_text.config(state="normal")
        self.docs_text.insert("1.0", docs_content)
        self.docs_text.config(state="disabled")

    def setup_settings(self):
        # Settings interface
        settings_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        settings_frame.pack(fill="both", expand=True)

        # Snap strength slider
        snap_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        snap_frame.pack(fill="x", pady=10)

        tk.Label(snap_frame, text="Snap Strength:", bg="#f0f0f0").pack(side="left")
        self.snap_scale = tk.Scale(
            snap_frame,
            from_=30,
            to=150,
            orient="horizontal",
            bg="#f0f0f0",
            command=self.update_snap_strength,
        )
        self.snap_scale.set(SmartWindow.snap_threshold)
        self.snap_scale.pack(side="right", fill="x", expand=True)

        # Memory info
        memory_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        memory_frame.pack(fill="x", pady=10)

        tk.Label(
            memory_frame,
            text=f"Memory File: {SmartWindow.memory_file}",
            bg="#f0f0f0",
            font=("Arial", 8),
        ).pack()

        # Status
        self.status_label = tk.Label(
            settings_frame,
            text="Status: Ready",
            bg="#f0f0f0",
            fg="#008000",
            font=("Arial", 10, "bold"),
        )
        self.status_label.pack(pady=10)

    def update_snap_strength(self, value):
        SmartWindow.snap_threshold = int(value)
        self.status_label.config(text=f"Status: Snap threshold = {value}px")

    def setup_community_review(self):
        # Community review interface
        self.community_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        self.community_frame.pack(fill="both", expand=True)

        # Review input
        input_frame = tk.Frame(self.community_frame, bg="#f0f0f0")
        input_frame.pack(fill="x", pady=5)

        tk.Label(input_frame, text="Add Review:", bg="#f0f0f0").pack(side="left")
        self.review_entry = tk.Entry(input_frame, width=40)
        self.review_entry.pack(side="left", fill="x", expand=True, padx=5)

        add_btn = tk.Button(input_frame, text="Add Review", command=self.add_review)
        add_btn.pack(side="right")

        # Daily read button
        daily_btn = tk.Button(
            self.community_frame,
            text="Read Daily Review",
            command=self.read_daily_review,
        )
        daily_btn.pack(pady=5)

        # Reviews display
        self.reviews_text = tk.Text(
            self.community_frame, bg="#ffffff", fg="#333333", height=10
        )
        self.reviews_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Load existing reviews
        self.reviews = []
        self.load_reviews()

    def load_reviews(self):
        try:
            with open(SmartWindow.reviews_file, "r") as f:
                self.reviews = json.load(f)
        except:
            self.reviews = []
        self.display_reviews()

    def display_reviews(self):
        self.reviews_text.delete("1.0", "end")
        for review in self.reviews:
            self.reviews_text.insert("end", f"{review['date']}: {review['review']}\n\n")

    def add_review(self):
        review_text = self.review_entry.get().strip()
        if review_text:
            new_review = {
                "review": review_text,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.reviews.append(new_review)
            self.save_reviews()
            self.review_entry.delete(0, "end")
            self.display_reviews()

    def read_daily_review(self):
        if self.reviews:
            # Show the latest review as daily
            latest = self.reviews[-1]
            tk.messagebox.showinfo(
                "Daily Review",
                f"Today's Review:\n\n{latest['review']}\n\n- {latest['date']}",
            )
        else:
            tk.messagebox.showinfo("Daily Review", "No reviews available.")

    def save_reviews(self):
        try:
            with open(SmartWindow.reviews_file, "w") as f:
                json.dump(self.reviews, f)
        except Exception as e:
            print(f"Error saving reviews: {e}")

    def activate(self, event):
        # Highlight active window
        for window in SmartWindow.windows:
            window.title_bar.configure(bg="#333333")
            window.title_label.configure(bg="#333333")

        self.title_bar.configure(bg="#0066cc")
        self.title_label.configure(bg="#0066cc")
        self.active = True

    def start_drag(self, event):
        self.is_dragging = True
        self.drag_start_x = event.x_root - self.position[0]
        self.drag_start_y = event.y_root - self.position[1]
        self.window.configure(relief="sunken", bd=3)

    def on_drag(self, event):
        if not self.is_dragging:
            return

        # Calculate new position
        new_x = event.x_root - self.drag_start_x
        new_y = event.y_root - self.drag_start_y

        # Update window position
        self.window.geometry(f"+{new_x}+{new_y}")
        self.position = [new_x, new_y]

        # Check for snapping opportunities
        closest_window = self.find_closest_window(new_x, new_y)
        if (
            closest_window
            and self.calculate_distance(
                new_x, new_y, closest_window.position[0], closest_window.position[1]
            )
            < SmartWindow.snap_threshold
        ):
            snap_point = self.calculate_snap_point(new_x, new_y, closest_window)
            if snap_point:
                # Show snap preview
                self.show_snap_preview(snap_point[0], snap_point[1])
        else:
            self.hide_snap_preview()

    def end_drag(self, event):
        self.is_dragging = False
        self.window.configure(relief="raised", bd=1)

        # Try to snap to closest window
        closest_window = self.find_closest_window(self.position[0], self.position[1])
        if closest_window:
            snap_point = self.calculate_snap_point(
                self.position[0], self.position[1], closest_window
            )
            if (
                snap_point
                and self.calculate_distance(
                    self.position[0],
                    self.position[1],
                    closest_window.position[0],
                    closest_window.position[1],
                )
                < SmartWindow.snap_threshold
            ):
                self.snap_to_window(snap_point[0], snap_point[1])
                self.show_snap_feedback()

        self.hide_snap_preview()
        SmartWindow.save_layout()

    def find_closest_window(self, x, y):
        closest = None
        min_distance = float("inf")

        for window in SmartWindow.windows:
            if window != self:
                distance = self.calculate_distance(
                    x, y, window.position[0], window.position[1]
                )
                if distance < min_distance:
                    min_distance = distance
                    closest = window

        return closest

    def calculate_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def calculate_snap_point(self, x, y, target_window):
        # Calculate optimal snap position relative to target window
        target_x, target_y = target_window.position
        target_w, target_h = target_window.size
        self_w, self_h = self.size

        # Potential snap positions (relative to target)
        snap_positions = [
            # Left of target
            (target_x - self_w, target_y),
            # Right of target
            (target_x + target_w, target_y),
            # Above target
            (target_x, target_y - self_h),
            # Below target
            (target_x, target_y + target_h),
            # Top-left
            (target_x - self_w, target_y - self_h),
            # Top-right
            (target_x + target_w, target_y - self_h),
            # Bottom-left
            (target_x - self_w, target_y + target_h),
            # Bottom-right
            (target_x + target_w, target_y + target_h),
        ]

        # Find closest snap position
        best_snap = None
        min_distance = float("inf")

        for snap_pos in snap_positions:
            distance = self.calculate_distance(x, y, snap_pos[0], snap_pos[1])
            if distance < min_distance:
                min_distance = distance
                best_snap = snap_pos

        return best_snap

    def snap_to_window(self, snap_x, snap_y):
        self.window.geometry(f"+{snap_x}+{snap_y}")
        self.position = [snap_x, snap_y]

    def show_snap_preview(self, x, y):
        self.snap_preview.place(x=x, y=y, width=self.size[0], height=self.size[1])

    def hide_snap_preview(self):
        self.snap_preview.place_forget()

    def show_snap_feedback(self):
        # Brief visual feedback after snapping
        original_bg = self.window.cget("bg")
        self.window.configure(bg="#0066cc")
        self.window.after(200, lambda: self.window.configure(bg=original_bg))

    def close_window(self, event):
        # Remove from windows list and destroy
        SmartWindow.windows.remove(self)
        self.window.destroy()

        # Update memory
        SmartWindow.save_layout()

    # Class methods for layout management
    @classmethod
    def save_layout(cls):
        """Save current window positions to file"""
        layout = {}
        for window in cls.windows:
            layout[window.name] = {"position": window.position, "size": window.size}

        try:
            with open(cls.memory_file, "w") as f:
                json.dump(layout, f)
            print(f"💾 Window layout saved to {cls.memory_file}")
        except Exception as e:
            print(f"Error saving layout: {e}")

    @classmethod
    def load_layout(cls):
        """Load window positions from file"""
        if not os.path.exists(cls.memory_file):
            return {}

        try:
            with open(cls.memory_file, "r") as f:
                layout = json.load(f)
            print(f"📁 Loaded window layout from {cls.memory_file}")
            return layout
        except Exception as e:
            print(f"Error loading layout: {e}")
            return {}

    @classmethod
    def create_all_windows(cls):
        """Create all windows with optional layout restoration"""
        layout = cls.load_layout()

        # Default window configurations
        window_configs = [
            ("Code Editor", "Code Editor"),
            ("Terminal", "Terminal"),
            ("Browser", "Browser"),
            ("Docs", "Documentation"),
            ("Settings", "Settings"),
            ("Community Review", "Community Review"),
        ]

        # Position windows in a grid if no layout exists
        default_positions = [
            (100, 100),  # Code Editor
            (450, 100),  # Terminal
            (800, 100),  # Browser
            (100, 300),  # Docs
            (450, 300),  # Settings
            (800, 300),  # Community Review
        ]

        for i, (name, content) in enumerate(window_configs):
            # Use saved position or default
            if name in layout:
                pos = layout[name]["position"]
                size = layout[name]["size"]
            else:
                pos = default_positions[i]
                size = [300, 150]

            window = cls(name, content, pos[0], pos[1], size[0], size[1])

        # Start the main loop for all windows
        for window in cls.windows:
            window.window.mainloop()


# Create and run the window manager
if __name__ == "__main__":
    print("🧲 Starting Magnetic Window Manager...")
    SmartWindow.create_all_windows()
