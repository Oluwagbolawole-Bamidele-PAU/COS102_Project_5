import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import os

USERS = {
    'student1': 'stud1',
    'lecturer1': 'lect1'
}

USER_ROLES = {
    'student1': 'Student',
    'lecturer1': 'Lecturer'
}

BG_COLOR = 'white'
BUTTON_BG_COLOR = '#800080'
BUTTON_HOVER_COLOR = '#A020F0'
BUTTON_TEXT_COLOR = 'white'
BUTTON_BORDER_COLOR = '#800080'
ENTRY_BG_COLOR = 'white'
ENTRY_BORDER_COLOR = '#800080'
ANSWERED_COLOR = '#D4EDDA'
UNANSWERED_COLOR = '#F8D7DA'
CURRENT_QUESTION_COLOR = '#CCE5FF'

QUESTIONS_FILE = "questions.json"
STUDENT_PRACTICE_QUESTIONS_FILE = "student_practice_questions.json"


class QuizApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_attributes('-alpha', 0)
        self.root.withdraw()
        self.root.update_idletasks()

        self.user_role = None
        self.active_quiz_data = {
            "title": "No Quiz Loaded",
            "time_limit_minutes": 1,
            "questions": []
        }
        self.questions = self.active_quiz_data["questions"]

        self.current_question = 0
        self.selected_answers = {}

        self.newly_created_questions = []
        self.current_question_index_creation = 0
        self.create_win = None
        self.quiz_title_entry = None
        self.num_questions_entry = None
        self.quiz_time_limit_entry = None

        self.current_quiz_title_being_created = ""
        self.current_quiz_time_limit_being_created = 0

        self.timer_seconds = 0
        self.timer_running = False

        self._load_questions_on_startup()
        self.role_selection_window()
        self.root.mainloop()

    def _on_button_enter(self, event):
        event.widget.config(bg=BUTTON_HOVER_COLOR)

    def _on_button_leave(self, event):
        event.widget.config(bg=BUTTON_BG_COLOR)

    def _load_questions_on_startup(self):
        if os.path.exists(QUESTIONS_FILE):
            try:
                with open(QUESTIONS_FILE, 'r') as f:
                    loaded_data = json.load(f)

                if isinstance(loaded_data, list):
                    # Handle old format where questions were just a list
                    self.active_quiz_data = {
                        "title": "Loaded Quiz",
                        "time_limit_minutes": 1, # Defaulting time limit for old format
                        "questions": loaded_data
                    }
                elif isinstance(loaded_data, dict) and \
                        all(k in loaded_data for k in ["title", "time_limit_minutes", "questions"]) and \
                        isinstance(loaded_data["questions"], list):
                    self.active_quiz_data = loaded_data
                else:
                    messagebox.showwarning("Load Error", "Questions file format is invalid. Starting with no questions.", parent=self.root)
                    self.active_quiz_data = {"title": "No Quiz Loaded", "time_limit_minutes": 1, "questions": []}

                valid_questions = []
                for q in self.active_quiz_data["questions"]:
                    # Validate each question structure
                    if all(k in q for k in ("question", "options", "answer")) and \
                            isinstance(q["options"], list) and len(q["options"]) == 4:
                        valid_questions.append(q)
                    else:
                        print(f"Skipping invalid question loaded from file: {q}")
                self.active_quiz_data["questions"] = valid_questions

            except json.JSONDecodeError:
                messagebox.showerror("Load Error", "Error decoding questions file (invalid JSON). Starting with no questions).", parent=self.root)
                self.active_quiz_data = {"title": "No Quiz Loaded", "time_limit_minutes": 1, "questions": []}
            except Exception as e:
                messagebox.showerror("Load Error", f"An unexpected error occurred loading questions: {e}. Starting with no questions.", parent=self.root)
                self.active_quiz_data = {"title": "No Quiz Loaded", "time_limit_minutes": 1, "questions": []}
        else:
            print(f"No {QUESTIONS_FILE} found. Starting with no questions.")

        self.questions = self.active_quiz_data["questions"]

    def _save_questions_to_file(self, quiz_data_to_save, filename=QUESTIONS_FILE):
        try:
            with open(filename, 'w') as f:
                json.dump(quiz_data_to_save, f, indent=4)
            print(f"Saved {len(quiz_data_to_save['questions'])} questions to {filename}.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save questions to {filename}:\n{e}", parent=self.root)

    def _load_student_practice_questions_on_startup(self):
        if os.path.exists(STUDENT_PRACTICE_QUESTIONS_FILE):
            try:
                with open(STUDENT_PRACTICE_QUESTIONS_FILE, 'r') as f:
                    loaded_data = json.load(f)
                if isinstance(loaded_data, list):
                    valid_questions = []
                    for q in loaded_data:
                        if all(k in q for k in ("question", "options", "answer")) and \
                                isinstance(q["options"], list) and len(q["options"]) == 4:
                            valid_questions.append(q)
                        else:
                            print(f"Skipping invalid student practice question: {q}")
                    self.student_practice_questions = valid_questions
                else:
                    messagebox.showwarning("Load Error", "Student practice questions file format is invalid. Starting with no practice questions.", parent=self.root)
                    self.student_practice_questions = []
            except json.JSONDecodeError:
                messagebox.showerror("Load Error", "Error decoding student practice questions file (invalid JSON). Starting with no practice questions).", parent=self.root)
                self.student_practice_questions = []
            except Exception as e:
                messagebox.showerror("Load Error", f"An unexpected error occurred loading student practice questions: {e}. Starting with no practice questions.", parent=self.root)
                self.student_practice_questions = []
        else:
            print(f"No {STUDENT_PRACTICE_QUESTIONS_FILE} found. Starting with no student practice questions.")

    def _save_student_practice_questions_to_file(self):
        try:
            with open(STUDENT_PRACTICE_QUESTIONS_FILE, 'w') as f:
                json.dump(self.student_practice_questions, f, indent=4)
            print(f"Saved {len(self.student_practice_questions)} student practice questions to {STUDENT_PRACTICE_QUESTIONS_FILE}.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save student practice questions to {STUDENT_PRACTICE_QUESTIONS_FILE}:\n{e}", parent=self.root)

    def role_selection_window(self):
        # Destroy existing windows if they are open
        if hasattr(self, 'login_win') and self.login_win.winfo_exists():
            self.login_win.destroy()
        if hasattr(self, 'lect_win') and self.lect_win.winfo_exists():
            self.lect_win.destroy()
        if hasattr(self, 'quiz_win') and self.quiz_win.winfo_exists():
            if self.timer_running and self.timer_id:
                self.quiz_win.after_cancel(self.timer_id)
                self.timer_running = False
            self.quiz_win.destroy()
        if hasattr(self, 'student_menu_win') and self.student_menu_win.winfo_exists():
            self.student_menu_win.destroy()
        if hasattr(self, 'create_win') and self.create_win and self.create_win.winfo_exists():
            self.create_win.destroy()
        if hasattr(self, 'create_start_win') and self.create_start_win and self.create_start_win.winfo_exists():
            self.create_start_win.destroy()
        if hasattr(self, 'student_create_win') and self.student_create_win and self.student_create_win.winfo_exists():
            self.student_create_win.destroy()
        if hasattr(self, 'student_create_start_win') and self.student_create_start_win and self.student_create_start_win.winfo_exists():
            self.student_create_start_win.destroy()

        self.role_win = tk.Toplevel(self.root)
        self.role_win.title("Quiz System - Select Role")
        self.role_win.geometry("300x180")
        self.role_win.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.role_win.config(bg=BG_COLOR)

        tk.Label(self.role_win, text="Please select your role:", font=("Arial", 14), bg=BG_COLOR).pack(pady=20)

        lecturer_btn = tk.Button(self.role_win, text="Login as Lecturer", width=20,
                                 command=lambda: self.start_login("Lecturer"),
                                 bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                 bd=2, relief="groove", padx=10, pady=5)
        lecturer_btn.pack(pady=5)
        lecturer_btn.bind("<Enter>", self._on_button_enter)
        lecturer_btn.bind("<Leave>", self._on_button_leave)

        student_btn = tk.Button(self.role_win, text="Login as Student", width=20,
                                command=lambda: self.start_login("Student"),
                                bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                bd=2, relief="groove", padx=10, pady=5)
        student_btn.pack(pady=5)
        student_btn.bind("<Enter>", self._on_button_enter)
        student_btn.bind("<Leave>", self._on_button_leave)

        self.role_win.grab_set()
        self.root.wait_window(self.role_win)

    def start_login(self, role_chosen):
        self.chosen_role_for_login = role_chosen
        self.role_win.destroy()
        self.login_window()

    def login_window(self):
        self.login_win = tk.Toplevel(self.root)
        self.login_win.title(f"Quiz System - Login ({self.chosen_role_for_login})")
        self.login_win.geometry("300x290")
        self.login_win.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.login_win.config(bg=BG_COLOR)

        tk.Label(self.login_win, text="Username:", bg=BG_COLOR).pack(pady=(20, 5))
        self.entry_username = tk.Entry(self.login_win, bg=ENTRY_BG_COLOR,
                                       highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
        self.entry_username.pack()

        tk.Label(self.login_win, text="Password:", bg=BG_COLOR).pack(pady=(10, 5))
        self.entry_password = tk.Entry(self.login_win, show="*", bg=ENTRY_BG_COLOR,
                                       highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
        self.entry_password.pack()

        login_btn = tk.Button(self.login_win, text="Login", width=15, command=self.try_login,
                              bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                              bd=2, relief="groove", padx=10, pady=5)
        login_btn.pack(pady=20)
        login_btn.bind("<Enter>", self._on_button_enter)
        login_btn.bind("<Leave>", self._on_button_leave)

        return_btn = tk.Button(self.login_win, text="Return to Role Selection", width=20,
                               command=lambda: self.return_to_role_selection(self.login_win),
                               bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                               bd=2, relief="groove", padx=10, pady=5)
        return_btn.pack(pady=5)
        return_btn.bind("<Enter>", self._on_button_enter)
        return_btn.bind("<Leave>", self._on_button_leave)

        self.login_win.grab_set()
        self.root.wait_window(self.login_win)

    def try_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if username in USERS and USERS[username] == password and USER_ROLES.get(username) == self.chosen_role_for_login:
            messagebox.showinfo("Login", "Successful login", parent=self.login_win)
            self.user_role = self.chosen_role_for_login
            self.login_win.destroy()
            if self.user_role == "Lecturer":
                self.lecturer_dashboard()
            else:
                self.student_menu_dashboard()
        else:
            if username in USERS and USERS[username] == password and USER_ROLES.get(
                    username) != self.chosen_role_for_login:
                messagebox.showerror("Login", f"This login is for a {USER_ROLES.get(username)}. Please select the correct role.", parent=self.login_win)
            else:
                messagebox.showerror("Login", "Invalid login credentials", parent=self.login_win)

    def lecturer_dashboard(self):
        self.lect_win = tk.Toplevel(self.root)
        self.lect_win.title("Lecturer Dashboard")
        self.lect_win.geometry("600x350")
        self.lect_win.protocol("WM_DELETE_WINDOW", lambda: self.return_to_role_selection(self.lect_win))
        self.lect_win.config(bg=BG_COLOR)

        tk.Label(self.lect_win, text="Lecturer Dashboard", font=("Arial", 16, "bold"), bg=BG_COLOR).pack(pady=20)

        button_frame = tk.Frame(self.lect_win, bg=BG_COLOR)
        button_frame.pack(pady=10)

        self.create_questions_btn = tk.Button(button_frame, text="Create New Questions", width=25,
                                              command=self.create_questions_flow_start,
                                              bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                              bd=2, relief="groove", padx=10, pady=5)
        self.create_questions_btn.grid(row=0, column=0, padx=10, pady=5)
        self.create_questions_btn.bind("<Enter>", self._on_button_enter)
        self.create_questions_btn.bind("<Leave>", self._on_button_leave)

        self.view_questions_btn = tk.Button(button_frame, text="View Current Quiz Questions", width=25,
                                            command=self.view_questions_window,
                                            bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                            bd=2, relief="groove", padx=10, pady=5)
        self.view_questions_btn.grid(row=0, column=1, padx=10, pady=5)
        self.view_questions_btn.bind("<Enter>", self._on_button_enter)
        self.view_questions_btn.bind("<Leave>", self._on_button_leave)

        self.delete_questions_btn = tk.Button(button_frame, text="Delete All Questions in Current Quiz", width=25,
                                              command=self.delete_all_questions,
                                              bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                              bd=2, relief="groove", padx=10, pady=5)
        self.delete_questions_btn.grid(row=1, column=0, padx=10, pady=5)
        self.delete_questions_btn.bind("<Enter>", self._on_button_enter)
        self.delete_questions_btn.bind("<Leave>", self._on_button_leave)

        self.load_from_file_btn = tk.Button(button_frame, text="Load Quiz from File (JSON)", width=25,
                                            command=self.load_questions_from_file,
                                            bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                            bd=2, relief="groove", padx=10, pady=5)
        self.load_from_file_btn.grid(row=1, column=1, padx=10, pady=5)
        self.load_from_file_btn.bind("<Enter>", self._on_button_enter)
        self.load_from_file_btn.bind("<Leave>", self._on_button_leave)

        return_btn = tk.Button(self.lect_win, text="Return to Role Selection", width=25,
                               command=lambda: self.return_to_role_selection(self.lect_win),
                               bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                               bd=2, relief="groove", padx=10, pady=5)
        return_btn.pack(pady=15)
        return_btn.bind("<Enter>", self._on_button_enter)
        return_btn.bind("<Leave>", self._on_button_leave)

        self.update_lecturer_dashboard_buttons()

    def update_lecturer_dashboard_buttons(self):
        """Enables/disables buttons based on whether questions are loaded."""
        if self.questions:
            self.view_questions_btn.config(state=tk.NORMAL)
            self.delete_questions_btn.config(state=tk.NORMAL)
        else:
            self.view_questions_btn.config(state=tk.DISABLED)
            self.delete_questions_btn.config(state=tk.DISABLED)

    def load_questions_from_file(self):
        """Allows lecturer to load quiz data from a JSON file, replacing current quiz."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], parent=self.lect_win)
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    loaded_data = json.load(f)

                new_active_quiz_data = None

                if isinstance(loaded_data, list):
                    # Handle old format where questions were just a list
                    new_active_quiz_data = {
                        "title": os.path.basename(file_path).replace(".json", ""),
                        "time_limit_minutes": 1, # Defaulting time limit for old format
                        "questions": loaded_data
                    }
                    messagebox.showinfo("Load Info",
                                        f"Loaded {len(loaded_data)} questions from old format '{os.path.basename(file_path)}'. Defaulting time limit to 1 minute.",
                                        parent=self.lect_win)
                elif isinstance(loaded_data, dict) and \
                        all(k in loaded_data for k in ["title", "time_limit_minutes", "questions"]) and \
                        isinstance(loaded_data["questions"], list):
                    new_active_quiz_data = loaded_data
                    messagebox.showinfo("Load Info",
                                        f"Loaded '{new_active_quiz_data['title']}' with {len(new_active_quiz_data['questions'])} questions (Time Limit: {new_active_quiz_data['time_limit_minutes']} mins) from '{os.path.basename(file_path)}'.",
                                        parent=self.lect_win)
                else:
                    messagebox.showwarning("Load Error", "The selected file format is invalid. No quiz loaded.",
                                           parent=self.lect_win)
                    return

                valid_new_questions = []
                for q in new_active_quiz_data["questions"]:
                    # Validate each question structure
                    if all(k in q for k in ("question", "options", "answer")) and \
                            isinstance(q["options"], list) and len(q["options"]) == 4:
                        valid_new_questions.append(q)
                    else:
                        print(f"Skipping invalid question from loaded file: {q}")

                if valid_new_questions:
                    new_active_quiz_data["questions"] = valid_new_questions
                    self.active_quiz_data = new_active_quiz_data
                    self.questions = self.active_quiz_data["questions"]
                    self._save_questions_to_file(self.active_quiz_data)
                else:
                    messagebox.showwarning("No Valid Questions", "The selected file contains no valid questions or is empty. No quiz loaded.", parent=self.lect_win)
                    return

                self.update_lecturer_dashboard_buttons()
            except json.JSONDecodeError:
                messagebox.showerror("Load Error", "Error decoding selected file (invalid JSON).", parent=self.lect_win)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load questions from file:\n{e}", parent=self.lect_win)
        else:
            messagebox.showwarning("Warning", "No file selected.", parent=self.lect_win)

    def create_questions_flow_start(self):
        self.newly_created_questions = []
        self.current_question_index_creation = 0
        self.current_quiz_title_being_created = ""
        self.current_quiz_time_limit_being_created = 0

        self.create_start_win = tk.Toplevel(self.lect_win)
        self.create_start_win.title("Create New Quiz")
        self.create_start_win.geometry("400x300")
        self.create_start_win.transient(self.lect_win)
        self.create_start_win.grab_set()
        self.create_start_win.config(bg=BG_COLOR)
        self.create_start_win.protocol("WM_DELETE_WINDOW", self.create_start_win.destroy)

        tk.Label(self.create_start_win, text="Enter Quiz Title (e.g., 'Math Quiz'):", font=("Arial", 12),
                 bg=BG_COLOR).pack(pady=(10, 5))
        self.quiz_title_entry = tk.Entry(self.create_start_win, width=30, bg=ENTRY_BG_COLOR,
                                         highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
        self.quiz_title_entry.pack(pady=5)

        tk.Label(self.create_start_win, text="Enter the number of questions to create:", font=("Arial", 12),
                 bg=BG_COLOR).pack(pady=(10, 5))
        self.num_questions_entry = tk.Entry(self.create_start_win, width=10, bg=ENTRY_BG_COLOR,
                                            highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
        self.num_questions_entry.pack(pady=5)
        self.num_questions_entry.insert(0, "1")

        tk.Label(self.create_start_win, text="Quiz Time Limit (minutes):", font=("Arial", 12), bg=BG_COLOR).pack(
            pady=(10, 5))
        self.quiz_time_limit_entry = tk.Entry(self.create_start_win, width=10, bg=ENTRY_BG_COLOR,
                                              highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
        self.quiz_time_limit_entry.pack(pady=5)
        self.quiz_time_limit_entry.insert(0, "1")

        start_creating_btn = tk.Button(self.create_start_win, text="Start Creating",
                                       command=self._start_question_form_from_initial,
                                       bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                       bd=2, relief="groove", padx=10, pady=5)
        start_creating_btn.pack(pady=15)
        start_creating_btn.bind("<Enter>", self._on_button_enter)
        start_creating_btn.bind("<Leave>", self._on_button_leave)

        self.root.wait_window(self.create_start_win)

    def _start_question_form_from_initial(self):
        """Validates input and starts the question form."""
        quiz_title = self.quiz_title_entry.get().strip()
        if not quiz_title:
            messagebox.showwarning("Missing Input", "Please enter a Quiz Title.", parent=self.create_start_win)
            return

        try:
            num_q = int(self.num_questions_entry.get())
            if num_q <= 0:
                messagebox.showerror("Invalid Input", "Please enter a positive number of questions.",
                                     parent=self.create_start_win)
                return

            time_limit_str = self.quiz_time_limit_entry.get().strip()
            time_limit_minutes = int(time_limit_str)
            if time_limit_minutes <= 0:
                messagebox.showerror("Invalid Input", "Please enter a positive time limit in minutes.",
                                     parent=self.create_start_win)
                return

            self.num_questions_to_create = num_q
            self.current_quiz_title_being_created = quiz_title
            self.current_quiz_time_limit_being_created = time_limit_minutes
            self.create_start_win.destroy()

            # Initialize newly_created_questions with empty templates
            self.newly_created_questions = [
                {"question": "", "options": ["", "", "", ""], "answer": ""}
                for _ in range(self.num_questions_to_create)
            ]
            self.current_question_index_creation = 0
            self.display_question_creation_form()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for questions and time limit.",
                                 parent=self.create_start_win)

    def display_question_creation_form(self):
        if self.create_win and self.create_win.winfo_exists():
            self.create_win.destroy()

        display_title = self.current_quiz_title_being_created if self.current_quiz_title_being_created else "New Quiz"
        self.create_win = tk.Toplevel(self.lect_win)
        self.create_win.title(
            f"{display_title} - Question {self.current_question_index_creation + 1}/{self.num_questions_to_create}")
        self.create_win.geometry("700x550")
        self.create_win.transient(self.lect_win)
        self.create_win.grab_set()
        self.create_win.config(bg=BG_COLOR)
        self.create_win.protocol("WM_DELETE_WINDOW", self._cancel_question_creation)

        tk.Label(self.create_win, text=f"Question {self.current_question_index_creation + 1}:",
                 font=("Arial", 12, "bold"), bg=BG_COLOR).pack(pady=(10, 5))
        self.q_entry = scrolledtext.ScrolledText(self.create_win, wrap=tk.WORD, width=70, height=4, font=("Arial", 10),
                                                 bg=ENTRY_BG_COLOR, highlightbackground=ENTRY_BORDER_COLOR,
                                                 highlightthickness=2, bd=0)
        self.q_entry.pack(pady=5)

        self.option_entries = []
        self.correct_option_var = tk.StringVar()
        option_labels = ["A", "B", "C", "D"]

        tk.Label(self.create_win, text="Options:", font=("Arial", 12, "bold"), bg=BG_COLOR).pack(pady=(10, 5))
        for i, label_text in enumerate(option_labels):
            opt_frame = tk.Frame(self.create_win, bg=BG_COLOR)
            opt_frame.pack(fill="x", padx=20, pady=2)
            tk.Label(opt_frame, text=f"{label_text}.", bg=BG_COLOR).pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(opt_frame, width=60, bg=ENTRY_BG_COLOR,
                             highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
            entry.pack(side=tk.LEFT, expand=True, fill="x")
            self.option_entries.append(entry)

            rb = tk.Radiobutton(opt_frame, text="Correct", variable=self.correct_option_var, value=label_text,
                                bg=BG_COLOR, activebackground=BG_COLOR, selectcolor=BG_COLOR)
            rb.pack(side=tk.RIGHT, padx=5)

        nav_frame = tk.Frame(self.create_win, bg=BG_COLOR)
        nav_frame.pack(pady=20)

        prev_btn = tk.Button(nav_frame, text="Previous", width=10,
                             command=self._save_and_navigate_question_creation_form_prev,
                             bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                             bd=2, relief="groove", padx=10, pady=5)
        prev_btn.grid(row=0, column=0, padx=10)
        prev_btn.bind("<Enter>", self._on_button_enter)
        prev_btn.bind("<Leave>", self._on_button_leave)

        next_btn = tk.Button(nav_frame, text="Next", width=10,
                             command=self._save_and_navigate_question_creation_form_next,
                             bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                             bd=2, relief="groove", padx=10, pady=5)
        next_btn.grid(row=0, column=1, padx=10)
        next_btn.bind("<Enter>", self._on_button_enter)
        next_btn.bind("<Leave>", self._on_button_leave)

        finalize_btn = tk.Button(self.create_win, text="Finalize & Save Quiz", width=20,
                                 command=self._finalize_created_questions,
                                 bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                 bd=2, relief="groove", padx=10, pady=5)
        finalize_btn.pack(pady=10)
        finalize_btn.bind("<Enter>", self._on_button_enter)
        finalize_btn.bind("<Leave>", self._on_button_leave)

        self._load_question_for_creation_editing()

    def _save_current_question_input(self):
        q_text = self.q_entry.get("1.0", tk.END).strip()
        options = [entry.get().strip() for entry in self.option_entries]
        correct_opt_label = self.correct_option_var.get()

        if not q_text:
            messagebox.showwarning("Missing Input", "Question text cannot be empty.", parent=self.create_win)
            return False
        if any(not opt for opt in options):
            messagebox.showwarning("Missing Input", "All options must be filled.", parent=self.create_win)
            return False
        if not correct_opt_label:
            messagebox.showwarning("Missing Input", "Please select the correct answer.", parent=self.create_win)
            return False

        correct_answer_text = ""
        try:
            correct_index = ord(correct_opt_label.upper()) - ord('A')
            if 0 <= correct_index < len(options):
                correct_answer_text = options[correct_index]
            else:
                raise ValueError("Invalid correct option selected.")
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Could not determine correct answer from selected option.", parent=self.create_win)
            return False

        self.newly_created_questions[self.current_question_index_creation] = {
            "question": q_text,
            "options": options,
            "answer": correct_answer_text
        }
        return True

    def _load_question_for_creation_editing(self):
        if self.current_question_index_creation < len(self.newly_created_questions):
            q_data = self.newly_created_questions[self.current_question_index_creation]
            self.q_entry.config(state=tk.NORMAL)
            self.q_entry.delete("1.0", tk.END)
            self.q_entry.insert("1.0", q_data["question"])
            for i, entry in enumerate(self.option_entries):
                entry.delete(0, tk.END)
                if i < len(q_data["options"]):
                    entry.insert(0, q_data["options"][i])
            if q_data["answer"]:
                try:
                    answer_index = q_data["options"].index(q_data["answer"])
                    self.correct_option_var.set(chr(ord('A') + answer_index))
                except ValueError:
                    self.correct_option_var.set("")
            else:
                self.correct_option_var.set("")

            self.q_entry.config(state=tk.NORMAL)
            for entry in self.option_entries:
                entry.config(state=tk.NORMAL)

    def _save_and_navigate_question_creation_form_next(self):
        if self._save_current_question_input():
            if self.current_question_index_creation < self.num_questions_to_create - 1:
                self.current_question_index_creation += 1
                self.display_question_creation_form()
            else:
                messagebox.showinfo("End of Questions", "You have reached the last question. Click 'Finalize & Save Quiz' to save your quiz.", parent=self.create_win)

    def _save_and_navigate_question_creation_form_prev(self):
        if self._save_current_question_input():
            if self.current_question_index_creation > 0:
                self.current_question_index_creation -= 1
                self.display_question_creation_form()
            else:
                messagebox.showinfo("First Question", "You are already at the first question.", parent=self.create_win)

    def _finalize_created_questions(self):
        """Validates and saves all newly created questions to a user-defined file and makes it the active quiz."""
        if not self._save_current_question_input():
            return
        if not self.newly_created_questions:
            messagebox.showwarning("No Questions", "No questions have been created to finalize.", parent=self.create_win)
            return
        for i, q_data in enumerate(self.newly_created_questions):
            if not q_data["question"] or any(not opt for opt in q_data["options"]) or not q_data["answer"]:
                messagebox.showerror("Validation Error", f"Question {i + 1} is incomplete. Please fill in all fields for all questions.", parent=self.create_win)
                return

        quiz_data_to_save = {
            "title": self.current_quiz_title_being_created,
            "time_limit_minutes": self.current_quiz_time_limit_being_created,
            "questions": self.newly_created_questions
        }

        self.active_quiz_data = quiz_data_to_save
        self.questions = self.active_quiz_data["questions"]
        self._save_questions_to_file(self.active_quiz_data)

        messagebox.showinfo("Quiz Created", f"Quiz '{self.active_quiz_data['title']}' with {len(self.questions)} questions and {self.active_quiz_data['time_limit_minutes']} minutes time limit has been created and saved as the current quiz.", parent=self.create_win)
        self.create_win.destroy()
        self.update_lecturer_dashboard_buttons()

    def _cancel_question_creation(self):
        if messagebox.askyesno("Cancel Creation", "Are you sure you want to cancel quiz creation? All unsaved questions will be lost.", parent=self.create_win):
            self.create_win.destroy()

    def view_questions_window(self):
        view_win = tk.Toplevel(self.lect_win)
        view_win.title("Current Quiz Questions")
        view_win.geometry("800x600")
        view_win.transient(self.lect_win)
        view_win.grab_set()
        view_win.config(bg=BG_COLOR)
        view_win.protocol("WM_DELETE_WINDOW", view_win.destroy)

        tk.Label(view_win, text=f"Quiz Title: {self.active_quiz_data['title']}", font=("Arial", 14, "bold"), bg=BG_COLOR).pack(pady=10)
        tk.Label(view_win, text=f"Time Limit: {self.active_quiz_data['time_limit_minutes']} minutes", font=("Arial", 12), bg=BG_COLOR).pack(pady=5)

        if not self.questions:
            tk.Label(view_win, text="No questions loaded.", bg=BG_COLOR).pack(pady=20)
            return

        canvas = tk.Canvas(view_win, bg=BG_COLOR)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(view_win, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frame = tk.Frame(canvas, bg=BG_COLOR)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        for i, q in enumerate(self.questions):
            q_frame = tk.LabelFrame(frame, text=f"Question {i + 1}", padx=10, pady=10, bg=BG_COLOR, bd=2, relief="groove")
            q_frame.pack(fill="x", padx=10, pady=5)

            tk.Label(q_frame, text=q["question"], wraplength=700, justify="left", font=("Arial", 10, "bold"), bg=BG_COLOR).pack(anchor="w", pady=5)

            options_text = "\n".join([f"{chr(65+j)}. {opt}" for j, opt in enumerate(q["options"])])
            tk.Label(q_frame, text=options_text, wraplength=700, justify="left", bg=BG_COLOR).pack(anchor="w", pady=2)

            tk.Label(q_frame, text=f"Correct Answer: {q['answer']}", font=("Arial", 9, "italic"), bg=BG_COLOR, fg="#008000").pack(anchor="w", pady=2)

    def delete_all_questions(self):
        """Deletes all questions from the current quiz."""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete ALL questions from the current quiz? This action cannot be undone.", parent=self.lect_win):
            self.active_quiz_data = {
                "title": "No Quiz Loaded",
                "time_limit_minutes": 1,
                "questions": []
            }
            self.questions = self.active_quiz_data["questions"]
            self._save_questions_to_file(self.active_quiz_data)
            messagebox.showinfo("Deleted", "All questions have been deleted from the current quiz.", parent=self.lect_win)
            self.update_lecturer_dashboard_buttons()

    def student_menu_dashboard(self):
        self._load_student_practice_questions_on_startup() # Load student practice questions
        self.student_menu_win = tk.Toplevel(self.root)
        self.student_menu_win.title("Student Dashboard")
        self.student_menu_win.geometry("400x350")
        self.student_menu_win.protocol("WM_DELETE_WINDOW", lambda: self.return_to_role_selection(self.student_menu_win))
        self.student_menu_win.config(bg=BG_COLOR)

        tk.Label(self.student_menu_win, text="Student Dashboard", font=("Arial", 16, "bold"), bg=BG_COLOR).pack(pady=20)

        start_quiz_btn = tk.Button(self.student_menu_win, text="Start Main Quiz", width=25,
                                   command=self.start_quiz,
                                   bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                   bd=2, relief="groove", padx=10, pady=5)
        start_quiz_btn.pack(pady=5)
        start_quiz_btn.bind("<Enter>", self._on_button_enter)
        start_quiz_btn.bind("<Leave>", self._on_button_leave)

        create_practice_q_btn = tk.Button(self.student_menu_win, text="Create Practice Questions", width=25,
                                           command=self.create_student_practice_questions_flow_start,
                                           bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                           bd=2, relief="groove", padx=10, pady=5)
        create_practice_q_btn.pack(pady=5)
        create_practice_q_btn.bind("<Enter>", self._on_button_enter)
        create_practice_q_btn.bind("<Leave>", self._on_button_leave)

        practice_quiz_btn = tk.Button(self.student_menu_win, text="Start Practice Quiz", width=25,
                                       command=self.start_practice_quiz,
                                       bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                       bd=2, relief="groove", padx=10, pady=5)
        practice_quiz_btn.pack(pady=5)
        practice_quiz_btn.bind("<Enter>", self._on_button_enter)
        practice_quiz_btn.bind("<Leave>", self._on_button_leave)

        return_btn = tk.Button(self.student_menu_win, text="Return to Role Selection", width=25,
                               command=lambda: self.return_to_role_selection(self.student_menu_win),
                               bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                               bd=2, relief="groove", padx=10, pady=5)
        return_btn.pack(pady=15)
        return_btn.bind("<Enter>", self._on_button_enter)
        return_btn.bind("<Leave>", self._on_button_leave)

        self.update_student_dashboard_buttons()

    def update_student_dashboard_buttons(self):
        """Enables/disables buttons based on whether quizzes are available."""
        main_quiz_available = bool(self.questions)
        practice_quiz_available = bool(hasattr(self, 'student_practice_questions') and self.student_practice_questions)

        # Assuming start_quiz_btn is the main quiz button, and practice_quiz_btn is for practice
        for widget in self.student_menu_win.winfo_children():
            if isinstance(widget, tk.Button):
                if "Start Main Quiz" in widget.cget("text"):
                    widget.config(state=tk.NORMAL if main_quiz_available else tk.DISABLED)
                elif "Start Practice Quiz" in widget.cget("text"):
                    widget.config(state=tk.NORMAL if practice_quiz_available else tk.DISABLED)

    def create_student_practice_questions_flow_start(self):
        self.newly_created_questions = []
        self.current_question_index_creation = 0
        self.current_quiz_title_being_created = "Student Practice Quiz" # Fixed title
        self.current_quiz_time_limit_being_created = 0 # Not applicable for practice questions

        self.student_create_start_win = tk.Toplevel(self.student_menu_win)
        self.student_create_start_win.title("Create Practice Questions")
        self.student_create_start_win.geometry("400x200")
        self.student_create_start_win.transient(self.student_menu_win)
        self.student_create_start_win.grab_set()
        self.student_create_start_win.config(bg=BG_COLOR)
        self.student_create_start_win.protocol("WM_DELETE_WINDOW", self.student_create_start_win.destroy)

        tk.Label(self.student_create_start_win, text="Enter the number of practice questions to create:", font=("Arial", 12),
                 bg=BG_COLOR).pack(pady=(20, 5))
        self.num_practice_questions_entry = tk.Entry(self.student_create_start_win, width=10, bg=ENTRY_BG_COLOR,
                                            highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
        self.num_practice_questions_entry.pack(pady=5)
        self.num_practice_questions_entry.insert(0, "1")

        start_creating_btn = tk.Button(self.student_create_start_win, text="Start Creating",
                                       command=self._start_student_question_form_from_initial,
                                       bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                       bd=2, relief="groove", padx=10, pady=5)
        start_creating_btn.pack(pady=15)
        start_creating_btn.bind("<Enter>", self._on_button_enter)
        start_creating_btn.bind("<Leave>", self._on_button_leave)

        self.root.wait_window(self.student_create_start_win)

    def _start_student_question_form_from_initial(self):
        try:
            num_q = int(self.num_practice_questions_entry.get())
            if num_q <= 0:
                messagebox.showerror("Invalid Input", "Please enter a positive number of questions.",
                                     parent=self.student_create_start_win)
                return

            self.num_questions_to_create = num_q
            self.student_create_start_win.destroy()

            self.newly_created_questions = [
                {"question": "", "options": ["", "", "", ""], "answer": ""}
                for _ in range(self.num_questions_to_create)
            ]
            self.current_question_index_creation = 0
            self.display_student_practice_question_creation_form()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for questions.",
                                 parent=self.student_create_start_win)

    def display_student_practice_question_creation_form(self):
        if self.student_create_win and self.student_create_win.winfo_exists():
            self.student_create_win.destroy()

        self.student_create_win = tk.Toplevel(self.student_menu_win)
        self.student_create_win.title(
            f"Practice Questions - Question {self.current_question_index_creation + 1}/{self.num_questions_to_create}")
        self.student_create_win.geometry("700x550")
        self.student_create_win.transient(self.student_menu_win)
        self.student_create_win.grab_set()
        self.student_create_win.config(bg=BG_COLOR)
        self.student_create_win.protocol("WM_DELETE_WINDOW", self._cancel_student_practice_question_creation)

        tk.Label(self.student_create_win, text=f"Question {self.current_question_index_creation + 1}:",
                 font=("Arial", 12, "bold"), bg=BG_COLOR).pack(pady=(10, 5))
        self.q_entry_student = scrolledtext.ScrolledText(self.student_create_win, wrap=tk.WORD, width=70, height=4, font=("Arial", 10),
                                                 bg=ENTRY_BG_COLOR, highlightbackground=ENTRY_BORDER_COLOR,
                                                 highlightthickness=2, bd=0)
        self.q_entry_student.pack(pady=5)

        self.option_entries_student = []
        self.correct_option_var_student = tk.StringVar()
        option_labels = ["A", "B", "C", "D"]

        tk.Label(self.student_create_win, text="Options:", font=("Arial", 12, "bold"), bg=BG_COLOR).pack(pady=(10, 5))
        for i, label_text in enumerate(option_labels):
            opt_frame = tk.Frame(self.student_create_win, bg=BG_COLOR)
            opt_frame.pack(fill="x", padx=20, pady=2)
            tk.Label(opt_frame, text=f"{label_text}.", bg=BG_COLOR).pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(opt_frame, width=60, bg=ENTRY_BG_COLOR,
                             highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
            entry.pack(side=tk.LEFT, expand=True, fill="x")
            self.option_entries_student.append(entry)

            rb = tk.Radiobutton(opt_frame, text="Correct", variable=self.correct_option_var_student, value=label_text,
                                bg=BG_COLOR, activebackground=BG_COLOR, selectcolor=BG_COLOR)
            rb.pack(side=tk.RIGHT, padx=5)

        nav_frame = tk.Frame(self.student_create_win, bg=BG_COLOR)
        nav_frame.pack(pady=20)

        prev_btn = tk.Button(nav_frame, text="Previous", width=10,
                             command=self._save_and_navigate_student_practice_question_creation_form_prev,
                             bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                             bd=2, relief="groove", padx=10, pady=5)
        prev_btn.grid(row=0, column=0, padx=10)
        prev_btn.bind("<Enter>", self._on_button_enter)
        prev_btn.bind("<Leave>", self._on_button_leave)

        next_btn = tk.Button(nav_frame, text="Next", width=10,
                             command=self._save_and_navigate_student_practice_question_creation_form_next,
                             bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                             bd=2, relief="groove", padx=10, pady=5)
        next_btn.grid(row=0, column=1, padx=10)
        next_btn.bind("<Enter>", self._on_button_enter)
        next_btn.bind("<Leave>", self._on_button_leave)

        finalize_btn = tk.Button(self.student_create_win, text="Finalize & Save Practice Questions", width=30,
                                 command=self._finalize_created_student_practice_questions,
                                 bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                 bd=2, relief="groove", padx=10, pady=5)
        finalize_btn.pack(pady=10)
        finalize_btn.bind("<Enter>", self._on_button_enter)
        finalize_btn.bind("<Leave>", self._on_button_leave)

        self._load_student_practice_question_for_creation_editing()

    def _save_current_student_practice_question_input(self):
        q_text = self.q_entry_student.get("1.0", tk.END).strip()
        options = [entry.get().strip() for entry in self.option_entries_student]
        correct_opt_label = self.correct_option_var_student.get()

        if not q_text:
            messagebox.showwarning("Missing Input", "Question text cannot be empty.", parent=self.student_create_win)
            return False
        if any(not opt for opt in options):
            messagebox.showwarning("Missing Input", "All options must be filled.", parent=self.student_create_win)
            return False
        if not correct_opt_label:
            messagebox.showwarning("Missing Input", "Please select the correct answer.", parent=self.student_create_win)
            return False

        correct_answer_text = ""
        try:
            correct_index = ord(correct_opt_label.upper()) - ord('A')
            if 0 <= correct_index < len(options):
                correct_answer_text = options[correct_index]
            else:
                raise ValueError("Invalid correct option selected.")
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Could not determine correct answer from selected option.", parent=self.student_create_win)
            return False

        self.newly_created_questions[self.current_question_index_creation] = {
            "question": q_text,
            "options": options,
            "answer": correct_answer_text
        }
        return True

    def _load_student_practice_question_for_creation_editing(self):
        if self.current_question_index_creation < len(self.newly_created_questions):
            q_data = self.newly_created_questions[self.current_question_index_creation]
            self.q_entry_student.config(state=tk.NORMAL)
            self.q_entry_student.delete("1.0", tk.END)
            self.q_entry_student.insert("1.0", q_data["question"])
            for i, entry in enumerate(self.option_entries_student):
                entry.delete(0, tk.END)
                if i < len(q_data["options"]):
                    entry.insert(0, q_data["options"][i])
            if q_data["answer"]:
                try:
                    answer_index = q_data["options"].index(q_data["answer"])
                    self.correct_option_var_student.set(chr(ord('A') + answer_index))
                except ValueError:
                    self.correct_option_var_student.set("")
            else:
                self.correct_option_var_student.set("")

            self.q_entry_student.config(state=tk.NORMAL)
            for entry in self.option_entries_student:
                entry.config(state=tk.NORMAL)

    def _save_and_navigate_student_practice_question_creation_form_next(self):
        if self._save_current_student_practice_question_input():
            if self.current_question_index_creation < self.num_questions_to_create - 1:
                self.current_question_index_creation += 1
                self.display_student_practice_question_creation_form()
            else:
                messagebox.showinfo("End of Questions", "You have reached the last question. Click 'Finalize & Save Practice Questions' to save.", parent=self.student_create_win)

    def _save_and_navigate_student_practice_question_creation_form_prev(self):
        if self._save_current_student_practice_question_input():
            if self.current_question_index_creation > 0:
                self.current_question_index_creation -= 1
                self.display_student_practice_question_creation_form()
            else:
                messagebox.showinfo("First Question", "You are already at the first question.", parent=self.student_create_win)

    def _finalize_created_student_practice_questions(self):
        if not self._save_current_student_practice_question_input():
            return
        if not self.newly_created_questions:
            messagebox.showwarning("No Questions", "No questions have been created to finalize.", parent=self.student_create_win)
            return
        for i, q_data in enumerate(self.newly_created_questions):
            if not q_data["question"] or any(not opt for opt in q_data["options"]) or not q_data["answer"]:
                messagebox.showerror("Validation Error", f"Question {i + 1} is incomplete. Please fill in all fields for all questions.", parent=self.student_create_win)
                return

        self.student_practice_questions = self.newly_created_questions
        self._save_student_practice_questions_to_file()

        messagebox.showinfo("Practice Questions Created", f"Practice questions ({len(self.student_practice_questions)} questions) have been created and saved.", parent=self.student_create_win)
        self.student_create_win.destroy()
        self.update_student_dashboard_buttons()

    def _cancel_student_practice_question_creation(self):
        if messagebox.askyesno("Cancel Creation", "Are you sure you want to cancel practice question creation? All unsaved questions will be lost.", parent=self.student_create_win):
            self.student_create_win.destroy()

    def start_quiz(self):
        """Starts the main quiz for the student."""
        if not self.questions:
            messagebox.showwarning("No Quiz Available", "No quiz has been loaded by the lecturer yet.", parent=self.student_menu_win)
            return

        self.student_menu_win.destroy()
        self.quiz_win = tk.Toplevel(self.root)
        self.quiz_win.title(f"Quiz - {self.active_quiz_data['title']}")
        self.quiz_win.geometry("800x600")
        self.quiz_win.protocol("WM_DELETE_WINDOW", lambda: self.confirm_exit_quiz(self.quiz_win))
        self.quiz_win.config(bg=BG_COLOR)

        self.current_quiz_questions = self.questions
        self.current_quiz_title = self.active_quiz_data['title']
        self.current_quiz_time_limit_seconds = self.active_quiz_data['time_limit_minutes'] * 60

        self.current_question = 0
        self.selected_answers = {i: "" for i in range(len(self.current_quiz_questions))}

        self.quiz_title_label = tk.Label(self.quiz_win, text=self.current_quiz_title, font=("Arial", 16, "bold"), bg=BG_COLOR)
        self.quiz_title_label.pack(pady=10)

        self.timer_label = tk.Label(self.quiz_win, text=f"Time Left: {self.active_quiz_data['time_limit_minutes']}:00", font=("Arial", 12), bg=BG_COLOR)
        self.timer_label.pack(pady=5)

        self.question_number_label = tk.Label(self.quiz_win, text="", font=("Arial", 12), bg=BG_COLOR)
        self.question_number_label.pack(pady=5)

        self.question_text_area = scrolledtext.ScrolledText(self.quiz_win, wrap=tk.WORD, width=80, height=8, font=("Arial", 11),
                                                          bg=ENTRY_BG_COLOR, highlightbackground=ENTRY_BORDER_COLOR,
                                                          highlightthickness=2, bd=0)
        self.question_text_area.pack(pady=10, padx=20)
        self.question_text_area.config(state=tk.DISABLED)

        self.option_radio_buttons = []
        self.answer_var = tk.StringVar()
        for i in range(4):
            rb = tk.Radiobutton(self.quiz_win, text="", variable=self.answer_var, value="",
                                command=self.save_selected_answer,
                                font=("Arial", 10), bg=BG_COLOR, activebackground=BG_COLOR, selectcolor=BG_COLOR)
            rb.pack(anchor="w", padx=30, pady=2)
            self.option_radio_buttons.append(rb)

        navigation_frame = tk.Frame(self.quiz_win, bg=BG_COLOR)
        navigation_frame.pack(pady=20)

        self.prev_button = tk.Button(navigation_frame, text="Previous", command=self.prev_question, state=tk.DISABLED,
                                     bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, bd=2, relief="groove", padx=10, pady=5)
        self.prev_button.grid(row=0, column=0, padx=10)
        self.prev_button.bind("<Enter>", self._on_button_enter)
        self.prev_button.bind("<Leave>", self._on_button_leave)

        self.next_button = tk.Button(navigation_frame, text="Next", command=self.next_question,
                                     bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, bd=2, relief="groove", padx=10, pady=5)
        self.next_button.grid(row=0, column=1, padx=10)
        self.next_button.bind("<Enter>", self._on_button_enter)
        self.next_button.bind("<Leave>", self._on_button_leave)

        self.submit_button = tk.Button(self.quiz_win, text="Submit Quiz", command=self.submit_quiz,
                                       bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, bd=2, relief="groove", padx=10, pady=5)
        self.submit_button.pack(pady=10)
        self.submit_button.bind("<Enter>", self._on_button_enter)
        self.submit_button.bind("<Leave>", self._on_button_leave)

        self.question_overview_frame = tk.Frame(self.quiz_win, bg=BG_COLOR)
        self.question_overview_frame.pack(pady=10)
        self.update_question_overview()

        self.display_question()
        self.timer_seconds = self.current_quiz_time_limit_seconds
        self.timer_running = True
        self.start_timer()

    def start_practice_quiz(self):
        """Starts the practice quiz for the student."""
        if not hasattr(self, 'student_practice_questions') or not self.student_practice_questions:
            messagebox.showwarning("No Practice Questions", "No practice questions available. Please create some first.", parent=self.student_menu_win)
            return

        self.student_menu_win.destroy()
        self.quiz_win = tk.Toplevel(self.root)
        self.quiz_win.title("Practice Quiz")
        self.quiz_win.geometry("800x600")
        self.quiz_win.protocol("WM_DELETE_WINDOW", lambda: self.confirm_exit_quiz(self.quiz_win))
        self.quiz_win.config(bg=BG_COLOR)

        self.current_quiz_questions = self.student_practice_questions
        self.current_quiz_title = "Practice Quiz"
        self.current_quiz_time_limit_seconds = 0 # No time limit for practice

        self.current_question = 0
        self.selected_answers = {i: "" for i in range(len(self.current_quiz_questions))}

        self.quiz_title_label = tk.Label(self.quiz_win, text=self.current_quiz_title, font=("Arial", 16, "bold"), bg=BG_COLOR)
        self.quiz_title_label.pack(pady=10)

        self.timer_label = tk.Label(self.quiz_win, text="No time limit for practice.", font=("Arial", 12), bg=BG_COLOR)
        self.timer_label.pack(pady=5)

        self.question_number_label = tk.Label(self.quiz_win, text="", font=("Arial", 12), bg=BG_COLOR)
        self.question_number_label.pack(pady=5)

        self.question_text_area = scrolledtext.ScrolledText(self.quiz_win, wrap=tk.WORD, width=80, height=8, font=("Arial", 11),
                                                          bg=ENTRY_BG_COLOR, highlightbackground=ENTRY_BORDER_COLOR,
                                                          highlightthickness=2, bd=0)
        self.question_text_area.pack(pady=10, padx=20)
        self.question_text_area.config(state=tk.DISABLED)

        self.option_radio_buttons = []
        self.answer_var = tk.StringVar()
        for i in range(4):
            rb = tk.Radiobutton(self.quiz_win, text="", variable=self.answer_var, value="",
                                command=self.save_selected_answer,
                                font=("Arial", 10), bg=BG_COLOR, activebackground=BG_COLOR, selectcolor=BG_COLOR)
            rb.pack(anchor="w", padx=30, pady=2)
            self.option_radio_buttons.append(rb)

        navigation_frame = tk.Frame(self.quiz_win, bg=BG_COLOR)
        navigation_frame.pack(pady=20)

        self.prev_button = tk.Button(navigation_frame, text="Previous", command=self.prev_question, state=tk.DISABLED,
                                     bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, bd=2, relief="groove", padx=10, pady=5)
        self.prev_button.grid(row=0, column=0, padx=10)
        self.prev_button.bind("<Enter>", self._on_button_enter)
        self.prev_button.bind("<Leave>", self._on_button_leave)

        self.next_button = tk.Button(navigation_frame, text="Next", command=self.next_question,
                                     bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, bd=2, relief="groove", padx=10, pady=5)
        self.next_button.grid(row=0, column=1, padx=10)
        self.next_button.bind("<Enter>", self._on_button_enter)
        self.next_button.bind("<Leave>", self._on_button_leave)

        self.submit_button = tk.Button(self.quiz_win, text="End Practice", command=self.submit_practice_quiz,
                                       bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, bd=2, relief="groove", padx=10, pady=5)
        self.submit_button.pack(pady=10)
        self.submit_button.bind("<Enter>", self._on_button_enter)
        self.submit_button.bind("<Leave>", self._on_button_leave)

        self.question_overview_frame = tk.Frame(self.quiz_win, bg=BG_COLOR)
        self.question_overview_frame.pack(pady=10)
        self.update_question_overview()

        self.display_question()

    def start_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            minutes, seconds = divmod(self.timer_seconds, 60)
            self.timer_label.config(text=f"Time Left: {minutes:02d}:{seconds:02d}")
            self.timer_seconds -= 1
            self.timer_id = self.quiz_win.after(1000, self.start_timer)
        elif self.timer_running and self.timer_seconds <= 0:
            self.timer_label.config(text="Time's Up!")
            messagebox.showinfo("Time's Up", "Your time for the quiz has expired!", parent=self.quiz_win)
            self.submit_quiz()

    def display_question(self):
        """Displays the current question and its options."""
        if not self.current_quiz_questions:
            self.question_text_area.config(state=tk.NORMAL)
            self.question_text_area.delete("1.0", tk.END)
            self.question_text_area.insert("1.0", "No questions available.")
            self.question_text_area.config(state=tk.DISABLED)
            for rb in self.option_radio_buttons:
                rb.config(text="", value="", state=tk.DISABLED)
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.submit_button.config(state=tk.DISABLED)
            return

        question_data = self.current_quiz_questions[self.current_question]
        self.question_number_label.config(text=f"Question {self.current_question + 1} of {len(self.current_quiz_questions)}")

        self.question_text_area.config(state=tk.NORMAL)
        self.question_text_area.delete("1.0", tk.END)
        self.question_text_area.insert("1.0", question_data["question"])
        self.question_text_area.config(state=tk.DISABLED)

        self.answer_var.set(self.selected_answers.get(self.current_question, "")) # Load selected answer
        for i, option in enumerate(question_data["options"]):
            self.option_radio_buttons[i].config(text=f"{chr(65+i)}. {option}", value=option, state=tk.NORMAL)

        # Update navigation button states
        self.prev_button.config(state=tk.NORMAL if self.current_question > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_question < len(self.current_quiz_questions) - 1 else tk.DISABLED)

        self.update_question_overview()

    def save_selected_answer(self):
        self.selected_answers[self.current_question] = self.answer_var.get()
        self.update_question_overview()

    def next_question(self):
        if self.current_question < len(self.current_quiz_questions) - 1:
            self.current_question += 1
            self.display_question()

    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.display_question()

    def update_question_overview(self):
        """Updates the visual indicators for question status."""
        for widget in self.question_overview_frame.winfo_children():
            widget.destroy()

        num_cols = 10 # Number of columns for question buttons
        for i in range(len(self.current_quiz_questions)):
            status_color = UNANSWERED_COLOR
            if i in self.selected_answers and self.selected_answers[i] != "":
                status_color = ANSWERED_COLOR

            btn_color = status_color
            if i == self.current_question:
                btn_color = CURRENT_QUESTION_COLOR

            q_btn = tk.Button(self.question_overview_frame, text=str(i + 1),
                              command=lambda q_num=i: self.jump_to_question(q_num),
                              width=3, height=1, bg=btn_color, fg="black", bd=1, relief="raised")
            row = i // num_cols
            col = i % num_cols
            q_btn.grid(row=row, column=col, padx=2, pady=2)

    def jump_to_question(self, q_num):
        """Jumps to a specific question."""
        self.current_question = q_num
        self.display_question()

    def submit_quiz(self):
        """Submits the main quiz, calculates score, and shows results."""
        if self.timer_running and self.timer_id:
            self.quiz_win.after_cancel(self.timer_id)
            self.timer_running = False

        score = 0
        total_questions = len(self.current_quiz_questions)
        unanswered_count = 0

        for i, q_data in enumerate(self.current_quiz_questions):
            selected = self.selected_answers.get(i, "")
            if selected == "":
                unanswered_count += 1
            elif selected == q_data["answer"]:
                score += 1

        if unanswered_count > 0:
            if not messagebox.askyesno("Confirm Submission", f"You have {unanswered_count} unanswered questions. Are you sure you want to submit?", parent=self.quiz_win):
                if not self.timer_seconds <=0: # Resume timer if not expired
                    self.timer_running = True
                    self.start_timer()
                return

        percentage = (score / total_questions) * 100 if total_questions > 0 else 0

        self.quiz_win.destroy()
        self.show_results(score, total_questions, percentage, is_practice=False)

    def submit_practice_quiz(self):
        """Submits the practice quiz and shows results."""
        self.quiz_win.destroy()
        score = 0
        total_questions = len(self.current_quiz_questions)

        for i, q_data in enumerate(self.current_quiz_questions):
            selected = self.selected_answers.get(i, "")
            if selected == q_data["answer"]:
                score += 1

        percentage = (score / total_questions) * 100 if total_questions > 0 else 0
        self.show_results(score, total_questions, percentage, is_practice=True)

    def show_results(self, score, total_questions, percentage, is_practice):
        results_win = tk.Toplevel(self.root)
        results_win.title("Quiz Results" if not is_practice else "Practice Quiz Results")
        results_win.geometry("400x300")
        results_win.protocol("WM_DELETE_WINDOW", lambda: (results_win.destroy(), self.student_menu_dashboard()))
        results_win.config(bg=BG_COLOR)

        tk.Label(results_win, text="Quiz Finished!", font=("Arial", 16, "bold"), bg=BG_COLOR).pack(pady=20)
        tk.Label(results_win, text=f"Quiz Title: {self.current_quiz_title}", font=("Arial", 12), bg=BG_COLOR).pack(pady=5)
        tk.Label(results_win, text=f"Your Score: {score} / {total_questions}", font=("Arial", 12), bg=BG_COLOR).pack(pady=5)
        tk.Label(results_win, text=f"Percentage: {percentage:.2f}%", font=("Arial", 12), bg=BG_COLOR).pack(pady=5)

        return_btn = tk.Button(results_win, text="Return to Student Dashboard", width=25,
                               command=lambda: (results_win.destroy(), self.student_menu_dashboard()),
                               bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                               bd=2, relief="groove", padx=10, pady=5)
        return_btn.pack(pady=15)
        return_btn.bind("<Enter>", self._on_button_enter)
        return_btn.bind("<Leave>", self._on_button_leave)

        results_win.grab_set()
        self.root.wait_window(results_win)

    def confirm_exit_quiz(self, current_window):
        if self.timer_running:
            if self.timer_id:
                current_window.after_cancel(self.timer_id)
            self.timer_running = False

        if messagebox.askyesno("Exit Quiz", "Are you sure you want to exit the quiz? Your progress will be lost.",
                               parent=current_window):
            current_window.destroy()
            self.student_menu_dashboard()
        else:
            self.timer_running = True
            self.start_timer()

    def return_to_role_selection(self, current_window):
        current_window.destroy()
        self.role_selection_window()

if __name__ == "__main__":
    QuizApp()