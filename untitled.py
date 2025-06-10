import tkinter as tk
from tkinter import filedialog, messagebox
import json

#Usernames and passwords of users
#format is username : password
USERS = {
    'student1': 'stud1',
    'lecturer1': 'lect1'
}

# User roles
USER_ROLES = {
    'student1': 'Student',
    'lecturer1': 'Lecturer'
}

class QuizApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() 

        self.user_role = None
        self.questions = [] 
        self.current_question = 0
        self.selected_answers = {}

        self.timer_seconds = 60
        #the timer is default set to 60, couldn't figure out how to do it otherwise
        self.timer_running = False

        # Start with the role selection window
        self.role_selection_window()
        self.root.mainloop()

    def role_selection_window(self):
        #Close windows before showing role selection
        if hasattr(self, 'login_win') and self.login_win.winfo_exists():
            self.login_win.destroy()
        if hasattr(self, 'lect_win') and self.lect_win.winfo_exists():
            self.lect_win.destroy()
        if hasattr(self, 'quiz_win') and self.quiz_win.winfo_exists():
            self.quiz_win.destroy()
        if hasattr(self, 'student_menu_win') and self.student_menu_win.winfo_exists():
            self.student_menu_win.destroy()

        self.role_win = tk.Toplevel(self.root)
        self.role_win.title("Quiz System - Select Role")
        self.role_win.geometry("300x180")
        self.role_win.protocol("WM_DELETE_WINDOW", self.root.destroy) 

        tk.Label(self.role_win, text="Please select your role:", font=("Arial", 14)).pack(pady=20)

        tk.Button(self.role_win, text="Login as Lecturer", width=20,
                  command=lambda: self.start_login("Lecturer")).pack(pady=5)
        tk.Button(self.role_win, text="Login as Student", width=20,
                  command=lambda: self.start_login("Student")).pack(pady=5)

        self.role_win.grab_set()
        self.root.wait_window(self.role_win)

    def start_login(self, role_chosen):
        self.chosen_role_for_login = role_chosen
        #to store the selected role
        self.role_win.destroy()
        self.login_window()

    def login_window(self):
        self.login_win = tk.Toplevel(self.root)
        self.login_win.title(f"Quiz System - Login ({self.chosen_role_for_login})")
        self.login_win.geometry("300x220") 
        self.login_win.protocol("WM_DELETE_WINDOW", self.root.destroy)

        tk.Label(self.login_win, text="Username:").pack(pady=(20, 5))
        self.entry_username = tk.Entry(self.login_win)
        self.entry_username.pack()

        tk.Label(self.login_win, text="Password:").pack(pady=(10, 5))
        self.entry_password = tk.Entry(self.login_win, show="*")
        self.entry_password.pack()

        #buttons
        tk.Button(self.login_win, text="Login", width=15, command=self.try_login).pack(pady=20)
        tk.Button(self.login_win, text="Return to Role Selection", width=20,
                  command=lambda: self.return_to_role_selection(self.login_win)).pack(pady=5)

        self.login_win.grab_set()
        self.root.wait_window(self.login_win)

    def try_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Check if the entered credentials match the chosen role
        if username in USERS and USERS[username] == password and USER_ROLES.get(username) == self.chosen_role_for_login:
            messagebox.showinfo("Login", "Successful login", parent=self.login_win)
            self.user_role = self.chosen_role_for_login
            self.login_win.destroy()
            if self.user_role == "Lecturer":
                self.lecturer_dashboard()
            else:
                self.student_menu_dashboard()
        else:
            #error messages
            if username in USERS and USERS[username] == password and USER_ROLES.get(username) != self.chosen_role_for_login:
                messagebox.showerror("Login", f"This login is for a {USER_ROLES.get(username)}. Please select the correct role.", parent=self.login_win)
            else:
                messagebox.showerror("Login", "Invalid login credentials", parent=self.login_win)


    def upload_questions_window(self, parent_window, upload_button_ref=None):
        def upload():
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], parent=upload_win)
            if file_path:
                try:
                    with open(file_path, 'r') as f:
                        loaded_questions = json.load(f)
                    if not isinstance(loaded_questions, list):
                        raise ValueError("JSON must be a list of questions")
                    for q in loaded_questions:
                        if not all(k in q for k in ("question", "options", "answer")):
                            raise ValueError("Each question must have 'question', 'options', 'answer'")
                        if not isinstance(q["options"], list) or len(q["options"]) != 4:
                            raise ValueError("Each question must have 4 options")
                    self.questions = loaded_questions
                    messagebox.showinfo("Success", f"{len(self.questions)} questions loaded.", parent=upload_win)

                    if upload_button_ref:
                        upload_button_ref.pack_forget()

                    upload_win.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load questions:\n{e}", parent=upload_win)
            else:
                messagebox.showwarning("Warning", "No file selected.", parent=upload_win)

        upload_win = tk.Toplevel(parent_window)
        upload_win.title("Upload Questions")
        upload_win.geometry("350x150")
        upload_win.grab_set()
        upload_win.transient(parent_window)
        upload_win.protocol("WM_DELETE_WINDOW", lambda: upload_win.destroy())

        tk.Label(upload_win, text="Upload Questions JSON File", font=("Arial", 14)).pack(pady=20)
        tk.Button(upload_win, text="Upload Questions", width=20, command=upload).pack(pady=10)
        self.root.wait_window(upload_win)

    def lecturer_dashboard(self):
        self.lect_win = tk.Toplevel(self.root)
        self.lect_win.title("Lecturer Dashboard")
        self.lect_win.geometry("600x200")
        self.lect_win.protocol("WM_DELETE_WINDOW", lambda: self.return_to_role_selection(self.lect_win))

        self.upload_btn = tk.Button(self.lect_win, text="Upload Questions",
                                     command=lambda: self.upload_questions_window(
                                         self.lect_win,
                                         upload_button_ref=self.upload_btn
                                     ))
        self.upload_btn.pack(pady=20)

        tk.Button(self.lect_win, text="Return to Role Selection", command=lambda: self.return_to_role_selection(self.lect_win)).pack(pady=10)

        if self.questions:
            messagebox.showinfo("Questions Loaded", f"{len(self.questions)} questions are already loaded. You can return to role selection.", parent=self.lect_win)
            self.upload_btn.pack_forget()

    def student_menu_dashboard(self):
        if hasattr(self, 'quiz_win') and self.quiz_win.winfo_exists():
            self.quiz_win.destroy()

        self.student_menu_win = tk.Toplevel(self.root)
        self.student_menu_win.title("Student Menu")
        self.student_menu_win.geometry("300x180")
        self.student_menu_win.protocol("WM_DELETE_WINDOW", lambda: self.return_to_role_selection(self.student_menu_win))

        tk.Label(self.student_menu_win, text="Welcome, Student!", font=("Arial", 14)).pack(pady=20)

        tk.Button(self.student_menu_win, text="Start Quiz", width=20,
                  command=self.start_quiz_from_menu).pack(pady=5)
        tk.Button(self.student_menu_win, text="Return to Role Selection", width=20,
                  command=lambda: self.return_to_role_selection(self.student_menu_win)).pack(pady=5)

        self.student_menu_win.grab_set()
        self.root.wait_window(self.student_menu_win)

    def start_quiz_from_menu(self):
        """Called when 'Start Quiz' is pressed from the student menu."""
        if not self.questions:
            messagebox.showinfo("No Questions", "No questions have been loaded by the lecturer yet. Please inform your lecturer.", parent=self.student_menu_win)
            # Stay on the student menu if no questions
            return

        self.student_menu_win.destroy() 
        self.student_quiz_window() 

    def student_quiz_window(self): 
        self.quiz_win = tk.Toplevel(self.root)
        self.quiz_win.title("Student Quiz")
        self.quiz_win.geometry("600x500")
        # When quiz window is closed, go back to student menu, not role selection
        self.quiz_win.protocol("WM_DELETE_WINDOW", lambda: self.student_menu_dashboard())

        self.current_question = 0
        self.selected_answers = {}
        self.timer_seconds = 60
        self.timer_running = False

        self.question_var = tk.StringVar()
        self.timer_var = tk.StringVar()
        self.selected_option = tk.StringVar()

        tk.Label(self.quiz_win, textvariable=self.timer_var, font=("Arial", 14), fg="red").pack(pady=5)
        tk.Label(self.quiz_win, textvariable=self.question_var, wraplength=550, font=("Arial", 12), justify="left").pack(pady=10)

        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.quiz_win, text="", variable=self.selected_option,
                                 value=str(i), font=("Arial", 11), anchor="w", justify="left")
            rb.pack(fill="x", padx=20, pady=2)
            self.radio_buttons.append(rb)

        def update_question(index):
            q = self.questions[index]
            self.question_var.set(f"Q{index+1}: {q['question']}")
            for i in range(4):
                self.radio_buttons[i].config(text=q["options"][i])
            selected = self.selected_answers.get(index, "")
            if selected:
                try:
                    selected_index = q["options"].index(selected)
                    self.selected_option.set(str(selected_index))
                except ValueError:
                    self.selected_option.set("")
            else:
                self.selected_option.set("")

        def save_answer():
            sel = self.selected_option.get()
            if sel.isdigit():
                idx = int(sel)
                answer = self.questions[self.current_question]["options"][idx]
                self.selected_answers[self.current_question] = answer

        def next_question():
            save_answer()
            if self.current_question < len(self.questions) - 1:
                self.current_question += 1
                update_question(self.current_question)

        def prev_question():
            save_answer()
            if self.current_question > 0:
                self.current_question -= 1
                update_question(self.current_question)

        def submit_quiz():
            self.timer_running = False
            save_answer()
            correct = 0
            for i, q in enumerate(self.questions):
                if self.selected_answers.get(i, "") == q["answer"]:
                    correct += 1
            total = len(self.questions)
            wrong = total - correct
            percent = (correct / total) * 100 if total > 0 else 0
            messagebox.showinfo("Result", f"Score: {correct}/{total}\nWrong: {wrong}\nPercent: {percent:.2f}%", parent=self.quiz_win)
            self.quiz_win.destroy()
            self.student_menu_dashboard()

        def countdown():
            if self.timer_seconds > 0 and self.timer_running:
                mins, secs = divmod(self.timer_seconds, 60)
                self.timer_var.set(f"Time Left: {mins:02}:{secs:02}")
                self.timer_seconds -= 1
                self.quiz_win.after(1000, countdown)
            elif self.timer_seconds == 0 and self.timer_running:
                messagebox.showinfo("Time Up", "Time is up! Submitting quiz.", parent=self.quiz_win)
                submit_quiz()

        def start_timer():
            self.timer_seconds = 60
            self.timer_running = True
            countdown()

        nav_frame = tk.Frame(self.quiz_win)
        nav_frame.pack(pady=20)

        tk.Button(nav_frame, text="Previous", width=10, command=prev_question).grid(row=0, column=0, padx=10)
        tk.Button(nav_frame, text="Next", width=10, command=next_question).grid(row=0, column=1, padx=10)
        tk.Button(nav_frame, text="Submit", width=10, command=submit_quiz).grid(row=0, column=2, padx=10)

        update_question(self.current_question)
        start_timer()

    def return_to_role_selection(self, current_window):
        """Destroys the current window and re-displays the role selection window."""
        if current_window and current_window.winfo_exists():
            current_window.destroy()
        self.role_selection_window()

#runs the application
if __name__ == "__main__":
    QuizApp()