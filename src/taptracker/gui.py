import sys

import tkinter
import customtkinter

from .params import THEME_FILE, LOGO_FILE
from . import track, report, stop_tracking, handle_exception


def gui():
    sys.excepthook = handle_exception

    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme(THEME_FILE)

    app = customtkinter.CTk()
    app.iconphoto(True, tkinter.PhotoImage(file=LOGO_FILE))
    app.title("Taptracker")
    app.geometry("400x240")

    def btn_track():
        track()
        track_button.configure(text="Stop tracking", command=btn_stop_tracking)

    def btn_stop_tracking():
        stop_tracking()
        track_button.configure(text="Start tracking", command=btn_track)

    def btn_report():
        print("Calculating...")
        # Create new window for results
        results_window = customtkinter.CTkToplevel(app)
        results_window.title("Results")
        results_window.geometry("300x200")

        # Label to store text in
        textbox = customtkinter.CTkLabel(
            results_window, text="Calculating...", wraplength=200
        )
        textbox.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        # Bring windows to front
        results_window.lift()
        results_window.attributes("-topmost", True)
        # results_window.after_idle(results_window.attributes, "-topmost", False)

        # Get and show result from model scoring
        result = report()
        textbox.configure(text=result)

    track_button = customtkinter.CTkButton(
        master=app, text="Start tracking", command=btn_track
    )
    track_button.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)

    report_button = customtkinter.CTkButton(
        master=app, text="Report", command=btn_report
    )
    report_button.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)

    app.mainloop()


if __name__ == "__main__":
    gui()
