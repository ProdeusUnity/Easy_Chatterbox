#!/usr/bin/env python3
"""
Chatterbox-TTS GUI
Simple interface for text-to-speech generation
Supports both standard and turbo models
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

# Try to import turbo model, but don't fail if it's not available
try:
    from chatterbox.tts_turbo import ChatterboxTurboTTS
    TURBO_AVAILABLE = True
except ImportError:
    TURBO_AVAILABLE = False
    ChatterboxTurboTTS = None

class ChatterboxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatterbox TTS")
        self.root.geometry("800x600")
        
        self.model = None
        self.model_dir = None
        self.reference_audio = None
        self.generating = False
        self.is_turbo = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # ===== Model Configuration Section =====
        config_frame = ttk.LabelFrame(main_frame, text="Model Configuration", padding="10")
        config_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Model type selection
        ttk.Label(config_frame, text="Model Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_type_var = tk.StringVar(value="standard")
        type_frame = ttk.Frame(config_frame)
        type_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(type_frame, text="Standard", variable=self.model_type_var, 
                       value="standard", command=self.on_model_type_change).pack(side=tk.LEFT, padx=5)
        turbo_btn = ttk.Radiobutton(type_frame, text="Turbo", variable=self.model_type_var, 
                       value="turbo", command=self.on_model_type_change)
        turbo_btn.pack(side=tk.LEFT, padx=5)
        if not TURBO_AVAILABLE:
            turbo_btn.config(state="disabled")
            ttk.Label(type_frame, text="(not installed)", foreground="gray").pack(side=tk.LEFT)
        
        # Model folder (only for standard model)
        self.model_folder_label = ttk.Label(config_frame, text="Model Folder:")
        self.model_folder_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_path_var = tk.StringVar()
        self.model_entry = ttk.Entry(config_frame, textvariable=self.model_path_var, state="readonly")
        self.model_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.model_browse_btn = ttk.Button(config_frame, text="Browse...", command=self.browse_model)
        self.model_browse_btn.grid(row=1, column=2, pady=5)
        
        # Reference audio
        ttk.Label(config_frame, text="Reference Audio:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.audio_path_var = tk.StringVar()
        audio_entry = ttk.Entry(config_frame, textvariable=self.audio_path_var, state="readonly")
        audio_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(config_frame, text="Browse...", command=self.browse_audio).grid(row=2, column=2, pady=5)
        
        # Device selection
        ttk.Label(config_frame, text="Device:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.device_var = tk.StringVar(value="cpu")
        device_frame = ttk.Frame(config_frame)
        device_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(device_frame, text="CPU", variable=self.device_var, value="cpu").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(device_frame, text="CUDA", variable=self.device_var, value="cuda").pack(side=tk.LEFT, padx=5)
        
        # Load model button
        self.load_btn = ttk.Button(config_frame, text="Load Model", command=self.load_model)
        self.load_btn.grid(row=4, column=0, columnspan=3, pady=10)
        
        # Status indicator
        self.status_label = ttk.Label(config_frame, text="Status: No model loaded", foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=3)
        
        # ===== Text Input Section =====
        input_frame = ttk.LabelFrame(main_frame, text="Text Input", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)
        
        # Input method selection
        method_frame = ttk.Frame(input_frame)
        method_frame.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.input_method = tk.StringVar(value="text")
        ttk.Radiobutton(method_frame, text="Text Input", variable=self.input_method, 
                       value="text", command=self.toggle_input_method).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="From File", variable=self.input_method, 
                       value="file", command=self.toggle_input_method).pack(side=tk.LEFT, padx=5)
        
        # Text input area
        self.text_input = scrolledtext.ScrolledText(input_frame, height=10, width=70, wrap=tk.WORD)
        self.text_input.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # File input (hidden by default)
        self.file_frame = ttk.Frame(input_frame)
        self.text_file_var = tk.StringVar()
        ttk.Entry(self.file_frame, textvariable=self.text_file_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(self.file_frame, text="Browse...", command=self.browse_text_file).pack(side=tk.LEFT)
        
        # ===== Output Section =====
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_path_var = tk.StringVar(value="output.wav")
        ttk.Entry(output_frame, textvariable=self.output_path_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).grid(row=0, column=2, pady=5)
        
        # ===== Generate Button =====
        self.generate_btn = ttk.Button(main_frame, text="Generate Audio", command=self.generate_audio, state="disabled")
        self.generate_btn.grid(row=3, column=0, columnspan=3, pady=10)
        
        # ===== Progress/Log Section =====
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=70, wrap=tk.WORD, state="disabled")
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
    
    def on_model_type_change(self):
        """Handle model type selection changes."""
        # Reset model state when switching types
        self.model = None
        self.status_label.config(text="Status: No model loaded", foreground="red")
        self.generate_btn.config(state="disabled")
        
        model_type = self.model_type_var.get()
        self.log(f"{model_type.capitalize()} model selected")
    
    def toggle_input_method(self):
        """Switch between text input and file input."""
        if self.input_method.get() == "text":
            self.file_frame.grid_forget()
            self.text_input.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        else:
            self.text_input.grid_forget()
            self.file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
    
    def log(self, message):
        """Add message to log."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
    
    def browse_model(self):
        """Browse for model folder."""
        folder = filedialog.askdirectory(title="Select Model Folder")
        if folder:
            self.model_path_var.set(folder)
            self.log(f"Model folder selected: {folder}")
    
    def browse_audio(self):
        """Browse for reference audio file."""
        file = filedialog.askopenfilename(
            title="Select Reference Audio",
            filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.ogg"), ("All Files", "*.*")]
        )
        if file:
            self.audio_path_var.set(file)
            self.log(f"Reference audio selected: {file}")
    
    def browse_text_file(self):
        """Browse for text file."""
        file = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file:
            self.text_file_var.set(file)
            self.log(f"Text file selected: {file}")
    
    def browse_output(self):
        """Browse for output file location."""
        file = filedialog.asksaveasfilename(
            title="Save Audio As",
            defaultextension=".wav",
            filetypes=[("WAV Files", "*.wav"), ("All Files", "*.*")]
        )
        if file:
            self.output_path_var.set(file)
            self.log(f"Output file: {file}")
    
    def load_model(self):
        """Load the TTS model."""
        self.is_turbo = self.model_type_var.get() == "turbo"
        
        # Check if turbo is available
        if self.is_turbo and not TURBO_AVAILABLE:
            messagebox.showerror("Error", "Turbo model is not installed.\n\nPlease install it or use the standard model.")
            return
        
        # Get model path and audio path
        model_path = self.model_path_var.get()
        audio_path = self.audio_path_var.get()
        
        # Check if model folder is selected
        if not model_path:
            messagebox.showerror("Error", "Please select a model folder")
            return
        
        # Check if reference audio is selected
        if not audio_path:
            messagebox.showerror("Error", "Please select a reference audio file")
            return
        
        def load_thread():
            try:
                self.load_btn.config(state="disabled")
                self.status_label.config(text="Status: Loading model...", foreground="orange")
                
                device = self.device_var.get()
                model_path_str = model_path  # Capture in closure
                audio_path_str = audio_path  # Capture in closure
                
                if self.is_turbo:
                    self.log(f"Loading Turbo model from: {model_path_str}")
                    self.model = ChatterboxTurboTTS.from_local(Path(model_path_str), device=device)
                    self.model_dir = Path(model_path_str)
                    self.log("Turbo model loaded successfully!")
                else:
                    self.log("Loading standard model...")
                    self.model = ChatterboxTTS.from_local(Path(model_path_str), device=device)
                    self.model_dir = Path(model_path_str)
                    
                    self.log("Preparing conditionals from reference audio...")
                    self.model.prepare_conditionals(Path(audio_path_str))
                    self.log("Standard model loaded successfully!")
                
                self.reference_audio = Path(audio_path_str)
                self.status_label.config(text="Status: Model loaded ✓", foreground="green")
                self.generate_btn.config(state="normal")
                
            except Exception as e:
                self.status_label.config(text="Status: Load failed", foreground="red")
                self.log(f"Error loading model: {str(e)}")
                messagebox.showerror("Error", f"Failed to load model:\n{str(e)}")
            finally:
                self.load_btn.config(state="normal")
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
    
    def generate_audio(self):
        """Generate audio from text."""
        if self.model is None:
            messagebox.showerror("Error", "Please load a model first")
            return
        
        # Get text input
        if self.input_method.get() == "text":
            text = self.text_input.get("1.0", tk.END).strip()
            if not text:
                messagebox.showerror("Error", "Please enter text to generate")
                return
        else:
            text_file = self.text_file_var.get()
            if not text_file:
                messagebox.showerror("Error", "Please select a text file")
                return
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                if not text:
                    messagebox.showerror("Error", "Text file is empty")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read text file:\n{str(e)}")
                return
        
        output_path = self.output_path_var.get()
        if not output_path:
            messagebox.showerror("Error", "Please specify an output file")
            return
        
        def generate_thread():
            try:
                self.generating = True
                self.generate_btn.config(state="disabled", text="Generating...")
                self.log(f"Generating audio for text: {text[:50]}...")
                
                # Generate based on model type
                if self.is_turbo:
                    # Turbo model uses audio_prompt_path in generate()
                    wav = self.model.generate(text, audio_prompt_path=str(self.reference_audio))
                else:
                    # Standard model uses pre-prepared conditionals
                    wav = self.model.generate(text)
                
                self.log(f"Saving to: {output_path}")
                ta.save(output_path, wav, self.model.sr)
                
                self.log(f"✓ Audio saved successfully to {output_path}")
                messagebox.showinfo("Success", f"Audio generated successfully!\n\nSaved to: {output_path}")
                
            except Exception as e:
                self.log(f"✗ Error generating audio: {str(e)}")
                messagebox.showerror("Error", f"Failed to generate audio:\n{str(e)}")
            finally:
                self.generating = False
                self.generate_btn.config(state="normal", text="Generate Audio")
        
        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = ChatterboxGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()