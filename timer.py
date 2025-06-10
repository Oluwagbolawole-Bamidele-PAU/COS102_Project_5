

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


def set_time_and_questions():
    """
    Function to handle the setting of time and questions.
    This is where you would process the selected values.
    """
    try:
        hours = int(hours_spinbox.get())
        minutes = int(minutes_spinbox.get())


        if hours < 0 or minutes < 0 or minutes >= 60:
            messagebox.showerror("Input Error", "Please enter valid hours and minutes.")
            return

        messagebox.showinfo("Settings Saved", f"Time limit set to: {hours} hours and {minutes} minutes.")

        print(f"Time limit: {hours} hours, {minutes} minutes")



    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for hours and minutes.")



root = tk.Tk()
root.title("Time Selection Feature")
root.geometry("450x350")
root.resizable(False, False)  # Prevent resizing

root.configure(bg="#D3D3D3")  # Light gray


content_frame = tk.Frame(root, bg="#EECCFF", bd=2, relief="solid")  # Light purple
content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.85)


title_bar = tk.Frame(content_frame, bg="#8A2BE2", height=30)  # Darker purple for title bar
title_bar.pack(fill="x")

title_label = tk.Label(title_bar, text="Time selection feature", bg="#8A2BE2", fg="white", font=("Arial", 12, "bold"))
title_label.pack(pady=5)


time_limit_label = tk.Label(content_frame, text="Please set a time limit for the test", bg="#EECCFF",
                            font=("Arial", 12))
time_limit_label.pack(pady=(20, 10))

# Hours and Minutes display
time_display_label = tk.Label(content_frame, text="Hours : Minutes", bg="#EECCFF", font=("Arial", 14, "bold"))
time_display_label.pack(pady=(0, 20))


time_input_frame = tk.Frame(content_frame, bg="#EECCFF")
time_input_frame.pack(pady=5)

hours_spinbox = ttk.Spinbox(time_input_frame, from_=0, to_=23, width=5, justify="center", font=("Arial", 10))
hours_spinbox.set(0)  # Default value
hours_spinbox.pack(side="left", padx=10)

minutes_spinbox = ttk.Spinbox(time_input_frame, from_=0, to_=59, width=5, justify="center", font=("Arial", 10))
minutes_spinbox.set(0)  # Default value
minutes_spinbox.pack(side="left", padx=10)


questions_label = tk.Label(content_frame, text="Please set the number of questions for the test", bg="#EECCFF",font=("Arial", 12))
questions_label.pack(pady=(40, 10))



set_button = tk.Button(content_frame, text="Set Settings", command=set_time_and_questions, bg="#8A2BE2", fg="white",font=("Arial", 10, "bold"))
set_button.pack(pady=20)


root.mainloop()