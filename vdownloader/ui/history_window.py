import customtkinter as ctk
from tkinter import messagebox

from ..history import format_history
from ..config import MAX_HISTORY_DISPLAY


def build_history_window(parent, data, *, on_clear):
    win = ctk.CTkToplevel(parent)
    win.title("Download History")
    win.geometry("600x400")

    textbox = ctk.CTkTextbox(win, wrap="word")
    textbox.pack(fill="both", expand=True, padx=10, pady=10)
    textbox.insert("0.0", format_history(data, MAX_HISTORY_DISPLAY))
    textbox.configure(state="disabled")

    def clear_history():
        if messagebox.askyesno("Konfirmasi", "Hapus semua riwayat download?"):
            try:
                on_clear()
                textbox.configure(state="normal")
                textbox.delete("0.0", "end")
                textbox.insert("0.0", "Riwayat sudah dihapus.")
                textbox.configure(state="disabled")
            except OSError:
                messagebox.showerror("Error", "Gagal menghapus history.")

    btn_clear = ctk.CTkButton(win, text="Hapus Riwayat", fg_color="#ef4444",
                              hover_color="#dc2626", command=clear_history)
    btn_clear.pack(pady=5)

    return win
