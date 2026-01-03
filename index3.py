import tkinter as tk
from tkinter import filedialog, messagebox
from ascii_magic import AsciiArt
import colorama
import io
import sys
from contextlib import redirect_stdout

class ASCIIGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Earths ASCII Art Generator")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Initialize colorama
        colorama.init()
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Earths ASCII Magic Generator", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Image path display
        self.path_label = tk.Label(main_frame, text="No image selected", fg="gray")
        self.path_label.pack(pady=5)
        
        # Detail control frame
        detail_frame = tk.Frame(main_frame)
        detail_frame.pack(pady=10)
        
        tk.Label(detail_frame, text="Detail Level (columns):", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # Detail slider
        self.detail_var = tk.IntVar(value=120)
        self.detail_slider = tk.Scale(detail_frame, from_=50, to=500, orient=tk.HORIZONTAL, 
                                       variable=self.detail_var, length=200)
        self.detail_slider.pack(side=tk.LEFT, padx=5)
        
        self.detail_label = tk.Label(detail_frame, text="120", font=("Arial", 10, "bold"))
        self.detail_label.pack(side=tk.LEFT, padx=5)
        
        # Update label when slider moves
        self.detail_slider.config(command=self.update_detail_label)
        
        # Info label
        info_label = tk.Label(main_frame, text="Higher values = more detail (but slower)", 
                             fg="gray", font=("Arial", 8))
        info_label.pack()
        
        # Buttons frame
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        # Select image button (light yellow)
        self.select_btn = tk.Button(btn_frame, text="Select Image", command=self.select_image, 
                                   bg="#FFD700", fg="black", padx=20, font=("Arial", 10, "bold"))
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        # Generate button (dark yellow/gold)
        self.generate_btn = tk.Button(btn_frame, text="Generate ASCII Art", command=self.generate_art, 
                                     bg="#FFA500", fg="black", padx=20, font=("Arial", 10, "bold"), state=tk.DISABLED)
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = tk.Label(main_frame, text="Select an image, adjust detail level, then generate\nOutput will appear in the terminal", 
                               justify=tk.LEFT, font=("Arial", 9))
        instructions.pack(pady=10)
        
        # Terminal output frame
        terminal_frame = tk.LabelFrame(main_frame, text="Terminal Output Preview", padx=10, pady=10)
        terminal_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Text widget for preview
        self.text_widget = tk.Text(terminal_frame, wrap=tk.NONE, bg="black", fg="white", font=("Courier", 6))
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scroll = tk.Scrollbar(self.text_widget, orient=tk.VERTICAL, command=self.text_widget.yview)
        h_scroll = tk.Scrollbar(self.text_widget, orient=tk.HORIZONTAL, command=self.text_widget.xview)
        self.text_widget.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status bar
        self.status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_detail_label(self, value):
        self.detail_label.config(text=str(int(float(value))))
        
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.image_path = file_path
            # Show filename only
            filename = file_path.split('/')[-1].split('\\')[-1]  # Works for both Unix and Windows paths
            self.path_label.config(text=f"Selected: {filename}", fg="blue")
            self.generate_btn.config(state=tk.NORMAL)
            self.status.config(text=f"Image loaded: {filename}")
    
    def generate_art(self):
        if not hasattr(self, 'image_path'):
            messagebox.showwarning("Warning", "Please select an image first!")
            return
            
        try:
            self.status.config(text="Generating... Please wait")
            self.root.update()
            
            # Get detail level from slider
            columns = self.detail_var.get()
            
            # Generate ASCII art with specified detail level
            my_art = AsciiArt.from_image(self.image_path)
            
            # Capture the output that would go to terminal
            f = io.StringIO()
            with redirect_stdout(f):
                my_art.to_terminal(columns=columns)
            output = f.getvalue()
            
            # Display in GUI text widget
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, output)
            
            # Also print to actual terminal with colors
            my_art.to_terminal(columns=columns)
            
            self.status.config(text=f"ASCII art generated successfully with {columns} columns! Check terminal for colored output")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ASCII art:\n{str(e)}")
            self.status.config(text="Error occurred")

if __name__ == "__main__":
    root = tk.Tk()
    app = ASCIIGeneratorGUI(root)
    root.mainloop()