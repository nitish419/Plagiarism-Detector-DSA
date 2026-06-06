import customtkinter as ctk
from tkinter import messagebox, filedialog
import os

# Document parsing libraries
import docx
import PyPDF2

# Import the DSA logic
from preprocessor import get_sentences
from algorithms import kmp_search

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PlagiarismApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Plagiarism Detector - String Matching Algorithms")
        self.geometry("950x750")
        self.minsize(800, 650)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkLabel(self, text="Plagiarism Detector", font=ctk.CTkFont(size=28, weight="bold"))
        self.header.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # --- Original Text Area (Left) ---
        self.orig_frame = ctk.CTkFrame(self)
        self.orig_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.orig_label = ctk.CTkLabel(self.orig_frame, text="Original Source Text", font=ctk.CTkFont(size=16, weight="bold"))
        self.orig_label.pack(pady=(10, 5))
        
        # Upload Button for Original
        self.orig_upload_btn = ctk.CTkButton(self.orig_frame, text="Upload Document", command=lambda: self.browse_file(self.orig_textbox))
        self.orig_upload_btn.pack(pady=(0, 10))

        self.orig_textbox = ctk.CTkTextbox(self.orig_frame, wrap="word", font=ctk.CTkFont(size=14))
        self.orig_textbox.pack(expand=True, fill="both", padx=15, pady=(0, 15))

        # --- Submitted Text Area (Right) ---
        self.sub_frame = ctk.CTkFrame(self)
        self.sub_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        self.sub_label = ctk.CTkLabel(self.sub_frame, text="Submitted Document", font=ctk.CTkFont(size=16, weight="bold"))
        self.sub_label.pack(pady=(10, 5))
        
        # Upload Button for Submitted
        self.sub_upload_btn = ctk.CTkButton(self.sub_frame, text="Upload Document", command=lambda: self.browse_file(self.sub_textbox))
        self.sub_upload_btn.pack(pady=(0, 10))

        self.sub_textbox = ctk.CTkTextbox(self.sub_frame, wrap="word", font=ctk.CTkFont(size=14))
        self.sub_textbox.pack(expand=True, fill="both", padx=15, pady=(0, 15))

        # --- Action Button ---
        self.detect_btn = ctk.CTkButton(self, text="Run KMP Algorithm", command=self.run_detection, height=45, font=ctk.CTkFont(size=16, weight="bold"))
        self.detect_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # --- Results Area (Bottom) ---
        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="nsew")
        
        self.score_label = ctk.CTkLabel(self.result_frame, text="Plagiarism Score: 0.00%", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1f6aa5")
        self.score_label.pack(pady=5)

        self.result_textbox = ctk.CTkTextbox(self.result_frame, wrap="word", height=120, font=ctk.CTkFont(size=14))
        self.result_textbox.pack(expand=True, fill="both", padx=10, pady=5)
        self.result_textbox.insert("0.0", "Matched content will appear here after analysis...")
        self.result_textbox.configure(state="disabled")

    # --- NEW FILE UPLOAD LOGIC ---
    def browse_file(self, target_textbox):
        filepath = filedialog.askopenfilename(
            title="Select a Document",
            filetypes=[
                ("Text/Word/PDF Files", "*.txt *.docx *.pdf"),
                ("Text Files", "*.txt"),
                ("Word Documents", "*.docx"),
                ("PDF Files", "*.pdf"),
                ("All Files", "*.*")
            ]
        )
        
        if not filepath:
            return # User canceled

        try:
            extracted_text = ""
            ext = os.path.splitext(filepath)[1].lower()

            if ext == ".txt":
                with open(filepath, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            
            elif ext == ".docx":
                doc = docx.Document(filepath)
                extracted_text = "\n".join([para.text for para in doc.paragraphs])
            
            elif ext == ".pdf":
                with open(filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    extracted_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            else:
                messagebox.showerror("Unsupported File", "Please upload a .txt, .docx, or .pdf file.")
                return

            # Clear the textbox and insert the newly extracted text
            target_textbox.delete("1.0", "end")
            target_textbox.insert("1.0", extracted_text)

        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{str(e)}")

    # --- EXISTING DETECTION LOGIC ---
    def run_detection(self):
        orig_text = self.orig_textbox.get("1.0", "end-1c")
        sub_text = self.sub_textbox.get("1.0", "end-1c")

        if not orig_text.strip() or not sub_text.strip():
            messagebox.showwarning("Missing Input", "Please upload or paste text into both fields.")
            return

        orig_sentences = get_sentences(orig_text)
        sub_sentences = get_sentences(sub_text)

        if not sub_sentences:
            self.update_results(0, ["Not enough valid text to analyze."])
            return

        orig_clean_full = " ".join(orig_sentences)
        matched_sentences = []

        for sentence in sub_sentences:
            if kmp_search(orig_clean_full, sentence):
                matched_sentences.append(sentence)

        score = (len(matched_sentences) / len(sub_sentences)) * 100
        self.update_results(score, matched_sentences)

    def update_results(self, score, matches):
        color = "#00cc66" if score == 0 else "#ffcc00" if score < 40 else "#ff4d4d"
        self.score_label.configure(text=f"Plagiarism Score: {score:.2f}%", text_color=color)
        
        self.result_textbox.configure(state="normal")
        self.result_textbox.delete("1.0", "end")
        
        if matches and score > 0:
            self.result_textbox.insert("end", f"🚨 Found {len(matches)} plagiarized sentences:\n\n")
            for i, match in enumerate(matches, 1):
                self.result_textbox.insert("end", f"{i}. {match}\n")
        else:
            self.result_textbox.insert("end", "✅ No plagiarism detected. 100% Original!")
            
        self.result_textbox.configure(state="disabled")

if __name__ == "__main__":
    app = PlagiarismApp()
    app.mainloop()