import queue
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from pdf_converter import pdf_to_dark_mode

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PRESETS = {
    "Classic Dark": ((28, 31, 38), (232, 235, 241)),
    "Ocean Blue": ((16, 35, 55), (220, 239, 255)),
    "Forest Green": ((20, 39, 30), (224, 242, 226)),
    "Deep Purple": ((39, 29, 51), (241, 229, 255)),
    "Warm Sepia": ((48, 39, 30), (246, 230, 204)),
}


class SmartPDFApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SmartPDF | PDF Dark Mode")
        self.geometry("850x650")
        self.minsize(760, 750)

        self.events = queue.Queue()
        self.source = ctk.StringVar()
        self.output = ctk.StringVar()
        self.dpi = ctk.StringVar(value="144")
        self.format = ctk.StringVar(value="PNG")
        self.quality = ctk.StringVar(value="90")
        self.preserve = ctk.BooleanVar(value=True)
        self.preset = ctk.StringVar(value="Classic Dark")

        self.build_ui()
        self.after(100, self.check_events)

    def build_ui(self):
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=35, pady=25)

        ctk.CTkLabel(root, text="SmartPDF", font=("Arial", 30, "bold")).pack(anchor="w")
        ctk.CTkLabel(root, text="Convert your PDF into a comfortable dark theme.", text_color="#929BAA").pack(anchor="w", pady=(3, 22))

        files = self.card(root, "01  /  PDF FILES")
        self.file_row(files, "Source PDF", self.source, self.pick_source)
        self.file_row(files, "Save as", self.output, self.pick_output)

        settings = self.card(root, "02  /  SETTINGS")
        grid = ctk.CTkFrame(settings, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 12))
        grid.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(grid, text="Format").grid(row=0, column=0, sticky="w", pady=6)
        ctk.CTkSegmentedButton(grid, values=["PNG", "JPEG"], variable=self.format, command=self.toggle_quality_state).grid(row=1, column=0, sticky="ew", padx=(0, 12))

        ctk.CTkLabel(grid, text="Color preset").grid(row=2, column=0, sticky="w", pady=(14, 6))
        ctk.CTkOptionMenu(grid, values=list(PRESETS), variable=self.preset).grid(row=3, column=0, sticky="ew", padx=(0, 12))

        ctk.CTkLabel(grid, text="Resolution (DPI)").grid(row=0, column=1, sticky="w", pady=6)
        ctk.CTkOptionMenu(grid, values=["96", "120", "144", "180", "200", "240", "300", "400"], variable=self.dpi).grid(row=1, column=1, sticky="ew", padx=(12, 0))

        row = ctk.CTkFrame(settings, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 12))
        
        self.quality_label = ctk.CTkLabel(row, text="JPEG quality")
        self.quality_label.pack(side="left")
        
        self.quality_entry = ctk.CTkEntry(row, textvariable=self.quality, width=85)
        self.quality_entry.pack(side="right")
        
        self.quality_entry.configure(state="disabled")
        self.quality_label.configure(text_color="#697383")

        ctk.CTkCheckBox(
            settings, text="Preserve original images and illustrations",
            variable=self.preserve, fg_color="#4263EB",
            hover_color="#3451C5", checkmark_color="white"
        ).pack(anchor="w", padx=20, pady=(0, 18))

        self.status = ctk.CTkLabel(root, text="Ready.", text_color="#929BAA")
        self.status.pack(anchor="w", pady=(8, 8))
        self.progress = ctk.CTkProgressBar(root, height=8)
        self.progress.pack(fill="x")
        self.progress.set(0)

        self.convert_btn = ctk.CTkButton(root, text="Convert PDF", height=46, command=self.convert)
        self.convert_btn.pack(fill="x", pady=18)

        ctk.CTkLabel(root, text="Your original PDF is never modified.", text_color="#697383").pack()

    def toggle_quality_state(self, selected_value):
        if selected_value == "JPEG":
            self.quality_entry.configure(state="normal")
            self.quality_label.configure(text_color=("gray10", "gray90"))
        else:
            self.quality_entry.configure(state="disabled")
            self.quality_label.configure(text_color="#697383")

    def card(self, parent, title):
        frame = ctk.CTkFrame(parent, fg_color="#191E27", corner_radius=14)
        frame.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(frame, text=title, text_color="#8793A6", font=("Arial", 11, "bold")).pack(anchor="w", padx=20, pady=14)
        return frame

    def file_row(self, parent, label, variable, command):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(row, text=label, width=125, anchor="w").pack(side="left")
        ctk.CTkEntry(row, textvariable=variable).pack(side="left", fill="x", expand=True, padx=8)
        ctk.CTkButton(row, text="Browse", width=85, command=command).pack(side="right")

    def pick_source(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.source.set(path)
            if not self.output.get():
                file = Path(path)
                self.output.set(str(file.with_name(file.stem + "_dark.pdf")))

    def pick_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if path:
            self.output.set(path)

    def convert(self):
        source, output = self.source.get().strip(), self.output.get().strip()
        if not source or not output:
            return messagebox.showwarning("Missing file", "Select input and output PDF.")

        try:
            dpi = int(self.dpi.get())
            if not 72 <= dpi <= 400:
                raise ValueError("DPI must be between 72 and 400.")
            
            quality = 90
            if self.format.get() == "JPEG":
                quality = int(self.quality.get())
                if not 40 <= quality <= 100:
                    raise ValueError("Quality must be between 40 and 100.")
                    
        except ValueError as error:
            return messagebox.showerror("Invalid settings", str(error))

        settings = (source, output, dpi, quality, self.format.get(), self.preserve.get(), PRESETS[self.preset.get()])
        self.convert_btn.configure(state="disabled", text="Converting...")
        self.progress.set(0)
        self.status.configure(text="Starting conversion...")
        threading.Thread(target=self.worker, args=settings, daemon=True).start()

    def worker(self, source, output, dpi, quality, fmt, preserve, palette):
        try:
            pdf_to_dark_mode(
                source, output, dpi=dpi, output_format=fmt, quality=quality,
                preserve_images=preserve, background=palette[0], foreground=palette[1],
                progress_callback=lambda done, total: self.events.put(("progress", done, total))
            )
            self.events.put(("done", output))
        except Exception as error:
            self.events.put(("error", str(error)))

    def check_events(self):
        try:
            while True:
                event, *data = self.events.get_nowait()
                if event == "progress":
                    done, total = data
                    self.progress.set(done / total if total else 0)
                    self.status.configure(text=f"Processing pages: {done}/{total}")
                else:
                    self.convert_btn.configure(state="normal", text="Convert PDF")
                    if event == "done":
                        self.progress.set(1)
                        self.status.configure(text="Conversion completed.")
                        messagebox.showinfo("Done", f"Saved to:\n{data[0]}")
                    else:
                        self.status.configure(text="Conversion failed.")
                        messagebox.showerror("Conversion error", data[0])
        except queue.Empty:
            pass
        self.after(100, self.check_events)


if __name__ == "__main__":
    SmartPDFApp().mainloop()