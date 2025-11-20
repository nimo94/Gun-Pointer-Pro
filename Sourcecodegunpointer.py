#NOTICE/WARNING THIS CODE SOLELY CREATED BY DEV. ASWINDRA SELVAM AND
#DEV.GANESAN SELVERAJU
#© GUNPOINTER 2025
#v1.0b
import customtkinter as ctk
import threading
import math
import re
import os
import difflib
import time
import random
import webbrowser
from collections import Counter
from tkinter import filedialog

#REASON USED SERPAPI BECAUSE NEED TO BYPASS GOOGLE BOT DETECTION
SERP_API_KEY = "REPLACETTHEAPIKEY" #SERPAPIKEY

try:
    import docx #TO READ DOCX FILE

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


try:
    import fitz  # PyMuPDF TO READ PDF FILE

    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False


try:
    import PyPDF2 #PyPDF2 ALTERNATIVE PDF READER

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from serpapi import GoogleSearch #SERPAPI

    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False


class LogicEngine: #THE HEART OF THE SYSTEM
    def __init__(self, api_key):
        self.api_key = api_key


    def clean_text_for_search(self, text): #TO FILTER OUT NOT NEEDED TEXT CONTENTS TO MAKE THE SEARCH ACCURATE AND EASY
        text = re.sub(r'^\s*\d+[\.)]?\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*[a-zA-Z][\.)]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\(\d+\s*marks?\)', '', text, flags=re.IGNORECASE)
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def get_search_chunks(self, text, chunk_size=12): #TO GET THE RANDOM CHUNKS OF TEXT TO SEARCH IN WEB
        words = text.split()
        if len(words) < chunk_size: return [text]
        chunks = []
        for i in range(0, len(words) - chunk_size + 1, 6):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def get_sentences(self, text): #COLLABRATE WITH GET CHUNKS
        return [s.strip() for s in re.split(r'[.!?]+', text) if len(s.split()) > 3]

    def preprocess(self, text): #PRE PROCESS THE TEXT FUTHER MORE
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower().split()

    def load_file(self, file_path): #LOAD THE FILE
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        text = ""

        try:
            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

            elif ext == '.docx':
                if not DOCX_AVAILABLE: return "ERROR: python-docx library missing."
                doc = docx.Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])

            elif ext == '.pdf':

                if FITZ_AVAILABLE:
                    try:
                        with fitz.open(file_path) as doc:
                            for page in doc:
                                text += page.get_text() + "\n"
                    except Exception:
                        pass

                if not text.strip() and PDF_AVAILABLE:
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            extracted = page.extract_text()
                            if extracted: text += extracted + "\n"

                if not FITZ_AVAILABLE and not PDF_AVAILABLE:
                    return "ERROR: No PDF library found. Please run: pip install pymupdf" #DISPLAYING FRIENDLY ERROR

            else:
                return "Unsupported file format."

            # VALIDATION
            if not text or len(text.strip()) < 10: #IF NO TEXT FOUND WARNING WILL BE OUT
                return "WARNING: No readable text found in this file. It might be scanned images or encrypted."

            return text

        except Exception as e:
            return f"Error reading file: {str(e)}"


    def search_web(self, query): #SEARCH THE WEB USING SERPAPI AND CHUNKS OF THE TEXT
        if not SERPAPI_AVAILABLE or not self.api_key or "PASTE" in self.api_key: return []
        results = []
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": 3,
                "hl": "en",
                "gl": "us"
            }
            search = GoogleSearch(params)
            data = search.get_dict()
            for r in data.get("organic_results", []):
                results.append({
                    'title': r.get('title'),
                    'link': r.get('link'),
                    'snippet': r.get('snippet', '')
                })
        except Exception:
            pass
        return results


    def check_plagiarism(self, text, log_callback, progress_callback): #WILL BE SEARCHING FOR SIMILARITY
        log_callback("\n🔎 Scanning content against the web...")

        found_sources = []
        total_similarity_sum = 0.0
        total_checked = 0


        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 10] #PROCESS OF EXTRACTING TITLE
        if lines:
            raw_title = self.clean_text_for_search(lines[0])
            search_title = " ".join(raw_title.split()[:15])

            title_res = self.search_web(f'"{search_title}"')
            if title_res:
                found_sources.append((title_res[0]['title'], title_res[0]['link']))
                total_similarity_sum += 1.0
                total_checked += 1


        clean_text = self.clean_text_for_search(text)
        chunks = self.get_search_chunks(clean_text, chunk_size=10)

        indices = [0, len(chunks) // 2, len(chunks) - 1]
        if len(chunks) > 5: indices.append(random.randint(1, len(chunks) - 2))
        if len(chunks) > 10: indices.append(random.randint(1, len(chunks) - 2))
        indices = sorted(list(set(indices)))

        step_size = 0.8 / len(indices) if indices else 0
        current_progress = 0.1

        for idx in indices:
            if idx >= len(chunks): continue
            chunk = chunks[idx]
            total_checked += 1

            results = self.search_web(f'"{chunk}"')
            if not results: results = self.search_web(chunk)

            best_sim = 0
            best_info = {}

            for res in results:
                matcher = difflib.SequenceMatcher(None, chunk.lower(), res['snippet'].lower())
                ratio = matcher.ratio()
                if chunk.lower() in res['snippet'].lower(): ratio = 1.0
                if ratio > best_sim:
                    best_sim = ratio
                    best_info = res

            total_similarity_sum += best_sim

            if best_sim > 0.35:
                found_sources.append((best_info['title'], best_info['link']))

            current_progress += step_size
            progress_callback(current_progress)

        score = 0
        if total_checked > 0:
            score = int((total_similarity_sum / total_checked) * 100)

        if score == 0 and found_sources: #DISPLAY SCORE
            score = 100

        return score, found_sources
        
    def check_ai(self, text): #AI CHECKER IN THE LOGIC OF Stylometric Estimate
        clean_text = self.clean_text_for_search(text)
        sentences = self.get_sentences(clean_text)

        if not sentences: return 0, (0, 0)

        lengths = [len(s.split()) for s in sentences]
        if not lengths: return 0, (0, 0)

        avg_len = sum(lengths) / len(lengths)
        variance = sum((x - avg_len) ** 2 for x in lengths) / len(lengths)
        std_dev = math.sqrt(variance)

        words = self.preprocess(text)
        diversity = len(set(words)) / len(words) if words else 0

        ai_prob = 0
        if std_dev < 5:
            ai_prob += 40
        elif std_dev < 12:
            ai_prob += 20
        if diversity < 0.45:
            ai_prob += 40
        elif diversity < 0.65:
            ai_prob += 20
        ai_prob = min(99, ai_prob)

        return ai_prob, (std_dev, diversity)



# ASSGANE GUI ENGINE
#GRAPCHICAL USER INTERFACE ENGINE BULD BY US
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gun Pointer Pro") #TITLE OF THE APP
        self.geometry("950x700")
        self.engine = None
        self.current_file_text = ""
        self.link_counter = 0

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="🔫 Gun Pointer", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.upload_btn = ctk.CTkButton(self.sidebar, text="📂 Upload & Scan", command=self.upload_file, height=40,
                                        font=("Arial", 14, "bold"))
        self.upload_btn.grid(row=1, column=0, padx=20, pady=20)

        self.status_label = ctk.CTkLabel(self.sidebar, text="V1.0b", text_color="gray")
        self.status_label.grid(row=3, column=0, padx=20, pady=10, sticky="s")


        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)


        self.card_ai = self.create_card(self.main_frame, "AI Probability", "0%", row=0, col=0, color="#3B8ED0")
        self.card_plag = self.create_card(self.main_frame, "Plagiarism Score", "0%", row=0, col=1, color="#E04F5F")


        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(20, 10))
        self.progress_bar.set(0)


        self.log_box = ctk.CTkTextbox(self.main_frame, height=400, font=("Segoe UI", 13))
        self.log_box.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.log_box.insert("0.0", "Waiting for file...\n")
        self.main_frame.grid_rowconfigure(2, weight=1)


        self.log_box._textbox.tag_config("link", foreground="#3399FF", underline=True)

    def create_card(self, parent, title, value, row, col, color):
        frame = ctk.CTkFrame(parent, fg_color=color)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        label_title = ctk.CTkLabel(frame, text=title, text_color="white", font=("Arial", 14))
        label_title.pack(pady=(10, 0))
        label_val = ctk.CTkLabel(frame, text=value, text_color="white", font=("Arial", 32, "bold"))
        label_val.pack(pady=(0, 10))
        return label_val


    def animate_score(self, label_widget, start, end, duration=1000):
        steps = 20
        step_time = duration // steps
        step_value = (end - start) / steps

        def step(current_step):
            if current_step <= steps:
                value = int(start + (step_value * current_step))
                label_widget.configure(text=f"{value}%")
                self.after(step_time, lambda: step(current_step + 1))
            else:
                label_widget.configure(text=f"{end}%")

        step(0)


    def log(self, message):
        url_pattern = r'(https?://\S+)'
        parts = re.split(url_pattern, message)
        for part in parts:
            if re.match(url_pattern, part):
                tag_name = f"link_{self.link_counter}"
                self.link_counter += 1
                self.log_box.insert("end", part, tag_name)

                def open_url(event, url=part):
                    webbrowser.open(url)

                self.log_box._textbox.tag_bind(tag_name, "<Button-1>", open_url)
                self.log_box._textbox.tag_add("link", "end-1c wordstart", "end-1c wordend")
            else:
                self.log_box.insert("end", part)
        self.log_box.insert("end", "\n")
        self.log_box.see("end")

    def clear_previous_scan(self):
        self.log_box.delete("0.0", "end")
        self.progress_bar.set(0)
        self.card_ai.configure(text="0%")
        self.card_plag.configure(text="0%")

    def upload_file(self):
        self.clear_previous_scan()
        file_path = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.docx *.txt")])
        if file_path:
            self.engine = LogicEngine(SERP_API_KEY)
            text = self.engine.load_file(file_path)

            # Stop if error
            if text.startswith("ERROR") or text.startswith("WARNING") or text.startswith("Unsupported"):
                self.log(f"❌ {text}")
            else:
                self.current_file_text = text
                self.log(f"✅ Loaded: {os.path.basename(file_path)}")
                self.log(f"   Length: {len(text.split())} words")
                self.start_scan_thread()

    def start_scan_thread(self):
        self.upload_btn.configure(state="disabled")
        self.status_label.configure(text="Scanning...", text_color="orange")
        self.progress_bar.set(0)
        self.card_ai.configure(text="...")
        self.card_plag.configure(text="...")
        threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        self.log("\n⚙️  Analyzing Writing Style...")
        ai_score, (burst, div) = self.engine.check_ai(self.current_file_text)
        self.after(0, lambda: self.animate_score(self.card_ai, 0, ai_score))
        self.progress_bar.set(0.3)

        plag_score, sources = self.engine.check_plagiarism(
            self.current_file_text,
            self.log,
            self.update_progress
        )
        self.after(0, lambda: self.animate_score(self.card_plag, 0, plag_score))
        self.progress_bar.set(1.0)

        self.log("\n\n📊 RESULTS SUMMARY")
        self.log("===================================")

        if sources:
            self.log(f"🚨 SUSPICIOUS SOURCES FOUND ({len(sources)}):")
            counts = Counter(sources)
            for i, ((title, link), count) in enumerate(counts.most_common(5), 1):
                self.log(f"\n{i}. {title}")
                self.log(f"🔗 {link}")
        else:
            self.log("✅ No direct plagiarism detected.")

        self.upload_btn.configure(state="normal")
        self.status_label.configure(text="Scan Complete", text_color="#4ADE80")

    def update_progress(self, val):
        self.progress_bar.set(val)


if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()




