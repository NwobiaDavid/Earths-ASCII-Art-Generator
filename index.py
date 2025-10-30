from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time

class ColoredASCIIArtGenerator:
    def __init__(self, width=120):
        """
        Initialize the ASCII art generator.
        
        Args:
            width: Width of the ASCII art in characters
        """
        self.width = width
        # Detailed ASCII characters from darkest to lightest
        self.ascii_chars = '@%#*+=-:. '
        
    def resize_image(self, img, new_width):
        """Resize image maintaining aspect ratio."""
        width, height = img.size
        aspect_ratio = height / width
        # Characters are taller than wide, so adjust
        new_height = int(aspect_ratio * new_width * 0.55)
        return img.resize((new_width, new_height))
    
    def get_ascii_char(self, pixel_value):
        """Map pixel brightness to ASCII character."""
        return self.ascii_chars[pixel_value * len(self.ascii_chars) // 256]
    
    def rgb_to_hex(self, r, g, b):
        """Convert RGB to hex color."""
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def generate_ascii_art(self, image_path, use_color=True, callback=None, line_callback=None):
        """
        Generate ASCII art from an image.
        
        Args:
            image_path: Path to the input image
            use_color: Whether to use colors
            callback: Function to call with progress updates
            line_callback: Function to call when each line is generated (for animation)
        
        Returns:
            Tuple of (ascii_text, color_data) where color_data is list of (char, color) tuples per line
        """
        try:
            # Open and process image
            img = Image.open(image_path)
            img = self.resize_image(img, self.width)
            img_gray = img.convert('L')  # Convert to grayscale for ASCII mapping
            img_color = img.convert('RGB') if use_color else None
            
            # Generate ASCII art
            ascii_lines = []
            color_data = []  # Store color info separately
            total_lines = img_gray.height
            
            for y in range(img_gray.height):
                if callback:
                    callback(int((y / total_lines) * 100))
                
                line_chars = []
                line_colors = []
                
                for x in range(img_gray.width):
                    # Get brightness
                    brightness = img_gray.getpixel((x, y))
                    char = self.get_ascii_char(brightness)
                    line_chars.append(char)
                    
                    if use_color and img_color:
                        # Get color
                        r, g, b = img_color.getpixel((x, y))
                        color = self.rgb_to_hex(r, g, b)
                        line_colors.append(color)
                    else:
                        line_colors.append(None)
                
                line_text = ''.join(line_chars)
                ascii_lines.append(line_text)
                color_data.append(line_colors)
                
                # Call line callback for animation
                if line_callback:
                    line_callback(y, line_text, line_colors)
            
            if callback:
                callback(100)
            
            return '\n'.join(ascii_lines), color_data
            
        except Exception as e:
            raise Exception(f"Error generating ASCII art: {str(e)}")


class ASCIIArtGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Earth's ASCII Art Generator")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.image_path = None
        self.ascii_result = None
        self.color_data = None
        self.dark_mode = True
        self.is_generating = False
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header frame with title and theme toggle
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="🎨 Earth's ASCII Art Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Theme toggle button
        self.theme_btn = ttk.Button(header_frame, text="☀️ Light Mode", 
                                    command=self.toggle_theme, width=12)
        self.theme_btn.grid(row=0, column=1, sticky=tk.E, padx=5)
        
        # Controls frame
        controls_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # File selection
        file_frame = ttk.Frame(controls_frame)
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.file_label = ttk.Label(file_frame, text="No image selected")
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        select_btn = ttk.Button(file_frame, text="📁 Select Image", 
                               command=self.select_image)
        select_btn.pack(side=tk.RIGHT, padx=5)
        
        # Width control
        ttk.Label(controls_frame, text="Width (characters):").grid(row=1, column=0, 
                                                                    sticky=tk.W, pady=5)
        self.width_var = tk.IntVar(value=100)
        width_spinbox = ttk.Spinbox(controls_frame, from_=40, to=200, 
                                    textvariable=self.width_var, width=10)
        width_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Color checkbox
        self.color_var = tk.BooleanVar(value=True)
        color_check = ttk.Checkbutton(controls_frame, text="Use colors", 
                                     variable=self.color_var)
        color_check.grid(row=1, column=2, sticky=tk.W, padx=20, pady=5)
        
        # Generate button
        self.generate_btn = ttk.Button(controls_frame, text="✨ Generate ASCII Art", 
                                      command=self.generate_art, state='disabled')
        self.generate_btn.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(controls_frame, mode='determinate', length=300)
        self.progress.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Status label
        self.status_label = ttk.Label(controls_frame, text="Ready", foreground='green')
        self.status_label.grid(row=4, column=0, columnspan=3, pady=2)
        
        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="ASCII Art Output", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Text widget with scrollbars
        text_scroll_y = ttk.Scrollbar(output_frame, orient=tk.VERTICAL)
        text_scroll_x = ttk.Scrollbar(output_frame, orient=tk.HORIZONTAL)
        
        self.output_text = tk.Text(output_frame, wrap=tk.NONE, 
                                   yscrollcommand=text_scroll_y.set,
                                   xscrollcommand=text_scroll_x.set,
                                   font=('Courier', 7))
        
        text_scroll_y.config(command=self.output_text.yview)
        text_scroll_x.config(command=self.output_text.xview)
        
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        text_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Save button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=10)
        
        self.save_btn = ttk.Button(button_frame, text="💾 Save to File", 
                                   command=self.save_art, state='disabled')
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        copy_btn = ttk.Button(button_frame, text="📋 Copy to Clipboard", 
                             command=self.copy_to_clipboard, state='disabled')
        copy_btn.pack(side=tk.LEFT, padx=5)
        self.copy_btn = copy_btn
        
        fullscreen_btn = ttk.Button(button_frame, text="🖼️ Fullscreen View", 
                                    command=self.show_fullscreen, state='disabled')
        fullscreen_btn.pack(side=tk.LEFT, padx=5)
        self.fullscreen_btn = fullscreen_btn
    
    def toggle_theme(self):
        """Toggle between light and dark mode."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        
        # Re-display ASCII art with new theme if it exists
        if self.ascii_result and self.color_data and not self.is_generating:
            self.display_result()
    
    def apply_theme(self):
        """Apply the current theme."""
        if self.dark_mode:
            self.output_text.config(bg='#1e1e1e', fg='#d4d4d4', insertbackground='white')
            self.theme_btn.config(text="☀️ Light Mode")
        else:
            self.output_text.config(bg='#ffffff', fg='#000000', insertbackground='black')
            self.theme_btn.config(text="🌙 Dark Mode")
    
    def select_image(self):
        """Open file dialog to select an image."""
        file_types = [
            ('Image files', '*.jpg *.jpeg *.png *.bmp *.gif *.tiff'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select an image",
            filetypes=file_types,
            initialdir="~"
        )
        
        if filename:
            self.image_path = filename
            # Show filename in label
            import os
            self.file_label.config(text=os.path.basename(filename))
            self.generate_btn.config(state='normal')
    
    def update_progress(self, value):
        """Update progress bar."""
        self.progress['value'] = value
        self.root.update_idletasks()
    
    def update_status(self, message, color='blue'):
        """Update status label."""
        self.status_label.config(text=message, foreground=color)
        self.root.update_idletasks()
    
    def animate_line(self, line_num, line_text, line_colors):
        """Animate a single line being added to the output."""
        def add_line():
            # Calculate animation speed based on total lines
            # Faster for more lines to keep total time reasonable
            delay = max(5, min(50, 2000 // (self.width_var.get() // 2)))
            
            if line_colors and any(line_colors):
                # Add colored line
                for char_idx, char in enumerate(line_text):
                    if char_idx < len(line_colors) and line_colors[char_idx]:
                        tag_name = f"color_{line_colors[char_idx]}"
                        self.output_text.insert(tk.END, char, tag_name)
                        self.output_text.tag_config(tag_name, foreground=line_colors[char_idx])
                    else:
                        self.output_text.insert(tk.END, char)
            else:
                # Add plain line
                self.output_text.insert(tk.END, line_text)
            
            self.output_text.insert(tk.END, '\n')
            
            # Auto-scroll to show latest content
            self.output_text.see(tk.END)
            
        # Schedule the line addition on the main thread
        self.root.after(0, add_line)
        
        # Small delay between lines for animation effect
        time.sleep(0.02)
    
    def generate_art(self):
        """Generate ASCII art in a separate thread with animation."""
        if not self.image_path:
            messagebox.showwarning("No Image", "Please select an image first!")
            return
        
        # Disable button during generation
        self.is_generating = True
        self.generate_btn.config(state='disabled')
        self.output_text.delete(1.0, tk.END)
        self.progress['value'] = 0
        
        # Clear existing tags
        for tag in self.output_text.tag_names():
            self.output_text.tag_delete(tag)
        
        self.update_status("🎨 Generating ASCII art...", 'blue')
        
        def generate_thread():
            try:
                generator = ColoredASCIIArtGenerator(width=self.width_var.get())
                self.ascii_result, self.color_data = generator.generate_ascii_art(
                    self.image_path, 
                    use_color=self.color_var.get(),
                    callback=self.update_progress,
                    line_callback=self.animate_line
                )
                
                # Finalize
                self.root.after(0, self.finalize_generation)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.generate_btn.config(state='normal'))
                self.root.after(0, lambda: self.update_status("Error occurred", 'red'))
                self.is_generating = False
        
        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()
    
    def finalize_generation(self):
        """Finalize the generation process."""
        self.is_generating = False
        self.generate_btn.config(state='normal')
        self.save_btn.config(state='normal')
        self.copy_btn.config(state='normal')
        self.fullscreen_btn.config(state='normal')
        self.update_status("✅ Generation complete!", 'green')
        
        # Show completion message after a short delay
        self.root.after(500, lambda: messagebox.showinfo("Success", "ASCII art generated successfully!"))
    
    def display_result(self):
        """Display the generated ASCII art with proper coloring (for theme switching)."""
        self.output_text.delete(1.0, tk.END)
        
        # Clear existing tags
        for tag in self.output_text.tag_names():
            self.output_text.tag_delete(tag)
        
        lines = self.ascii_result.split('\n')
        
        for line_idx, line in enumerate(lines):
            if line_idx < len(self.color_data):
                colors = self.color_data[line_idx]
                
                for char_idx, char in enumerate(line):
                    if char_idx < len(colors) and colors[char_idx]:
                        # Create unique tag for this color
                        tag_name = f"color_{colors[char_idx]}"
                        
                        # Insert character with tag
                        self.output_text.insert(tk.END, char, tag_name)
                        
                        # Configure tag with color
                        self.output_text.tag_config(tag_name, foreground=colors[char_idx])
                    else:
                        self.output_text.insert(tk.END, char)
                
                self.output_text.insert(tk.END, '\n')
            else:
                self.output_text.insert(tk.END, line + '\n')
    
    def save_art(self):
        """Save ASCII art to a file."""
        if not self.ascii_result:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.html'):
                    # Save as HTML with colors
                    self.save_as_html(filename)
                else:
                    # Save as plain text
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(self.ascii_result)
                messagebox.showinfo("Success", f"ASCII art saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def save_as_html(self, filename):
        """Save ASCII art as HTML with colors."""
        html = ['<!DOCTYPE html>\n<html>\n<head>\n<style>']
        html.append('body { background-color: ' + ('#1e1e1e' if self.dark_mode else '#ffffff') + '; }')
        html.append('pre { font-family: monospace; font-size: 10px; line-height: 1.2; }')
        html.append('</style>\n</head>\n<body>\n<pre>')
        
        lines = self.ascii_result.split('\n')
        
        for line_idx, line in enumerate(lines):
            if line_idx < len(self.color_data):
                colors = self.color_data[line_idx]
                for char_idx, char in enumerate(line):
                    if char_idx < len(colors) and colors[char_idx]:
                        html.append(f'<span style="color:{colors[char_idx]}">{char}</span>')
                    else:
                        html.append(char)
                html.append('\n')
        
        html.append('</pre>\n</body>\n</html>')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(''.join(html))
    
    def copy_to_clipboard(self):
        """Copy ASCII art to clipboard."""
        if not self.ascii_result:
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(self.ascii_result)
        messagebox.showinfo("Success", "ASCII art copied to clipboard!")
    
    def show_fullscreen(self):
        """Display ASCII art in fullscreen mode."""
        if not self.ascii_result or not self.color_data:
            return
        
        # Create fullscreen window
        fullscreen_window = tk.Toplevel(self.root)
        fullscreen_window.title("Fullscreen ASCII Art")
        
        # Set fullscreen
        fullscreen_window.attributes('-fullscreen', True)
        
        # Apply theme background
        bg_color = '#1e1e1e' if self.dark_mode else '#ffffff'
        fullscreen_window.configure(bg=bg_color)
        
        # Create frame for centering
        center_frame = tk.Frame(fullscreen_window, bg=bg_color)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Calculate the actual width and height of the ASCII art
        lines = self.ascii_result.split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        height = len(lines)
        
        # Create text widget for ASCII art with fixed dimensions
        text_widget = tk.Text(center_frame, 
                             wrap=tk.NONE,
                             font=('Courier', 8),
                             bg=bg_color,
                             fg='#d4d4d4' if self.dark_mode else '#000000',
                             relief=tk.FLAT,
                             borderwidth=0,
                             highlightthickness=0,
                             cursor='none',
                             width=max_width,
                             height=height)
        text_widget.pack()
        
        # Populate text widget with colored ASCII art
        lines = self.ascii_result.split('\n')
        
        for line_idx, line in enumerate(lines):
            if line_idx < len(self.color_data):
                colors = self.color_data[line_idx]
                
                for char_idx, char in enumerate(line):
                    if char_idx < len(colors) and colors[char_idx]:
                        tag_name = f"fs_color_{colors[char_idx]}"
                        text_widget.insert(tk.END, char, tag_name)
                        text_widget.tag_config(tag_name, foreground=colors[char_idx])
                    else:
                        text_widget.insert(tk.END, char)
                
                text_widget.insert(tk.END, '\n')
            else:
                text_widget.insert(tk.END, line + '\n')
        
        # Make text widget read-only
        text_widget.config(state='disabled')
        
        # Create instructions label
        instructions = tk.Label(fullscreen_window, 
                               text="Press ESC or click anywhere to exit fullscreen",
                               font=('Arial', 10),
                               bg=bg_color,
                               fg='#888888')
        instructions.place(relx=0.5, rely=0.95, anchor='center')
        
        # Bind escape key and click to exit fullscreen
        def exit_fullscreen(event=None):
            fullscreen_window.destroy()
        
        fullscreen_window.bind('<Escape>', exit_fullscreen)
        fullscreen_window.bind('<Button-1>', exit_fullscreen)
        text_widget.bind('<Button-1>', exit_fullscreen)
        
        # Focus the window
        fullscreen_window.focus_force()


def main():
    root = tk.Tk()
    app = ASCIIArtGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()