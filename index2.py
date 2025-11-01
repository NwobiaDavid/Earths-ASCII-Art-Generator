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
        self.root.geometry("500x300")
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
        instructions = tk.Label(main_frame, text="Select an image and click 'Generate ASCII Art'\nOutput will appear in the terminal", justify=tk.LEFT)
        instructions.pack(pady=20)
        
        # Terminal output frame
        terminal_frame = tk.LabelFrame(main_frame, text="Terminal Output Preview", padx=10, pady=10)
        terminal_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Text widget for preview
        self.text_widget = tk.Text(terminal_frame, wrap=tk.NONE, bg="black", fg="white", font=("Courier", 8))
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
            # Generate ASCII art
            my_art = AsciiArt.from_image(self.image_path)
            
            # Capture the output that would go to terminal
            f = io.StringIO()
            with redirect_stdout(f):
                my_art.to_terminal()
            output = f.getvalue()
            
            # Display in GUI text widget
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, output)
            
            # Also print to actual terminal with colors
            print(output)
            
            self.status.config(text="ASCII art generated successfully! Check terminal for colored output")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ASCII art:\n{str(e)}")
            self.status.config(text="Error occurred")

if __name__ == "__main__":
    root = tk.Tk()
    app = ASCIIGeneratorGUI(root)
    root.mainloop()