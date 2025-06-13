import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import os  # Import os module for path operations

# Usernames and passwords of users
# format is username : password
USERS = {
    'student1': 'stud1',
    'lecturer1': 'lect1'
}

# User roles
USER_ROLES = {
    'student1': 'Student',
    'lecturer1': 'Lecturer'
}

# Define color variables for easy modification
BG_COLOR = 'white'  # Overall window background
BUTTON_BG_COLOR = '#800080'  # Purple for button background
BUTTON_HOVER_COLOR = '#A020F0'  # Slightly lighter purple for hover effect
BUTTON_TEXT_COLOR = 'white'  # White text for buttons
BUTTON_BORDER_COLOR = '#800080'  # Purple for button borders (unchanged, matches bg)
ENTRY_BG_COLOR = 'white'  # Entry widget background color
ENTRY_BORDER_COLOR = '#800080'  # Purple for entry borders
ANSWERED_COLOR = '#D4EDDA'  # Light green for answered questions
UNANSWERED_COLOR = '#F8D7DA'  # Light red for unanswered questions
CURRENT_QUESTION_COLOR = '#CCE5FF'  # Light blue for current question

# Define the default filename for questions persistence
QUESTIONS_FILE = "questions.json"
STUDENT_PRACTICE_QUESTIONS_FILE = "student_practice_questions.json"

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import os


# ... (rest of your existing constants like USERS, USER_ROLES, BG_COLOR, etc. remain the same) ...

