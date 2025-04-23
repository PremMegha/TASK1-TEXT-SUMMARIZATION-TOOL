import subprocess
import sys
import nltk
import tkinter as tk
from tkinter import scrolledtext, messagebox
from transformers import pipeline
import threading

# Install essential libraries (only once)
def install_packages():
    packages = ["transformers", "torch", "nltk"]
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

install_packages()

# Ensure punkt tokenizer is available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# Load model pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", revision="a4f8f3e")

# Start GUI
app = tk.Tk()
app.title("🤖 Text Summarizer Tool")
app.geometry("950x750")
app.config(bg="#202123")

# Fonts
FONT_TITLE = ("Helvetica", 24, "bold")
FONT_LABEL = ("Helvetica", 13)
FONT_TEXT = ("Helvetica", 11)

DARKEST_BLACK = "#0a0a0a"

# --- GUI Layout ---

# Title
tk.Label(app, text="🧠 Text Summarizer Tool", font=FONT_TITLE, bg="#202123", fg="#ffffff").pack(pady=20)

# Token Counter
token_var = tk.StringVar()
token_var.set("Words: 0")
token_label = tk.Label(app, textvariable=token_var, bg="#202123", fg="#ffffff", font=FONT_LABEL)
token_label.pack(anchor="e", padx=20)

# Input Label
tk.Label(app, text="Paste your long content/article here:", font=FONT_LABEL, bg="#202123", fg="#ffffff").pack(anchor="w", padx=20)

# Input Area
input_area = scrolledtext.ScrolledText(app, wrap=tk.WORD, height=15, font=FONT_TEXT, bg=DARKEST_BLACK, fg="#ffffff", insertbackground="#ffffff")
input_area.pack(padx=20, pady=(5, 15), fill="both", expand=True)

# Summary Length Slider
tk.Label(app, text="Set maximum summary length (words):", font=FONT_LABEL, bg="#202123", fg="#ffffff").pack(anchor="w", padx=20)
length_slider = tk.Scale(app, from_=50, to=300, orient=tk.HORIZONTAL, length=300, font=("Helvetica", 10), bg="#202123", fg="#ffffff", troughcolor="#444654", highlightbackground="#202123")
length_slider.set(120)
length_slider.pack(pady=(0, 10))

# Output Label
tk.Label(app, text="Summary Output:", font=FONT_LABEL, bg="#202123", fg="#ffffff").pack(anchor="w", padx=20)

# Output Area
output_area = scrolledtext.ScrolledText(app, wrap=tk.WORD, height=10, font=FONT_TEXT, bg=DARKEST_BLACK, fg="#ffffff", insertbackground="#ffffff")
output_area.pack(padx=20, pady=10, fill="both", expand=True)

# --- Functionalities ---

def update_word_count(event=None):
    text = input_area.get("1.0", tk.END)
    word_count = len(text.strip().split())
    token_var.set(f"Words: {word_count}")

input_area.bind("<KeyRelease>", update_word_count)

def summarize_text():
    text = input_area.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Missing Input", "Please enter some text.")
        return

    output_area.delete("1.0", tk.END)
    output_area.insert(tk.END, "🔄 Summarizing...")
    summarize_btn.config(state="disabled")

    def run_summary():
        try:
            max_len = length_slider.get()
            min_len = max(30, max_len // 2)
            summary = summarizer(text, max_length=max_len, min_length=min_len, do_sample=False)
            output_area.delete("1.0", tk.END)
            output_area.insert(tk.END, summary[0]['summary_text'])
        except Exception as e:
            output_area.delete("1.0", tk.END)
            output_area.insert(tk.END, f"Error: {str(e)}")
        finally:
            summarize_btn.config(state="normal")

    threading.Thread(target=run_summary).start()

def clear_text():
    input_area.delete("1.0", tk.END)
    output_area.delete("1.0", tk.END)
    token_var.set("Words: 0")

# Buttons Frame (Bottom fixed)
btn_frame = tk.Frame(app, bg="#202123")
btn_frame.pack(pady=20)

summarize_btn = tk.Button(btn_frame, text="✨ Summarize", command=summarize_text,
                          font=FONT_LABEL, bg="#10a37f", fg="#ffffff", padx=20, pady=10, activebackground="#0d8b6d")
summarize_btn.grid(row=0, column=0, padx=15)

clear_btn = tk.Button(btn_frame, text="🧹 Clear All", command=clear_text,
                      font=FONT_LABEL, bg="#ef5350", fg="#ffffff", padx=20, pady=10, activebackground="#d32f2f")
clear_btn.grid(row=0, column=1, padx=15)

# Start GUI loop
app.mainloop()
