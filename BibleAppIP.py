import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import requests
import urllib.parse
import sys
from bible_lookup import fetch_bible_verse



# def lookup_verse_gui(self):
    # reference = self.verse_entry.get().strip()
    # text = lookup_verse(reference)
    # self.text_area.delete("1.0", tk.END)
    # self.text_area.insert(tk.END, text)

# ---------------------------------------------------------
# Path setup
# ---------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INTERPRETATIONS_FILE = os.path.join(SCRIPT_DIR, "interpretations.json")

# ---------------------------------------------------------
# Load interpretations
# ---------------------------------------------------------


def load_interpretations():
    try:
        with open(INTERPRETATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        messagebox.showerror(
            "Error", f"interpretations.json not found at:\n{INTERPRETATIONS_FILE}")
        return {}
    except json.JSONDecodeError as e:
        messagebox.showerror(
            "Error", f"interpretations.json is not valid JSON.\n{e}")
        return {}


# ---------------------------------------------------------
# Fetch verse
# ---------------------------------------------------------
# ---------------------------------------------------------
# Fetch verse (ESV)
# ---------------------------------------------------------
ESV_API_KEY = "7580d95a1be11f5097f01d04f98f6d6d999d2768"

headers = {
    "Authorization": f"Token {ESV_API_KEY}"
}


def fetch_bible_verse(reference):
    """
    Fetch verse text AND ESV footnotes from the ESV API.
    Returns: (verse_text_with_footnotes, source_or_error)
    """

    params = {
        "q": reference,
        "include-passage-references": False,
        "include-footnotes": True,
        "include-headings": False,
        "include-verse-numbers": True,
        "include-short-copyright": False,
    }

    url = "https://api.esv.org/v3/passage/text/"

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return None, f"ESV API error: {e}"

    passages = data.get("passages")
    footnotes = data.get("footnotes", [])

    if not passages:
        return None, "No passage text returned from ESV API."

    verse_text = "\n".join(p.strip() for p in passages)

    if footnotes:
        verse_text += "\n\nESV FOOTNOTES:\n"
        for fn in footnotes:
            verse_text += f"- {fn}\n"

    return verse_text, "English Standard Version (ESV)"


# ---------------------------------------------------------
# GUI Application
# ---------------------------------------------------------


class BibleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bible Verse Lookup GUI")
        self.root.minsize(800, 800)

        self.interpretations = load_interpretations()

        # Call AFTER setting title, BEFORE widgets
        self.center_window(800, 800)

        # Now your widgets
        # ----tk.Label(root, text="Bible Verse Lookup",
        # ---         font=("Arial", 20, "bold")).pack(pady=10)

        ...
        # all your other widgets
        ...

        # ============================
        # MAIN CONTAINER
        # ============================
        main = tk.Frame(root, padx=15, pady=15)
        main.pack(fill=tk.BOTH, expand=True)

        # ============================
        # HEADER
        # ============================
        tk.Label(
            main,
            text="Bible Verse Lookup",
            font=("Arial", 22, "bold")
        ).pack(pady=(0, 15))

        # ============================
        # VERSE LOOKUP SECTION
        # ============================
        lookup_frame = tk.Frame(main)
        lookup_frame.pack(fill=tk.X, pady=5)

        tk.Label(lookup_frame, text="Enter Verse:", font=(
            "Arial", 12)).grid(row=0, column=0, padx=5)
        self.verse_entry = tk.Entry(lookup_frame, width=40, font=("Arial", 12))
        self.verse_entry.grid(row=0, column=1, padx=5)

        tk.Button(
            lookup_frame,
            text="Lookup Verse",
            command=self.lookup_verse
        ).grid(row=0, column=2, padx=5)

        # ============================
        # INTERPRETATION LIST SECTION
        # ============================
        list_frame = tk.LabelFrame(
            main,
            text="Available Interpretations",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=14
        )
        list_frame.pack(fill=tk.X, pady=10)

        self.listbox = tk.Listbox(
            list_frame, width=40, height=10, font=("Arial", 12))
        self.listbox.pack(side=tk.LEFT, fill=tk.X)

        scroll = tk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=self.listbox.yview)

        for ref in self.interpretations.keys():
            self.listbox.insert(tk.END, ref)

        self.listbox.bind("<<ListboxSelect>>",
                          self.load_selected_interpretation)

        # ============================
        # BIBLE VERSE TEXT SECTION
        # ============================
        verse_frame = tk.LabelFrame(
            main,
            text="Bible Verse Text",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=12
        )

        self.text_area = tk.Text(
            verse_frame,
            wrap=tk.WORD,
            font=("Arial", 12),
            height=12
        )
        verse_frame.pack(fill=tk.X, pady=10)
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # ============================
        # INTERPRETATION EDITOR

        interp_frame = tk.LabelFrame(
            main,
            text="Enter / Edit Interpretation",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        interp_frame.pack(fill=tk.BOTH, pady=10)

        self.interpretation_box = tk.Text(
            interp_frame,
            wrap=tk.WORD,
            font=("Arial", 12),
            height=2
        )
        self.interpretation_box.pack(fill=tk.BOTH, expand=True)

        # ============================
        # BUTTONS SECTION
        # ============================
        btn_frame = tk.Frame(main)
        btn_frame.pack(pady=10)

        btn_style = {"font": ("Arial", 11), "width": 18}

        tk.Button(btn_frame, text="Clear Results", command=self.clear_results,
                  **btn_style).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Copy to Clipboard",
                  command=self.copy_to_clipboard, **btn_style).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Save Interpretation",
                  command=self.save_interpretation, **btn_style).grid(row=0, column=2, padx=5)

        # Interpretation management buttons
        interp_btn_frame = tk.Frame(main)
        interp_btn_frame.pack(pady=10)

        tk.Button(interp_btn_frame, text="Add Interpretation",
                  command=self.add_interpretation, **btn_style).grid(row=0, column=0, padx=5)
        tk.Button(interp_btn_frame, text="Update Interpretation",
                  command=self.update_interpretation, **btn_style).grid(row=0, column=1, padx=5)
        tk.Button(interp_btn_frame, text="Delete Interpretation",
                  command=self.delete_interpretation, **btn_style).grid(row=0, column=2, padx=5)
        

        btn_style = {"font": ("Arial", 11), "width": 18}

        interp_btn_frame = tk.Frame(main)
        interp_btn_frame.pack(pady=10)

        self.root.update_idletasks()
        self.root.resizable(False, False)

    # -----------------------------------------------------

    def lookup_verse(self):
        reference = self.verse_entry.get().strip()
        if not reference:
            messagebox.showwarning("Warning", "Please enter a verse.")
        return

        verse_text, raw_json = fetch_bible_verse(reference)
        interpretation = self.interpretations.get(reference)

        self.text_area.delete("1.0", tk.END)

        if verse_text is None:
            self.text_area.insert(tk.END, "Error fetching verse.\n\n")
            self.text_area.insert(tk.END, f"RAW JSON:\n{raw_json}\n")
        return

        # Display verse text
        self.text_area.insert(tk.END, f"Bible Verse: {reference}\n\n")
        self.text_area.insert(tk.END, f"VERSE:\n{verse_text}\n\n")

    # Display JSON
        self.text_area.insert(tk.END, "JSON RECORD:\n")
        self.text_area.insert(tk.END, f"{raw_json}\n\n")

        # Display interpretation
        if interpretation:
            self.text_area.insert(
            tk.END,
            f"INTERPRETATION:\n{interpretation.get('interpretation', 'No interpretation text found.')}\n"
        )
        else:
            self.text_area.insert(tk.END, "No interpretation found.\n")



        # Lock size AFTER widgets are created

    # -----------------------------------------------------

    def load_selected_interpretation(self, event):
        if not self.listbox.curselection():
            return

        selected = self.listbox.get(self.listbox.curselection())
        self.verse_entry.delete(0, tk.END)
        self.verse_entry.insert(0, selected)

        # Load verse + interpretation
        self.lookup_verse()

        interp = self.interpretations.get(selected, {})
        self.interpretation_box.delete("1.0", tk.END)
        self.interpretation_box.insert(
            tk.END, interp.get("interpretation", "")
        )

    # -----------------------------------------------------
    def clear_results(self):
        self.text_area.delete("1.0", tk.END)

    # -----------------------------------------------------
    def copy_to_clipboard(self):
        text = self.text_area.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Results copied to clipboard.")

    # -----------------------------------------------------
    def save_interpretation(self):
        reference = self.verse_entry.get().strip()
        if not reference:
            messagebox.showwarning("Warning", "Enter a verse reference first.")
            return

        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Nothing to save.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Saved to {save_path}")

            def add_interpretation(self):
                reference = self.verse_entry.get().strip()
                text = self.interpretation_box.get("1.0", tk.END).strip()

            if not reference or not text:
                messagebox.showwarning(
                    "Warning", "Enter verse and interpretation text.")
            return

            self.interpretations[reference] = {
                "verse": reference,
                "interpretation": text
            }

            self.save_interpretations_to_file()
            self.refresh_listbox()
            messagebox.showinfo(
                "Saved", f"Added interpretation for {reference}")

            def add_interpretation(self):
                reference = self.verse_entry.get().strip()
                text = self.interpretation_box.get("1.0", tk.END).strip()

            if not reference or not text:
                messagebox.showwarning(
                "Warning", "Enter verse and interpretation text.")
            return

        self.interpretations[reference] = {
            "verse": reference,
            "interpretation": text
        }

        self.save_interpretations_to_file()
        self.refresh_listbox()
        messagebox.showinfo("Saved", f"Added interpretation for {reference}")

    def add_interpretation(self):
        reference = self.verse_entry.get().strip()
        text = self.interpretation_box.get("1.0", tk.END).strip()

        if not reference or not text:
            messagebox.showwarning(
                "Warning", "Enter verse and interpretation text.")
            return

        self.interpretations[reference] = {
            "verse": reference,
            "interpretation": text
        }
        self.save_interpretations_to_file()
        self.refresh_listbox()
        messagebox.showinfo("Saved", f"Added interpretation for {reference}")

    def delete_interpretation(self):
        reference = self.verse_entry.get().strip()

        if reference in self.interpretations:
            del self.interpretations[reference]
            self.save_interpretations_to_file()
            self.refresh_listbox()
            self.interpretation_box.delete("1.0", tk.END)
            messagebox.showinfo(
                "Deleted", f"Deleted interpretation for {reference}")
        else:
            messagebox.showwarning(
                "Warning", "No interpretation found to delete.")

    def save_interpretations_to_file(self):
        with open(INTERPRETATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.interpretations, f, indent=4)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for ref in sorted(self.interpretations.keys()):
            self.listbox.insert(tk.END, ref)

    def update_interpretation(self):
        reference = self.verse_entry.get().strip()
        text = self.interpretation_box.get("1.0", tk.END).strip()

        if reference not in self.interpretations:
            messagebox.showwarning(
                "Warning", "No existing interpretation to update.")
            return

        self.interpretations[reference]["interpretation"] = text
        self.save_interpretations_to_file()
        messagebox.showinfo(
            "Updated", f"Updated interpretation for {reference}")

     # -------Center Window----------   <-- NOW OUTSIDE __init__

    def center_window(self, width=800, height=900):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 4)

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.update_idletasks()
        self.root.resizable(False, False)


# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BibleApp(root)
    root.mainloop()