class QuizApp:
    def __init__(self):
        self.root = tk.Tk()
        # Set the root window to be fully transparent initially
        # This prevents it from flashing even if it's briefly mapped before withdrawing
        self.root.wm_attributes('-alpha', 0)
        self.root.withdraw()
        # Force Tkinter to process the withdraw and alpha commands immediately
        self.root.update_idletasks()

        self.user_role = None

        # self.active_quiz_data will store the current quiz's title, time limit, and questions
        # Default structure if no quiz is loaded
        self.active_quiz_data = {
            "title": "No Quiz Loaded",
            "time_limit_minutes": 1,  # Default time limit in minutes
            "questions": []
        }
        self.questions = self.active_quiz_data["questions"]  # Reference to the active quiz's questions list

        self.current_question = 0  # For student quiz navigation
        self.selected_answers = {}  # For student quiz answers

        # New variables for question creation flow
        self.newly_created_questions = []  # Temporary storage for questions being created
        self.current_question_index_creation = 0  # Index for navigating creation forms
        self.create_win = None  # Reference to the question creation Toplevel window
        self.quiz_title_entry = None  # To hold the Tkinter Entry for quiz title (initial input)
        self.num_questions_entry = None  # To hold the Tkinter Entry for number of questions (initial input)
        self.quiz_time_limit_entry = None  # New: To hold the Tkinter Entry for quiz time limit (initial input)

        self.current_quiz_title_being_created = ""  # To persistently store the quiz title during creation flow
        self.current_quiz_time_limit_being_created = 0  # New: To persistently store the quiz time limit during creation flow

        self.timer_seconds = 0  # Will be set dynamically by quiz data
        self.timer_running = False

        # --- Persistence: Load questions at startup ---
        self._load_questions_on_startup()

        # Start with the role selection window
        self.role_selection_window()

        # The main event loop for the entire application
        self.root.mainloop()

    def _on_button_enter(self, event):
        """Changes button background on mouse enter."""
        event.widget.config(bg=BUTTON_HOVER_COLOR)

    def _on_button_leave(self, event):
        """Resets button background on mouse leave."""
        # For general buttons, reset to BUTTON_BG_COLOR
        # For navigation buttons, we need a more sophisticated logic
        # For simplicity for now, they will revert to BUTTON_BG_COLOR on leave if this is called directly.
        # If dynamic coloring is critical on hover out, it needs custom handling per button type.
        # Reverting to the initially configured BUTTON_BG_COLOR for all buttons.
        event.widget.config(bg=BUTTON_BG_COLOR)

    def _load_questions_on_startup(self):
        """Loads quiz data (title, time limit, questions) from the default JSON file when the app starts."""
        if os.path.exists(QUESTIONS_FILE):
            try:
                with open(QUESTIONS_FILE, 'r') as f:
                    loaded_data = json.load(f)

                if isinstance(loaded_data, list):
                    # Old format: just a list of questions
                    self.active_quiz_data = {
                        "title": "Loaded Quiz",
                        "time_limit_minutes": 1,  # Default time for old format
                        "questions": loaded_data
                    }
                    # Removed: messagebox.showinfo("Load Info", f"Loaded {len(loaded_data)} questions from old format {QUESTIONS_FILE}. Defaulting time limit to 1 minute.", parent=self.root)
                elif isinstance(loaded_data, dict) and \
                        all(k in loaded_data for k in ["title", "time_limit_minutes", "questions"]) and \
                        isinstance(loaded_data["questions"], list):
                    # New format: dict with title, time_limit, questions
                    self.active_quiz_data = loaded_data
                    # Removed: messagebox.showinfo("Load Info", f"Loaded '{self.active_quiz_data['title']}' with {len(self.active_quiz_data['questions'])} questions (Time Limit: {self.active_quiz_data['time_limit_minutes']} mins) from {QUESTIONS_FILE}.", parent=self.root)
                else:
                    messagebox.showwarning("Load Error",
                                           "Questions file format is invalid. Starting with no questions.",
                                           parent=self.root)
                    self.active_quiz_data = {"title": "No Quiz Loaded", "time_limit_minutes": 1, "questions": []}

                # Basic validation for loaded questions within the list
                valid_questions = []
                for q in self.active_quiz_data["questions"]:
                    if all(k in q for k in ("question", "options", "answer")) and \
                            isinstance(q["options"], list) and len(q["options"]) == 4:
                        valid_questions.append(q)
                    else:
                        print(f"Skipping invalid question loaded from file: {q}")  # For debugging
                self.active_quiz_data["questions"] = valid_questions  # Update with only valid questions

            except json.JSONDecodeError:
                messagebox.showerror("Load Error",
                                     "Error decoding questions file (invalid JSON). Starting with no questions).",
                                     parent=self.root)
                self.active_quiz_data = {"title": "No Quiz Loaded", "time_limit_minutes": 1, "questions": []}
            except Exception as e:
                messagebox.showerror("Load Error",
                                     f"An unexpected error occurred loading questions: {e}. Starting with no questions.",
                                     parent=self.root)
                self.active_quiz_data = {"title": "No Quiz Loaded", "time_limit_minutes": 1, "questions": []}
        else:
            print(f"No {QUESTIONS_FILE} found. Starting with no questions.")

        self.questions = self.active_quiz_data[
            "questions"]  # Ensure self.questions always references the active quiz's questions

    def _save_questions_to_file(self, quiz_data_to_save, filename=QUESTIONS_FILE):
        """
        Saves a complete quiz data dictionary (title, time_limit_minutes, questions) to a specified JSON file.
        """
        try:
            with open(filename, 'w') as f:
                json.dump(quiz_data_to_save, f, indent=4)
            print(f"Saved {len(quiz_data_to_save['questions'])} questions to {filename}.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save questions to {filename}:\n{e}", parent=self.root)

    def _load_student_practice_questions_on_startup(self):
        """Loads student practice questions from their dedicated JSON file."""
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
                    # Removed: if valid_questions:
                    # Removed:     messagebox.showinfo("Load Info", f"Loaded {len(valid_questions)} student practice questions from {STUDENT_PRACTICE_QUESTIONS_FILE}.", parent=self.root)
                else:
                    messagebox.showwarning("Load Error",
                                           "Student practice questions file format is invalid. Starting with no practice questions.",
                                           parent=self.root)
                    self.student_practice_questions = []
            except json.JSONDecodeError:
                messagebox.showerror("Load Error",
                                     "Error decoding student practice questions file (invalid JSON). Starting with no practice questions).",
                                     parent=self.root)
                self.student_practice_questions = []
            except Exception as e:
                messagebox.showerror("Load Error",
                                     f"An unexpected error occurred loading student practice questions: {e}. Starting with no practice questions.",
                                     parent=self.root)
                self.student_practice_questions = []
        else:
            print(f"No {STUDENT_PRACTICE_QUESTIONS_FILE} found. Starting with no student practice questions.")

    def _save_student_practice_questions_to_file(self):
        """Saves student practice questions to their dedicated JSON file."""
        try:
            with open(STUDENT_PRACTICE_QUESTIONS_FILE, 'w') as f:
                json.dump(self.student_practice_questions, f, indent=4)
            print(
                f"Saved {len(self.student_practice_questions)} student practice questions to {STUDENT_PRACTICE_QUESTIONS_FILE}.")
        except Exception as e:
            messagebox.showerror("Save Error",
                                 f"Failed to save student practice questions to {STUDENT_PRACTICE_QUESTIONS_FILE}:\n{e}",
                                 parent=self.root)

    def role_selection_window(self):
        # Close windows before showing role selection
        if hasattr(self, 'login_win') and self.login_win.winfo_exists():
            self.login_win.destroy()
        if hasattr(self, 'lect_win') and self.lect_win.winfo_exists():
            self.lect_win.destroy()
        if hasattr(self, 'quiz_win') and self.quiz_win.winfo_exists():
            # If a quiz window is open, ensure timer is stopped before closing
            if self.timer_running and self.timer_id:
                self.quiz_win.after_cancel(self.timer_id)
                self.timer_running = False
            self.quiz_win.destroy()
        if hasattr(self, 'student_menu_win') and self.student_menu_win.winfo_exists():
            self.student_menu_win.destroy()
        # Close creation window if it's open
        if hasattr(self, 'create_win') and self.create_win and self.create_win.winfo_exists():
            self.create_win.destroy()
        # Close initial create window if it's open
        if hasattr(self, 'create_start_win') and self.create_start_win and self.create_start_win.winfo_exists():
            self.create_start_win.destroy()
        # Close student creation window if it's open
        if hasattr(self, 'student_create_win') and self.student_create_win and self.student_create_win.winfo_exists():
            self.student_create_win.destroy()
        # Close student initial create window if it's open
        if hasattr(self,
                   'student_create_start_win') and self.student_create_start_win and self.student_create_start_win.winfo_exists():
            self.student_create_start_win.destroy()

        self.role_win = tk.Toplevel(self.root)
        self.role_win.title("Quiz System - Select Role")
        self.role_win.geometry("300x180")
        self.role_win.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.role_win.config(bg=BG_COLOR)  # Set window background to white

        tk.Label(self.role_win, text="Please select your role:", font=("Arial", 14), bg=BG_COLOR).pack(pady=20)

        # Buttons with specified background and border colors
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
        self.login_win.geometry("300x220")
        self.login_win.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.login_win.config(bg=BG_COLOR)  # Set window background to white

        tk.Label(self.login_win, text="Username:", bg=BG_COLOR).pack(pady=(20, 5))
        # Entry widget with specified background and border colors
        self.entry_username = tk.Entry(self.login_win, bg=ENTRY_BG_COLOR,
                                       highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
        self.entry_username.pack()

        tk.Label(self.login_win, text="Password:", bg=BG_COLOR).pack(pady=(10, 5))
        # Entry widget with specified background and border colors
        self.entry_password = tk.Entry(self.login_win, show="*", bg=ENTRY_BG_COLOR,
                                       highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
        self.entry_password.pack()

        # Buttons with specified background and border colors
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
            # error messages
            if username in USERS and USERS[username] == password and USER_ROLES.get(
                    username) != self.chosen_role_for_login:
                messagebox.showerror("Login",
                                     f"This login is for a {USER_ROLES.get(username)}. Please select the correct role.",
                                     parent=self.login_win)
            else:
                messagebox.showerror("Login", "Invalid login credentials", parent=self.login_win)

    def lecturer_dashboard(self):
        self.lect_win = tk.Toplevel(self.root)
        self.lect_win.title("Lecturer Dashboard")
        self.lect_win.geometry("600x350")  # Increased height for more buttons
        self.lect_win.protocol("WM_DELETE_WINDOW", lambda: self.return_to_role_selection(self.lect_win))
        self.lect_win.config(bg=BG_COLOR)  # Set window background to white

        tk.Label(self.lect_win, text="Lecturer Dashboard", font=("Arial", 16, "bold"), bg=BG_COLOR).pack(pady=20)

        # Frame for buttons for better layout
        button_frame = tk.Frame(self.lect_win, bg=BG_COLOR)
        button_frame.pack(pady=10)

        # Changed from "Upload Questions" to "Create Questions"
        self.create_questions_btn = tk.Button(button_frame, text="Create New Questions", width=25,
                                              command=self.create_questions_flow_start,  # New command
                                              bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                              bd=2, relief="groove", padx=10, pady=5)
        self.create_questions_btn.grid(row=0, column=0, padx=10, pady=5)  # Using grid
        self.create_questions_btn.bind("<Enter>", self._on_button_enter)
        self.create_questions_btn.bind("<Leave>", self._on_button_leave)

        self.view_questions_btn = tk.Button(button_frame, text="View Current Quiz Questions", width=25,  # Changed text
                                            command=self.view_questions_window,
                                            bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                            bd=2, relief="groove", padx=10, pady=5)
        self.view_questions_btn.grid(row=0, column=1, padx=10, pady=5)  # Using grid
        self.view_questions_btn.bind("<Enter>", self._on_button_enter)
        self.view_questions_btn.bind("<Leave>", self._on_button_leave)

        self.delete_questions_btn = tk.Button(button_frame, text="Delete All Questions in Current Quiz", width=25,
                                              # Changed text
                                              command=self.delete_all_questions,
                                              bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                              bd=2, relief="groove", padx=10, pady=5)
        self.delete_questions_btn.grid(row=1, column=0, padx=10, pady=5)  # Using grid
        self.delete_questions_btn.bind("<Enter>", self._on_button_enter)
        self.delete_questions_btn.bind("<Leave>", self._on_button_leave)

        # New button for loading questions from a file (optional, but good to have back)
        self.load_from_file_btn = tk.Button(button_frame, text="Load Quiz from File (JSON)", width=25,  # Changed text
                                            command=self.load_questions_from_file,  # New command
                                            bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                            bd=2, relief="groove", padx=10, pady=5)
        self.load_from_file_btn.grid(row=1, column=1, padx=10, pady=5)  # Using grid
        self.load_from_file_btn.bind("<Enter>", self._on_button_enter)
        self.load_from_file_btn.bind("<Leave>", self._on_button_leave)

        return_btn = tk.Button(self.lect_win, text="Return to Role Selection", width=25,
                               command=lambda: self.return_to_role_selection(self.lect_win),
                               bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                               bd=2, relief="groove", padx=10, pady=5)
        return_btn.pack(pady=15)
        return_btn.bind("<Enter>", self._on_button_enter)
        return_btn.bind("<Leave>", self._on_button_leave)

        # Call a method to initially update button states based on whether questions are loaded
        self.update_lecturer_dashboard_buttons()

    def update_lecturer_dashboard_buttons(self):
        """Enables/disables buttons based on whether questions are loaded."""
        if self.questions:
            # self.create_questions_btn.config(state=tk.DISABLED) # Keep enabled for continuous creation
            self.view_questions_btn.config(state=tk.NORMAL)
            self.delete_questions_btn.config(state=tk.NORMAL)
            # self.load_from_file_btn.config(state=tk.DISABLED) # Keep enabled to allow loading other quizzes
        else:
            self.view_questions_btn.config(state=tk.DISABLED)
            self.delete_questions_btn.config(state=tk.DISABLED)
            # self.create_questions_btn.config(state=tk.NORMAL) # Already default
            # self.load_from_file_btn.config(state=tk.NORMAL) # Already default

    def load_questions_from_file(self):
        """Allows lecturer to load quiz data (title, time limit, questions) from a JSON file, replacing current quiz."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], parent=self.lect_win)
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    loaded_data = json.load(f)

                new_active_quiz_data = None

                if isinstance(loaded_data, list):
                    # Old format: just a list of questions
                    new_active_quiz_data = {
                        "title": os.path.basename(file_path).replace(".json", ""),  # Use filename as title
                        "time_limit_minutes": 1,  # Default time for old format
                        "questions": loaded_data
                    }
                    messagebox.showinfo("Load Info",
                                        f"Loaded {len(loaded_data)} questions from old format '{os.path.basename(file_path)}'. Defaulting time limit to 1 minute.",
                                        parent=self.lect_win)
                elif isinstance(loaded_data, dict) and \
                        all(k in loaded_data for k in ["title", "time_limit_minutes", "questions"]) and \
                        isinstance(loaded_data["questions"], list):
                    # New format: dict with title, time_limit, questions
                    new_active_quiz_data = loaded_data
                    messagebox.showinfo("Load Info",
                                        f"Loaded '{new_active_quiz_data['title']}' with {len(new_active_quiz_data['questions'])} questions (Time Limit: {new_active_quiz_data['time_limit_minutes']} mins) from '{os.path.basename(file_path)}'.",
                                        parent=self.lect_win)
                else:
                    messagebox.showwarning("Load Error", "The selected file format is invalid. No quiz loaded.",
                                           parent=self.lect_win)
                    return  # Exit if format is invalid

                # Validate questions within the list for the new_active_quiz_data
                valid_new_questions = []
                for q in new_active_quiz_data["questions"]:
                    if all(k in q for k in ("question", "options", "answer")) and \
                            isinstance(q["options"], list) and len(q["options"]) == 4:
                        valid_new_questions.append(q)
                    else:
                        print(f"Skipping invalid question from loaded file: {q}")  # For debugging

                if valid_new_questions:
                    new_active_quiz_data["questions"] = valid_new_questions
                    self.active_quiz_data = new_active_quiz_data  # Set the new quiz as active
                    self.questions = self.active_quiz_data["questions"]  # Update the reference
                    self._save_questions_to_file(
                        self.active_quiz_data)  # Also save the newly loaded list as the default active quiz (questions.json)
                else:
                    messagebox.showwarning("No Valid Questions",
                                           "The selected file contains no valid questions or is empty. No quiz loaded.",
                                           parent=self.lect_win)
                    return  # Exit if no valid questions

                self.update_lecturer_dashboard_buttons()
            except json.JSONDecodeError:
                messagebox.showerror("Load Error", "Error decoding selected file (invalid JSON).", parent=self.lect_win)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load questions from file:\n{e}", parent=self.lect_win)
        else:
            messagebox.showwarning("Warning", "No file selected.", parent=self.lect_win)

    # --- New Question Creation Flow ---
    def create_questions_flow_start(self):
        """Initial window to ask for the number of questions to create, quiz title, and time limit."""
        # Reset temporary questions and metadata for a new creation session
        self.newly_created_questions = []
        self.current_question_index_creation = 0
        self.current_quiz_title_being_created = ""  # Reset title for new creation
        self.current_quiz_time_limit_being_created = 0  # Reset time limit for new creation

        self.create_start_win = tk.Toplevel(self.lect_win)
        self.create_start_win.title("Create New Quiz")
        self.create_start_win.geometry("400x300")  # Increased height
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
        self.num_questions_entry.insert(0, "1")  # Default to 1 question

        # New: Quiz Time Limit input
        tk.Label(self.create_start_win, text="Quiz Time Limit (minutes):", font=("Arial", 12), bg=BG_COLOR).pack(
            pady=(10, 5))
        self.quiz_time_limit_entry = tk.Entry(self.create_start_win, width=10, bg=ENTRY_BG_COLOR,
                                              highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
        self.quiz_time_limit_entry.pack(pady=5)
        self.quiz_time_limit_entry.insert(0, "1")  # Default to 1 minute

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
            self.current_quiz_title_being_created = quiz_title  # Store the title persistently
            self.current_quiz_time_limit_being_created = time_limit_minutes  # Store the time limit persistently
            self.create_start_win.destroy()  # Close the initial window

            # Initialize self.newly_created_questions with empty question structures
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
        """Displays the form for inputting a single question."""
        if self.create_win and self.create_win.winfo_exists():
            self.create_win.destroy()  # Close previous form if open

        display_title = self.current_quiz_title_being_created if self.current_quiz_title_being_created else "New Quiz"
        self.create_win = tk.Toplevel(self.lect_win)
        self.create_win.title(
            f"{display_title} - Question {self.current_question_index_creation + 1}/{self.num_questions_to_create}")
        self.create_win.geometry("700x550")
        self.create_win.transient(self.lect_win)
        self.create_win.grab_set()
        self.create_win.config(bg=BG_COLOR)
        self.create_win.protocol("WM_DELETE_WINDOW", self._cancel_question_creation)

        # Question Label and Entry
        tk.Label(self.create_win, text=f"Question {self.current_question_index_creation + 1}:",
                 font=("Arial", 12, "bold"), bg=BG_COLOR).pack(pady=(10, 5))
        self.q_entry = scrolledtext.ScrolledText(self.create_win, wrap=tk.WORD, width=70, height=4, font=("Arial", 10),
                                                 bg=ENTRY_BG_COLOR, highlightbackground=ENTRY_BORDER_COLOR,
                                                 highlightthickness=2, bd=0)
        self.q_entry.pack(pady=5)

        # Options Labels and Entries
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

            # Radiobutton for selecting correct answer
            rb = tk.Radiobutton(opt_frame, text="Correct", variable=self.correct_option_var, value=label_text,
                                bg=BG_COLOR, activebackground=BG_COLOR, selectcolor=BG_COLOR)
            rb.pack(side=tk.RIGHT, padx=5)

        # Navigation and Save Buttons
        nav_frame = tk.Frame(self.create_win, bg=BG_COLOR)
        nav_frame.pack(pady=20)

        # Save Current Question and Move Buttons
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

        finalize_btn = tk.Button(self.create_win, text="Finalize & Save Quiz", width=20,  # Changed button text
                                 command=self._finalize_created_questions,
                                 bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                 bd=2, relief="groove", padx=10, pady=5)
        finalize_btn.pack(pady=10)
        finalize_btn.bind("<Enter>", self._on_button_enter)
        finalize_btn.bind("<Leave>", self._on_button_leave)

        # Load data for the current question
        self._load_question_for_creation_editing()

    def _save_current_question_input(self):
        """Saves the input from the current form into self.newly_created_questions."""
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

        # Convert option label (A, B, C, D) to the actual option text
        correct_answer_text = ""
        try:
            # Map 'A' to index 0, 'B' to index 1, etc.
            correct_index = ord(correct_opt_label.upper()) - ord('A')
            if 0 <= correct_index < len(options):
                correct_answer_text = options[correct_index]
            else:
                raise ValueError("Invalid correct option selected.")
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Could not determine correct answer from selected option.",
                                 parent=self.create_win)
            return False

        self.newly_created_questions[self.current_question_index_creation] = {
            "question": q_text,
            "options": options,
            "answer": correct_answer_text
        }
        return True

    def _load_question_for_creation_editing(self):
        """Populates the form with data for the current question being edited/viewed."""
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
                    # Find the label (A, B, C, D) corresponding to the answer text
                    answer_index = q_data["options"].index(q_data["answer"])
                    self.correct_option_var.set(chr(ord('A') + answer_index))
                except ValueError:  # Answer text not found in options
                    self.correct_option_var.set("")
            else:
                self.correct_option_var.set("")
        # Re-enable all inputs for editing
        self.q_entry.config(state=tk.NORMAL)
        for entry in self.option_entries:
            entry.config(state=tk.NORMAL)

    def _save_and_navigate_question_creation_form_next(self):
        """Saves current question and moves to the next."""
        if self._save_current_question_input():
            if self.current_question_index_creation < self.num_questions_to_create - 1:
                self.current_question_index_creation += 1
                self.display_question_creation_form()
            else:
                messagebox.showinfo("End of Questions",
                                    "You have reached the last question. Click 'Finalize & Save Quiz' to save your quiz.",
                                    parent=self.create_win)

    def _save_and_navigate_question_creation_form_prev(self):
        """Saves current question and moves to the previous."""
        if self._save_current_question_input():
            if self.current_question_index_creation > 0:
                self.current_question_index_creation -= 1
                self.display_question_creation_form()
            else:
                messagebox.showinfo("First Question", "You are already at the first question.", parent=self.create_win)

    def _finalize_created_questions(self):
        """Validates and saves all newly created questions to a user-defined file and makes it the active quiz."""
        if not self._save_current_question_input():  # Save the last question being edited
            return

        # Perform a final check on all questions before saving
        if not self.newly_created_questions:
            messagebox.showwarning("No Questions", "No questions have been created to finalize.",
                                   parent=self.create_win)
            return

        for i, q_data in enumerate(self.newly_created_questions):
            if not q_data["question"] or any(not opt for opt in q_data["options"]) or not q_data["answer"]:
                messagebox.showerror("Validation Error",
                                     f"Question {i + 1} is incomplete. Please fill in all fields for all questions.",
                                     parent=self.create_win)
                return

        # Prepare the quiz data dictionary
        quiz_data_to_save = {
            "title": self.current_quiz_title_being_created,
            "time_limit_minutes": self.current_quiz_time_limit_being_created,
            "questions": self.newly_created_questions
        }

        # Use filedialog to let the lecturer choose where to save the file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"{quiz_data_to_save['title'].replace(' ', '_').lower()}_quiz.json",
            parent=self.create_win
        )

        if file_path:
            self._save_questions_to_file(quiz_data_to_save, file_path)
            # Make the newly created quiz the active quiz
            self.active_quiz_data = quiz_data_to_save
            self.questions = self.active_quiz_data["questions"]
            self._save_questions_to_file(self.active_quiz_data)  # Also save as default questions.json
            messagebox.showinfo("Quiz Saved",
                                f"Quiz '{quiz_data_to_save['title']}' saved successfully and set as active quiz!",
                                parent=self.create_win)
            self.create_win.destroy()  # Close creation window
            self.update_lecturer_dashboard_buttons()  # Update lecturer dashboard buttons
        else:
            messagebox.showwarning("Save Cancelled", "Quiz save operation cancelled.", parent=self.create_win)

    def _cancel_question_creation(self):
        """Handles cancellation of question creation, with confirmation."""
        if messagebox.askyesno("Cancel Creation",
                               "Are you sure you want to cancel quiz creation? Unsaved changes will be lost.",
                               parent=self.create_win):
            self.create_win.destroy()  # Close the creation window
            # Optionally clear temporary data if needed, but it's reset on next start anyway
            self.newly_created_questions = []
            self.current_question_index_creation = 0

    def view_questions_window(self):
        """Displays all current questions in a new window."""
        view_win = tk.Toplevel(self.lect_win)
        view_win.title(f"Current Quiz: {self.active_quiz_data['title']} ({len(self.questions)} Questions)")
        view_win.geometry("700x500")
        view_win.transient(self.lect_win)
        view_win.grab_set()
        view_win.config(bg=BG_COLOR)

        tk.Label(view_win, text=f"Quiz: {self.active_quiz_data['title']}", font=("Arial", 14, "bold"),
                 bg=BG_COLOR).pack(pady=(10, 5))
        tk.Label(view_win, text=f"Time Limit: {self.active_quiz_data['time_limit_minutes']} minutes",
                 font=("Arial", 12), bg=BG_COLOR).pack(pady=5)

        if not self.questions:
            tk.Label(view_win, text="No questions loaded.", font=("Arial", 12), bg=BG_COLOR).pack(pady=20)
            close_btn = tk.Button(view_win, text="Close", command=view_win.destroy,
                                  bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                  bd=2, relief="groove", padx=10, pady=5)
            close_btn.pack(pady=10)
            close_btn.bind("<Enter>", self._on_button_enter)
            close_btn.bind("<Leave>", self._on_button_leave)
            return

        text_area = scrolledtext.ScrolledText(view_win, wrap=tk.WORD, width=80, height=20, font=("Arial", 10),
                                              bg=ENTRY_BG_COLOR, highlightbackground=ENTRY_BORDER_COLOR,
                                              highlightthickness=2, bd=0)
        text_area.pack(pady=10, padx=20, expand=True, fill="both")

        for i, q_data in enumerate(self.questions):
            text_area.insert(tk.END, f"Question {i + 1}:\n", "bold")
            text_area.insert(tk.END, f"  Q: {q_data['question']}\n")
            for j, option in enumerate(q_data['options']):
                text_area.insert(tk.END, f"    {chr(65 + j)}. {option}\n")
            text_area.insert(tk.END, f"  Correct Answer: {q_data['answer']}\n\n")

        text_area.config(state=tk.DISABLED)  # Make read-only

        close_btn = tk.Button(view_win, text="Close", command=view_win.destroy,
                              bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                              bd=2, relief="groove", padx=10, pady=5)
        close_btn.pack(pady=10)
        close_btn.bind("<Enter>", self._on_button_enter)
        close_btn.bind("<Leave>", self._on_button_leave)

        view_win.grab_set()
        self.root.wait_window(view_win)

    def delete_all_questions(self):
        """Deletes all currently loaded questions after confirmation."""
        if messagebox.askyesno("Confirm Deletion",
                               "Are you sure you want to delete ALL questions in the current quiz? This action cannot be undone.",
                               parent=self.lect_win):
            self.active_quiz_data = {"title": "No Quiz Loaded", "time_limit_minutes": 1, "questions": []}
            self.questions = self.active_quiz_data["questions"]  # Update reference
            self.selected_answers = {}  # Clear any student answers if quiz was in progress
            self._save_questions_to_file(self.active_quiz_data)  # Save empty quiz to file
            messagebox.showinfo("Questions Deleted", "All questions have been deleted.", parent=self.lect_win)
            self.update_lecturer_dashboard_buttons()

    def student_menu_dashboard(self):
        """Displays the student's main menu."""
        self.student_menu_win = tk.Toplevel(self.root)
        self.student_menu_win.title("Student Dashboard")
        self.student_menu_win.geometry("400x280")  # Increased height for new button
        self.student_menu_win.protocol("WM_DELETE_WINDOW", lambda: self.return_to_role_selection(self.student_menu_win))
        self.student_menu_win.config(bg=BG_COLOR)

        tk.Label(self.student_menu_win, text="Student Dashboard", font=("Arial", 16, "bold"), bg=BG_COLOR).pack(pady=20)

        button_frame = tk.Frame(self.student_menu_win, bg=BG_COLOR)
        button_frame.pack(pady=10)

        # Button to load and start the main quiz (lecturer's quiz)
        main_quiz_btn = tk.Button(button_frame, text="Load & Start Main Quiz", width=25,  # Changed text for clarity
                                  command=self.student_load_and_start_main_quiz,  # New dedicated method
                                  bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                  bd=2, relief="groove", padx=10, pady=5)
        main_quiz_btn.grid(row=0, column=0, padx=10, pady=5)  # Using grid
        main_quiz_btn.bind("<Enter>", self._on_button_enter)
        main_quiz_btn.bind("<Leave>", self._on_button_leave)

        # Button to create practice questions
        create_practice_btn = tk.Button(button_frame, text="Create My Practice Questions", width=25,
                                        # Changed text for clarity
                                        command=self.student_create_questions_flow_start,
                                        bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                        bd=2, relief="groove", padx=10, pady=5)
        create_practice_btn.grid(row=0, column=1, padx=10, pady=5)  # Using grid
        create_practice_btn.bind("<Enter>", self._on_button_enter)
        create_practice_btn.bind("<Leave>", self._on_button_leave)

        # Button to start a practice quiz from their own questions
        start_practice_btn = tk.Button(button_frame, text="Start My Practice Quiz", width=25,
                                       # Changed text for clarity
                                       command=lambda: self.start_quiz(quiz_type="practice_my_questions"),
                                       # Pass quiz type
                                       bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                       bd=2, relief="groove", padx=10, pady=5)
        start_practice_btn.grid(row=1, column=0, padx=10, pady=5)  # Using grid
        start_practice_btn.bind("<Enter>", self._on_button_enter)
        start_practice_btn.bind("<Leave>", self._on_button_leave)

        # NEW: Button to load and start an external quiz for practice
        external_practice_btn = tk.Button(button_frame, text="Load & Start External Practice Quiz", width=25,
                                          command=self.student_load_and_start_quiz_from_file,  # New method
                                          bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                          bd=2, relief="groove", padx=10, pady=5)
        external_practice_btn.grid(row=1, column=1, padx=10, pady=5)  # Using grid
        external_practice_btn.bind("<Enter>", self._on_button_enter)
        external_practice_btn.bind("<Leave>", self._on_button_leave)

        return_btn = tk.Button(self.student_menu_win, text="Return to Role Selection", width=25,
                               command=lambda: self.return_to_role_selection(self.student_menu_win),
                               bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                               bd=2, relief="groove", padx=10, pady=5)
        return_btn.pack(pady=15)
        return_btn.bind("<Enter>", self._on_button_enter)
        return_btn.bind("<Leave>", self._on_button_leave)

    def student_load_and_start_main_quiz(self):
        """Allows student to load a quiz from a JSON file and start it as the main quiz.
           This also saves the loaded quiz as the new default 'questions.json'.
        """
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], parent=self.student_menu_win)
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    loaded_data = json.load(f)

                quiz_data_to_use = None

                if isinstance(loaded_data, list):
                    # Old format: just a list of questions
                    quiz_data_to_use = {
                        "title": os.path.basename(file_path).replace(".json", ""),
                        "time_limit_minutes": 1,  # Default time for old format
                        "questions": loaded_data
                    }
                elif isinstance(loaded_data, dict) and \
                        all(k in loaded_data for k in ["title", "time_limit_minutes", "questions"]) and \
                        isinstance(loaded_data["questions"], list):
                    # New format: dict with title, time_limit, questions
                    quiz_data_to_use = loaded_data
                else:
                    messagebox.showwarning("Load Error", "The selected file format is invalid. Cannot load main quiz.",
                                           parent=self.student_menu_win)
                    return  # Exit if format is invalid

                # Validate questions within the list
                valid_questions = []
                for q in quiz_data_to_use["questions"]:
                    if all(k in q for k in ("question", "options", "answer")) and \
                            isinstance(q["options"], list) and len(q["options"]) == 4:
                        valid_questions.append(q)
                    else:
                        print(f"Skipping invalid question from loaded file: {q}")  # For debugging

                if valid_questions:
                    quiz_data_to_use["questions"] = valid_questions

                    # Update active quiz data and save it as the new default main quiz
                    self.active_quiz_data = quiz_data_to_use
                    self.questions = self.active_quiz_data["questions"]
                    self._save_questions_to_file(self.active_quiz_data)  # Save as default questions.json

                    self.start_quiz(quiz_type="main",
                                    quiz_data_override=self.active_quiz_data)  # Start the newly loaded main quiz
                else:
                    messagebox.showwarning("No Valid Questions",
                                           "The selected file contains no valid questions or is empty. Cannot start main quiz.",
                                           parent=self.student_menu_win)
                    return  # Exit if no valid questions

            except json.JSONDecodeError:
                messagebox.showerror("Load Error", "Error decoding selected file (invalid JSON).",
                                     parent=self.student_menu_win)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load main quiz from file:\n{e}", parent=self.student_menu_win)
        else:
            messagebox.showwarning("Warning", "No file selected.", parent=self.student_menu_win)

    def student_load_and_start_quiz_from_file(self):
        """Allows student to load a quiz from a JSON file and start it as a practice quiz."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], parent=self.student_menu_win)
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    loaded_data = json.load(f)

                quiz_data_to_use = None

                if isinstance(loaded_data, list):
                    # Old format: just a list of questions
                    quiz_data_to_use = {
                        "title": os.path.basename(file_path).replace(".json", "") + " (External Practice)",
                        "time_limit_minutes": 1,  # Default time for old format
                        "questions": loaded_data
                    }
                elif isinstance(loaded_data, dict) and \
                        all(k in loaded_data for k in ["title", "time_limit_minutes", "questions"]) and \
                        isinstance(loaded_data["questions"], list):
                    # New format: dict with title, time_limit, questions
                    quiz_data_to_use = loaded_data
                    quiz_data_to_use["title"] += " (External Practice)"  # Append to title for clarity
                else:
                    messagebox.showwarning("Load Error", "The selected file format is invalid. Cannot start quiz.",
                                           parent=self.student_menu_win)
                    return  # Exit if format is invalid

                # Validate questions within the list
                valid_questions = []
                for q in quiz_data_to_use["questions"]:
                    if all(k in q for k in ("question", "options", "answer")) and \
                            isinstance(q["options"], list) and len(q["options"]) == 4:
                        valid_questions.append(q)
                    else:
                        print(f"Skipping invalid question from loaded file: {q}")  # For debugging

                if valid_questions:
                    quiz_data_to_use["questions"] = valid_questions
                    self.start_quiz(quiz_type="external_practice", quiz_data_override=quiz_data_to_use)
                else:
                    messagebox.showwarning("No Valid Questions",
                                           "The selected file contains no valid questions or is empty. Cannot start quiz.",
                                           parent=self.student_menu_win)
                    return  # Exit if no valid questions

            except json.JSONDecodeError:
                messagebox.showerror("Load Error", "Error decoding selected file (invalid JSON).",
                                     parent=self.student_menu_win)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load quiz from file:\n{e}", parent=self.student_menu_win)
        else:
            messagebox.showwarning("Warning", "No file selected.", parent=self.student_menu_win)

    # --- Student Practice Question Creation Flow ---
    def student_create_questions_flow_start(self):
        """Initial window for students to create practice questions."""
        # Reset temporary questions and metadata for a new creation session
        self.newly_created_questions = []  # Use this temp list for student creation too
        self.current_student_q_index_creation = 0
        self.current_student_quiz_title = "My Practice Quiz"  # Default title for student quizzes

        self.student_create_start_win = tk.Toplevel(self.student_menu_win)
        self.student_create_start_win.title("Create Practice Questions")
        self.student_create_start_win.geometry("400x200")
        self.student_create_start_win.transient(self.student_menu_win)
        self.student_create_start_win.grab_set()
        self.student_create_start_win.config(bg=BG_COLOR)
        self.student_create_start_win.protocol("WM_DELETE_WINDOW", self.student_create_start_win.destroy)

        tk.Label(self.student_create_start_win, text="Enter the number of practice questions:", font=("Arial", 12),
                 bg=BG_COLOR).pack(pady=(10, 5))
        self.student_num_q_entry = tk.Entry(self.student_create_start_win, width=10, bg=ENTRY_BG_COLOR,
                                            highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
        self.student_num_q_entry.pack(pady=5)
        self.student_num_q_entry.insert(0, "1")  # Default to 1 question

        start_creating_btn = tk.Button(self.student_create_start_win, text="Start Creating",
                                       command=self._student_start_question_form_from_initial,
                                       bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                       bd=2, relief="groove", padx=10, pady=5)
        start_creating_btn.pack(pady=15)
        start_creating_btn.bind("<Enter>", self._on_button_enter)
        start_creating_btn.bind("<Leave>", self._on_button_leave)

        self.root.wait_window(self.student_create_start_win)

    def _student_start_question_form_from_initial(self):
        """Validates input and starts the question form for students."""
        try:
            num_q = int(self.student_num_q_entry.get())
            if num_q <= 0:
                messagebox.showerror("Invalid Input", "Please enter a positive number of questions.",
                                     parent=self.student_create_start_win)
                return

            self.num_student_questions_to_create = num_q
            self.student_create_start_win.destroy()  # Close the initial window

            # Initialize self.newly_created_questions (used as temp storage) with empty structures
            self.newly_created_questions = [
                {"question": "", "options": ["", "", "", ""], "answer": ""}
                for _ in range(self.num_student_questions_to_create)
            ]
            self.current_student_q_index_creation = 0
            self._student_display_question_creation_form()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for questions.",
                                 parent=self.student_create_start_win)

    def _student_display_question_creation_form(self):
        """Displays the form for inputting a single practice question for students."""
        if self.student_create_win and self.student_create_win.winfo_exists():
            self.student_create_win.destroy()  # Close previous form if open

        self.student_create_win = tk.Toplevel(self.student_menu_win)
        self.student_create_win.title(
            f"Practice Question {self.current_student_q_index_creation + 1}/{self.num_student_questions_to_create}")
        self.student_create_win.geometry("700x550")
        self.student_create_win.transient(self.student_menu_win)
        self.student_create_win.grab_set()
        self.student_create_win.config(bg=BG_COLOR)
        self.student_create_win.protocol("WM_DELETE_WINDOW", self._cancel_student_question_creation)

        # Question Label and Entry
        tk.Label(self.student_create_win, text=f"Practice Question {self.current_student_q_index_creation + 1}:",
                 font=("Arial", 12, "bold"), bg=BG_COLOR).pack(pady=(10, 5))
        self.student_q_entry = scrolledtext.ScrolledText(self.student_create_win, wrap=tk.WORD, width=70, height=4,
                                                         font=("Arial", 10),
                                                         bg=ENTRY_BG_COLOR, highlightbackground=ENTRY_BORDER_COLOR,
                                                         highlightthickness=2, bd=0)
        self.student_q_entry.pack(pady=5)

        # Options Labels and Entries
        self.student_option_entries = []
        self.student_correct_option_var = tk.StringVar()
        option_labels = ["A", "B", "C", "D"]

        tk.Label(self.student_create_win, text="Options:", font=("Arial", 12, "bold"), bg=BG_COLOR).pack(pady=(10, 5))
        for i, label_text in enumerate(option_labels):
            opt_frame = tk.Frame(self.student_create_win, bg=BG_COLOR)
            opt_frame.pack(fill="x", padx=20, pady=2)
            tk.Label(opt_frame, text=f"{label_text}.", bg=BG_COLOR).pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(opt_frame, width=60, bg=ENTRY_BG_COLOR,
                             highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2, bd=0)
            entry.pack(side=tk.LEFT, expand=True, fill="x")
            self.student_option_entries.append(entry)

            # Radiobutton for selecting correct answer
            rb = tk.Radiobutton(opt_frame, text="Correct", variable=self.student_correct_option_var, value=label_text,
                                bg=BG_COLOR, activebackground=BG_COLOR, selectcolor=BG_COLOR)
            rb.pack(side=tk.RIGHT, padx=5)

        # Navigation and Save Buttons
        nav_frame = tk.Frame(self.student_create_win, bg=BG_COLOR)
        nav_frame.pack(pady=20)

        # Save Current Question and Move Buttons
        prev_btn = tk.Button(nav_frame, text="Previous", width=10,
                             command=self._student_save_and_navigate_question_creation_form_prev,
                             bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                             bd=2, relief="groove", padx=10, pady=5)
        prev_btn.grid(row=0, column=0, padx=10)
        prev_btn.bind("<Enter>", self._on_button_enter)
        prev_btn.bind("<Leave>", self._on_button_leave)

        next_btn = tk.Button(nav_frame, text="Next", width=10,
                             command=self._student_save_and_navigate_question_creation_form_next,
                             bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                             bd=2, relief="groove", padx=10, pady=5)
        next_btn.grid(row=0, column=1, padx=10)
        next_btn.bind("<Enter>", self._on_button_enter)
        next_btn.bind("<Leave>", self._on_button_leave)

        finalize_btn = tk.Button(self.student_create_win, text="Finalize & Save Practice Questions", width=30,
                                 command=self._finalize_student_created_questions,
                                 bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                                 bd=2, relief="groove", padx=10, pady=5)
        finalize_btn.pack(pady=10)
        finalize_btn.bind("<Enter>", self._on_button_enter)
        finalize_btn.bind("<Leave>", self._on_button_leave)

        # Load data for the current question
        self._student_load_question_for_creation_editing()

    def _student_save_current_question_input(self):
        """Saves the input from the current student form into self.newly_created_questions (temp)."""
        q_text = self.student_q_entry.get("1.0", tk.END).strip()
        options = [entry.get().strip() for entry in self.student_option_entries]
        correct_opt_label = self.student_correct_option_var.get()

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
            messagebox.showerror("Error", "Could not determine correct answer from selected option.",
                                 parent=self.student_create_win)
            return False

        # Store in the temporary list used for creation
        self.newly_created_questions[self.current_student_q_index_creation] = {
            "question": q_text,
            "options": options,
            "answer": correct_answer_text
        }
        return True

    def _student_load_question_for_creation_editing(self):
        """Populates the student form with data for the current question being edited/viewed."""
        if self.current_student_q_index_creation < len(self.newly_created_questions):
            q_data = self.newly_created_questions[self.current_student_q_index_creation]
            self.student_q_entry.config(state=tk.NORMAL)
            self.student_q_entry.delete("1.0", tk.END)
            self.student_q_entry.insert("1.0", q_data["question"])

            for i, entry in enumerate(self.student_option_entries):
                entry.delete(0, tk.END)
                if i < len(q_data["options"]):
                    entry.insert(0, q_data["options"][i])

            if q_data["answer"]:
                try:
                    answer_index = q_data["options"].index(q_data["answer"])
                    self.student_correct_option_var.set(chr(ord('A') + answer_index))
                except ValueError:
                    self.student_correct_option_var.set("")
            else:
                self.student_correct_option_var.set("")
        self.student_q_entry.config(state=tk.NORMAL)
        for entry in self.student_option_entries:
            entry.config(state=tk.NORMAL)

    def _student_save_and_navigate_question_creation_form_next(self):
        """Saves current student practice question and moves to the next."""
        if self._student_save_current_question_input():
            if self.current_student_q_index_creation < self.num_student_questions_to_create - 1:
                self.current_student_q_index_creation += 1
                self._student_display_question_creation_form()
            else:
                messagebox.showinfo("End of Questions",
                                    "You have reached the last question. Click 'Finalize & Save Practice Questions' to save.",
                                    parent=self.student_create_win)

    def _student_save_and_navigate_question_creation_form_prev(self):
        """Saves current student practice question and moves to the previous."""
        if self._student_save_current_question_input():
            if self.current_student_q_index_creation > 0:
                self.current_student_q_index_creation -= 1
                self._student_display_question_creation_form()
            else:
                messagebox.showinfo("First Question", "You are already at the first question.",
                                    parent=self.student_create_win)

    def _finalize_student_created_questions(self):
        """Validates and saves all newly created student practice questions."""
        if not self._student_save_current_question_input():  # Save the last question being edited
            return

        if not self.newly_created_questions:
            messagebox.showwarning("No Questions", "No practice questions have been created to finalize.",
                                   parent=self.student_create_win)
            return

        for i, q_data in enumerate(self.newly_created_questions):
            if not q_data["question"] or any(not opt for opt in q_data["options"]) or not q_data["answer"]:
                messagebox.showerror("Validation Error",
                                     f"Practice Question {i + 1} is incomplete. Please fill in all fields for all questions.",
                                     parent=self.student_create_win)
                return

        # Append newly created questions to the student's main practice list
        self.student_practice_questions.extend(self.newly_created_questions)
        self._save_student_practice_questions_to_file()  # Save all student practice questions

        messagebox.showinfo("Practice Questions Saved",
                            f"Successfully saved {len(self.newly_created_questions)} practice questions!",
                            parent=self.student_create_win)
        self.student_create_win.destroy()  # Close creation window
        self.newly_created_questions = []  # Clear temporary list after saving

    def _cancel_student_question_creation(self):
        """Handles cancellation of student question creation, with confirmation."""
        if messagebox.askyesno("Cancel Creation",
                               "Are you sure you want to cancel practice question creation? Unsaved changes will be lost.",
                               parent=self.student_create_win):
            self.student_create_win.destroy()
            self.newly_created_questions = []  # Clear temporary list

    def start_quiz(self, quiz_type="main", quiz_data_override=None):
        """
        Initiates the quiz for the student.
        Args:
            quiz_type (str): "main" for lecturer's main quiz, "practice_my_questions" for student's own,
                             "external_practice" for a quiz loaded from file by student.
        """

        if quiz_type == "main":
            # For "main" quiz, if override is provided (from student_load_and_start_main_quiz), use it.
            # Otherwise, use the globally active quiz.
            quiz_to_use = quiz_data_override if quiz_data_override else self.active_quiz_data
            quiz_questions = quiz_to_use["questions"]
            quiz_title_display = quiz_to_use['title']
            quiz_time_limit = quiz_to_use['time_limit_minutes']
        elif quiz_type == "practice_my_questions":
            quiz_questions = self.student_practice_questions
            quiz_title_display = "My Practice Quiz"
            quiz_time_limit = 1  # Default time limit for student created questions
        elif quiz_type == "external_practice" and quiz_data_override:
            quiz_questions = quiz_data_override["questions"]
            quiz_title_display = quiz_data_override["title"]
            quiz_time_limit = quiz_data_override["time_limit_minutes"]
        else:
            messagebox.showerror("Quiz Error", "Invalid quiz type or missing quiz data.", parent=self.student_menu_win)
            return

        if not quiz_questions:
            if quiz_type == "main":
                messagebox.showwarning("No Questions",
                                       "No main quiz questions available. Please inform the lecturer or load a quiz.",
                                       parent=self.student_menu_win)
            elif quiz_type == "practice_my_questions":
                messagebox.showwarning("No Practice Questions", "You have not created any practice questions yet.",
                                       parent=self.student_menu_win)
            elif quiz_type == "external_practice":
                messagebox.showwarning("No Questions", "The selected external quiz has no valid questions.",
                                       parent=self.student_menu_win)
            return

        self.student_menu_win.destroy()  # Close student dashboard

        self.quiz_win = tk.Toplevel(self.root)
        self.quiz_win.title(f"Quiz: {quiz_title_display}")
        self.quiz_win.geometry("800x600")
        self.quiz_win.protocol("WM_DELETE_WINDOW", lambda: self.confirm_exit_quiz(self.quiz_win))
        self.quiz_win.config(bg=BG_COLOR)

        self.current_question = 0
        self.selected_answers = {}  # Reset answers for a new quiz
        self.quiz_questions_to_use = quiz_questions  # Store reference to which questions are being used

        # Timer setup
        self.timer_seconds = quiz_time_limit * 60  # Convert minutes to seconds
        self.timer_var = tk.StringVar()
        self.timer_label = tk.Label(self.quiz_win, textvariable=self.timer_var, font=("Arial", 12, "bold"), bg=BG_COLOR,
                                    fg="red")
        self.timer_label.pack(pady=10)

        self.quiz_title_label = tk.Label(self.quiz_win, text=f"Quiz: {quiz_title_display}", font=("Arial", 16, "bold"),
                                         bg=BG_COLOR)
        self.quiz_title_label.pack(pady=(0, 10))

        self.question_text_label = tk.Label(self.quiz_win, text="", wraplength=750, justify=tk.LEFT, font=("Arial", 12),
                                            bg=BG_COLOR)
        self.question_text_label.pack(pady=10, padx=20)

        self.radio_var = tk.StringVar()
        self.option_radiobuttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.quiz_win, text="", variable=self.radio_var, value="", wraplength=700,
                                justify=tk.LEFT, anchor="w",
                                font=("Arial", 10), bg=BG_COLOR, activebackground=BG_COLOR, selectcolor=BG_COLOR)
            rb.pack(pady=5, padx=30, fill="x")
            self.option_radiobuttons.append(rb)

        # Question Navigation Buttons (will be dynamic)
        self.nav_button_frame = tk.Frame(self.quiz_win, bg=BG_COLOR)
        self.nav_button_frame.pack(pady=10)
        self.question_nav_buttons = []  # To store references to individual question nav buttons

        # Initialize navigation buttons (placeholder, will be updated by update_question)
        self.create_question_navigation_buttons()

        nav_control_frame = tk.Frame(self.quiz_win, bg=BG_COLOR)
        nav_control_frame.pack(pady=20)

        prev_btn = tk.Button(nav_control_frame, text="Previous", width=10,
                             command=self.prev_question,
                             bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                             bd=2, relief="groove", padx=10, pady=5)
        prev_btn.grid(row=0, column=0, padx=10)
        prev_btn.bind("<Enter>", self._on_button_enter)
        prev_btn.bind("<Leave>", self._on_button_leave)

        next_btn = tk.Button(nav_control_frame, text="Next", width=10,
                             command=self.next_question,
                             bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                             bd=2, relief="groove", padx=10, pady=5)
        next_btn.grid(row=0, column=1, padx=10)
        next_btn.bind("<Enter>", self._on_button_enter)
        next_btn.bind("<Leave>", self._on_button_leave)

        submit_btn = tk.Button(nav_control_frame, text="Submit Quiz", width=15,
                               command=self.submit_quiz,
                               bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                               bd=2, relief="groove", padx=10, pady=5)
        submit_btn.grid(row=0, column=2, padx=10)
        submit_btn.bind("<Enter>", self._on_button_enter)
        submit_btn.bind("<Leave>", self._on_button_leave)

        self.update_question()
        self.start_timer()

        self.quiz_win.grab_set()
        self.root.wait_window(self.quiz_win)

    def create_question_navigation_buttons(self):
        """Creates or updates the navigation buttons for each question."""
        # Clear existing buttons
        for widget in self.nav_button_frame.winfo_children():
            widget.destroy()
        self.question_nav_buttons = []

        # Create new buttons for each question
        for i in range(len(self.quiz_questions_to_use)):
            btn = tk.Button(self.nav_button_frame, text=str(i + 1), width=3, height=1,
                            command=lambda idx=i: self.goto_question(idx),
                            bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                            bd=1, relief="groove", padx=5, pady=2)  # Smaller border for these small buttons
            btn.grid(row=0, column=i, padx=2, pady=2)
            btn.bind("<Enter>", self._on_button_enter)
            btn.bind("<Leave>", self._on_button_leave)
            self.question_nav_buttons.append(btn)
        self.update_navigation_button_colors()

    def update_navigation_button_colors(self):
        """Updates the colors of question navigation buttons based on answer status."""
        for i, btn in enumerate(self.question_nav_buttons):
            if i == self.current_question:
                # Ensure the current question button also has a hover effect
                btn.config(bg=CURRENT_QUESTION_COLOR, bd=2)  # Slightly thicker border for current
                # Store original bg to restore from on leave
                btn.hover_original_bg = CURRENT_QUESTION_COLOR
            elif i in self.selected_answers:  # Question has been answered
                btn.config(bg=ANSWERED_COLOR, bd=1)
                btn.hover_original_bg = ANSWERED_COLOR
            else:  # Question is unanswered
                btn.config(bg=UNANSWERED_COLOR, bd=1)
                btn.hover_original_bg = UNANSWERED_COLOR

            # Re-bind hover for dynamic color buttons to ensure correct original color is used
            # We'll need to modify _on_button_leave to use btn.hover_original_bg
            # For now, let's just make sure the config sets the base color.
            # The simple _on_button_enter/_on_button_leave will apply, potentially making
            # the nav buttons lose their specific state color on hover.

            # Alternative approach for colored buttons:
            # Create a separate hover function for nav buttons that checks their current state color
            # Or, modify _on_button_leave to reset to the color it *should* be based on state.
            # Let's modify _on_button_leave for this.

            # We need to make a slight adjustment to the _on_button_leave to account for
            # the state-based background color of navigation buttons.
            # For simplicity, I will modify the general _on_button_leave to check if
            # the button is a navigation button and reset its color based on its state.

            # If the user asks for more specific hover on nav buttons, we can refine this.
            # For now, the current _on_button_enter/_leave will apply, potentially making
            # the nav buttons lose their specific state color on hover.
            pass

    def goto_question(self, index):
        """Navigates to a specific question."""
        # Save current answer before navigating
        self._save_current_answer()
        self.current_question = index
        self.update_question()

    def update_question(self):
        """Displays the current question and its options."""
        if self.current_question < len(self.quiz_questions_to_use):
            q_data = self.quiz_questions_to_use[self.current_question]
            self.question_text_label.config(text=f"Question {self.current_question + 1}: {q_data['question']}")

            self.radio_var.set("")  # Clear previous selection
            for i, option_text in enumerate(q_data["options"]):
                self.option_radiobuttons[i].config(text=option_text, value=option_text)
                # If this question was previously answered, pre-select the answer
                if self.current_question in self.selected_answers and \
                        self.selected_answers[self.current_question] == option_text:
                    self.radio_var.set(option_text)
            self.update_navigation_button_colors()  # Update colors after question change
        else:
            messagebox.showwarning("End of Quiz", "No more questions.", parent=self.quiz_win)
            self.submit_quiz()

    def _save_current_answer(self):
        """Saves the student's selected answer for the current question."""
        selected_option = self.radio_var.get()
        if selected_option:  # Only save if an option is selected
            self.selected_answers[self.current_question] = selected_option
        else:  # If no option selected, ensure it's not marked as answered
            if self.current_question in self.selected_answers:
                del self.selected_answers[self.current_question]

    def next_question(self):
        """Moves to the next question."""
        self._save_current_answer()  # Save current answer before moving
        if self.current_question < len(self.quiz_questions_to_use) - 1:
            self.current_question += 1
            self.update_question()
        else:
            messagebox.showinfo("End of Quiz", "You have reached the last question. Click 'Submit Quiz' to finish.",
                                parent=self.quiz_win)

    def prev_question(self):
        """Moves to the previous question."""
        self._save_current_answer()  # Save current answer before moving
        if self.current_question > 0:
            self.current_question -= 1
            self.update_question()
        else:
            messagebox.showinfo("First Question", "You are at the first question.", parent=self.quiz_win)

    def start_timer(self):
        """Starts the quiz countdown timer."""
        if self.timer_running:  # Prevent multiple timers
            if self.timer_id:  # Cancel any existing timer to avoid duplicates
                self.quiz_win.after_cancel(self.timer_id)
            self.countdown()

    def countdown(self):
        """Updates the timer display and handles time-up condition."""
        if self.timer_seconds > 0 and self.timer_running:
            mins, secs = divmod(self.timer_seconds, 60)
            self.timer_var.set(f"Time Left: {mins:02}:{secs:02}")
            self.timer_seconds -= 1
            self.timer_id = self.quiz_win.after(1000, self.countdown)
        elif self.timer_seconds == 0 and self.timer_running:
            self.timer_running = False  # Stop the timer
            if self.timer_id:
                self.quiz_win.after_cancel(self.timer_id)  # Ensure timer is cancelled
            messagebox.showinfo("Time Up", "Time is up! Submitting quiz.", parent=self.quiz_win)
            self.submit_quiz()

    def submit_quiz(self):
        """Submits the quiz and displays results."""
        if self.timer_running and self.timer_id:
            self.quiz_win.after_cancel(self.timer_id)  # Stop the timer immediately on submit
            self.timer_running = False

        self._save_current_answer()  # Ensure the last question's answer is saved

        correct_answers = 0
        total_questions = len(self.quiz_questions_to_use)

        results_details = []  # To store details for the results window

        for i, q_data in enumerate(self.quiz_questions_to_use):
            question_text = q_data['question']
            correct_answer = q_data['answer']
            student_answer = self.selected_answers.get(i)

            is_correct = False
            if student_answer == correct_answer:
                correct_answers += 1
                is_correct = True

            results_details.append({
                "question_num": i + 1,
                "question": question_text,
                "correct_answer": correct_answer,
                "student_answer": student_answer if student_answer is not None else "Not Answered",
                "is_correct": is_correct
            })

        percentage_score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        self.quiz_win.destroy()  # Close the quiz window
        self.display_results(correct_answers, total_questions, percentage_score, results_details)

    def display_results(self, correct, total, percentage, details):
        """Displays the quiz results to the student."""
        results_win = tk.Toplevel(self.root)
        results_win.title("Quiz Results")
        results_win.geometry("700x600")
        results_win.protocol("WM_DELETE_WINDOW", lambda: self.return_to_role_selection(results_win))
        results_win.config(bg=BG_COLOR)

        tk.Label(results_win, text="Quiz Results", font=("Arial", 16, "bold"), bg=BG_COLOR).pack(pady=20)
        tk.Label(results_win, text=f"You answered {correct} out of {total} questions correctly.", font=("Arial", 12),
                 bg=BG_COLOR).pack(pady=5)
        tk.Label(results_win, text=f"Your overall score: {percentage:.2f}%", font=("Arial", 14, "bold"),
                 bg=BG_COLOR).pack(pady=10)

        # Detailed results
        results_text_area = scrolledtext.ScrolledText(results_win, wrap=tk.WORD, width=80, height=20,
                                                      font=("Arial", 10), bg=ENTRY_BG_COLOR,
                                                      highlightbackground=ENTRY_BORDER_COLOR, highlightthickness=2,
                                                      bd=0)
        results_text_area.pack(pady=10, padx=20, expand=True, fill="both")

        for detail in details:
            status = "CORRECT" if detail["is_correct"] else "INCORRECT"
            color_tag = "green_text" if detail["is_correct"] else "red_text"

            results_text_area.insert(tk.END, f"Question {detail['question_num']}: ", "bold")
            results_text_area.insert(tk.END, f"{detail['question']}\n")
            results_text_area.insert(tk.END, f"  Your Answer: {detail['student_answer']}\n")
            results_text_area.insert(tk.END, f"  Correct Answer: {detail['correct_answer']}\n")
            results_text_area.insert(tk.END, f"  Status: {status}\n\n", color_tag)

        results_text_area.tag_config("green_text", foreground="green")
        results_text_area.tag_config("red_text", foreground="red")
        results_text_area.config(state=tk.DISABLED)  # Make read-only

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
        """Confirms if the user wants to exit the quiz without submitting."""
        if self.timer_running:  # If timer is running, cancel it
            if self.timer_id:
                current_window.after_cancel(self.timer_id)
            self.timer_running = False

        if messagebox.askyesno("Exit Quiz", "Are you sure you want to exit the quiz? Your progress will be lost.",
                               parent=current_window):
            current_window.destroy()
            self.student_menu_dashboard()
        else:
            # If user cancels exit, restart the timer if it was running
            self.timer_running = True
            self.start_timer()  # Resume timer

    def return_to_role_selection(self, current_window):
        """Destroys the current window and re-displays the role selection window."""
        current_window.destroy()
        self.role_selection_window()


# This block ensures the application runs when the script is executed
if __name__ == "__main__":
    app = QuizApp()