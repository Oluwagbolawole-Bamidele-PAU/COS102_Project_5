import tkinter as tk
from tkinter import messagebox

def login():
    username = username_entry.get()
    password = password_entry.get()
    user_type = user_type_var.get()

    # 
    if not username or not password:
        messagebox.showerror("Login Error", "Please enter both username and password.")
        return

    if user_type == "Student":
        if username == "student" and password == "pass":
            messagebox.showinfo("Login Success", "Student login successful!")
        else:
            messagebox.showerror("Login Error", "Invalid student credentials.")
    elif user_type == "Lecturer":
        if username == "lecturer" and password == "admin":
            messagebox.showinfo("Login Success", "Lecturer login successful!")
        else:
            messagebox.showerror("Login Error", "Invalid lecturer credentials.")
    else:
        messagebox.showerror("Login Error", "Please select user type.")


root = tk.Tk()
root.title("Login Feature")
root.geometry("400x300")
root.resizable(False, False) # Prevent resizing

root.configure(bg="#D3D3D3") #
login_frame = tk.Frame(root, bg="#EECCFF", bd=2, relief="solid") # Light purple
login_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)


title_bar = tk.Frame(login_frame, bg="#8A2BE2", height=30) # Darker purple for title bar
title_bar.pack(fill="x")

title_label = tk.Label(title_bar, text="Login feature", bg="#8A2BE2", fg="white", font=("Arial", 12, "bold"))
title_label.pack(pady=5)


welcome_label = tk.Label(login_frame, text="Welcome,please login", bg="#EECCFF", font=("Arial", 12))
welcome_label.pack(pady=(10, 20))

username_label = tk.Label(login_frame, text="Username", bg="#EECCFF", font=("Arial", 10))
username_label.pack(anchor="w", padx=40)
username_entry = tk.Entry(login_frame, width=30, relief="solid", bd=1)
username_entry.pack(pady=5, padx=40, fill="x")


password_label = tk.Label(login_frame, text="Password", bg="#EECCFF", font=("Arial", 10))
password_label.pack(anchor="w", padx=40)
password_entry = tk.Entry(login_frame, width=30, show="*", relief="solid", bd=1)
password_entry.pack(pady=5, padx=40, fill="x")

user_type_var = tk.StringVar(value="") # Initialize with an empty string
student_radio = tk.Radiobutton(login_frame, text="Student", variable=user_type_var, value="Student", bg="#EECCFF", font=("Arial", 10))
student_radio.pack(side="left", padx=(60, 10), pady=10)
lecturer_radio = tk.Radiobutton(login_frame, text="Lecturer", variable=user_type_var, value="Lecturer", bg="#EECCFF", font=("Arial", 10))
lecturer_radio.pack(side="left", padx=(10, 0), pady=10)

login_button = tk.Button(login_frame, text="Login", command=login, bg="#8A2BE2", fg="white", font=("Arial", 10, "bold"))
login_button.pack(pady=10)

root.mainloop()