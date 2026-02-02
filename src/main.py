import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import sys
import threading # For running Firebase commands in a separate thread

# --- Firebase CLI Automation Functions (adapted from previous script) ---

def run_firebase_command(command_args, cwd=None, check_success=True, capture_output=False, input_data=None, output_widget=None):
    """
    Runs a Firebase CLI command using subprocess and redirects output to a Tkinter Text widget.

    Args:
        command_args (list): A list of strings representing the command and its arguments.
        cwd (str, optional): The current working directory for the command.
        check_success (bool): If True, raises an exception if the command returns a non-zero exit code.
        capture_output (bool): If True, captures stdout and stderr and returns them.
                               Otherwise, output goes directly to the Tkinter widget.
        input_data (str, optional): String to be sent as input to the subprocess (e.g., for prompts).
        output_widget (tk.scrolledtext.ScrolledText): The widget to which output should be redirected.
    
    Returns:
        tuple: (stdout, stderr) if capture_output is True, otherwise None.
    """
    def write_to_widget(text, tag=None):
        if output_widget:
            output_widget.insert(tk.END, text)
            if tag:
                output_widget.tag_add(tag, output_widget.index(tk.END + f"-{len(text)}c"), tk.END)
            output_widget.see(tk.END) # Auto-scroll

    try:
        write_to_widget(f"\n--- Running command: {' '.join(command_args)} ---\n", "info")
        
        process = subprocess.Popen(
            command_args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True if sys.platform == "win32" else False,
            stdin=subprocess.PIPE if input_data else None
        )

        if input_data:
            process.stdin.write(input_data)
            process.stdin.flush()

        stdout_lines = []
        stderr_lines = []

        # Read output line by line to update GUI in real-time
        for line in iter(process.stdout.readline, ''):
            write_to_widget(line, "normal")
            stdout_lines.append(line)
        for line in iter(process.stderr.readline, ''):
            write_to_widget(line, "error")
            stderr_lines.append(line)

        process.stdout.close()
        process.stderr.close()
        return_code = process.wait()

        if check_success and return_code != 0:
            error_message = f"ERROR: Command '{' '.join(command_args)}' failed with exit code {return_code}.\n"
            write_to_widget(error_message, "error")
            write_to_widget("STDOUT:\n" + "".join(stdout_lines), "error")
            write_to_widget("STDERR:\n" + "".join(stderr_lines), "error")
            raise subprocess.CalledProcessError(return_code, command_args, "".join(stdout_lines), "".join(stderr_lines))
        
        write_to_widget(f"INFO: Command '{' '.join(command_args)}' completed with exit code {return_code}.\n", "info")
        if capture_output:
            return "".join(stdout_lines), "".join(stderr_lines)

    except FileNotFoundError:
        write_to_widget("ERROR: The command was not found. This might mean Node.js/npm or Firebase CLI is not installed or not in your system's PATH.\n", "error")
        raise
    except subprocess.CalledProcessError as e:
        # Error details already written by write_to_widget inside this block
        raise
    except Exception as e:
        write_to_widget(f"An unexpected error occurred: {e}\n", "error")
        raise

# --- Main Tkinter GUI Class ---
class FirebaseAutomationGUI:
    def __init__(self, master):
        self.master = master
        master.title("Firebase Automation Tool")
        master.geometry("800x600") # Default window size
        master.resizable(True, True)

        # Configure grid weights for responsive layout
        master.grid_rowconfigure(0, weight=0) # Input frame row
        master.grid_rowconfigure(1, weight=1) # Output area row
        master.grid_columnconfigure(0, weight=1) # Main column

        # --- Input Frame ---
        self.input_frame = tk.LabelFrame(master, text="Firebase Project Configuration", padx=10, pady=10)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.input_frame.grid_columnconfigure(1, weight=1) # Make entry columns expand

        tk.Label(self.input_frame, text="Project ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.project_id_entry = tk.Entry(self.input_frame, width=50)
        self.project_id_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        self.project_id_entry.insert(0, "your-firebase-project-id") # Placeholder

        tk.Label(self.input_frame, text="Public Directory:").grid(row=1, column=0, sticky="w", pady=5)
        self.public_dir_entry = tk.Entry(self.input_frame, width=50)
        self.public_dir_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        self.public_dir_entry.insert(0, "public") # Default public directory
        
        self.browse_button = tk.Button(self.input_frame, text="Browse", command=self._browse_public_dir)
        self.browse_button.grid(row=1, column=2, sticky="e", padx=5)

        # --- Action Buttons ---
        self.button_frame = tk.Frame(self.input_frame)
        self.button_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.login_button = tk.Button(self.button_frame, text="1. Firebase Login", command=self._run_firebase_login)
        self.login_button.pack(side="left", padx=5)

        self.init_button = tk.Button(self.button_frame, text="2. Init Hosting", command=self._run_firebase_init_hosting)
        self.init_button.pack(side="left", padx=5)

        self.deploy_button = tk.Button(self.button_frame, text="3. Deploy Hosting", command=self._run_firebase_deploy)
        self.deploy_button.pack(side="left", padx=5)

        # New: Install Firebase CLI Button
        self.install_cli_button = tk.Button(self.button_frame, text="4. Install Firebase CLI", command=self._run_firebase_install)
        self.install_cli_button.pack(side="left", padx=5)


        # --- Output Area (ScrolledText for logs) ---
        self.output_label = tk.Label(master, text="Firebase CLI Output:")
        self.output_label.grid(row=1, column=0, sticky="nw", padx=10, pady=(0, 5))

        self.output_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=15, width=80)
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(20, 10)) # Adjust pady to make space for label

        # Configure tags for output styling
        self.output_text.tag_config("info", foreground="blue")
        self.output_text.tag_config("error", foreground="red", font=("TkDefaultFont", 9, "bold"))
        self.output_text.tag_config("normal", foreground="black") # Default text color

        self._print_initial_message()

    def _print_initial_message(self):
        self.output_text.insert(tk.END, "Welcome to Firebase Automation Tool!\n", "info")
        self.output_text.insert(tk.END, "IMPORTANT: For this tool to work, Node.js and npm must be installed, and Firebase CLI (firebase-tools) must be installed globally.\n", "error")
        self.output_text.insert(tk.END, "If 'firebase' command is not recognized, click '4. Install Firebase CLI'.\n\n", "error")
        self.output_text.insert(tk.END, "1. Log in to Firebase CLI.\n", "normal")
        self.output_text.insert(tk.END, "2. Initialize Hosting (will prompt for project if not set, and public directory).\n", "normal")
        self.output_text.insert(tk.END, "3. Deploy your project to Firebase Hosting.\n", "normal")
        self.output_text.see(tk.END)

    def _browse_public_dir(self):
        """Allows the user to select a directory for public content."""
        selected_directory = filedialog.askdirectory(parent=self.master,
                                                     initialdir=self.public_dir_entry.get() or os.getcwd(),
                                                     title="Select Public Directory")
        if selected_directory:
            self.public_dir_entry.delete(0, tk.END)
            self.public_dir_entry.insert(0, selected_directory)
            self._log_message(f"INFO: Public directory selected: {selected_directory}\n", "info")
        else:
            self._log_message("INFO: Public directory selection cancelled.\n", "info")

    def _log_message(self, message, tag="normal"):
        """Helper to insert messages into the ScrolledText widget."""
        self.output_text.insert(tk.END, message, tag)
        self.output_text.see(tk.END)

    def _run_command_in_thread(self, target_function, *args, **kwargs):
        """Runs a given function in a separate thread to keep GUI responsive."""
        # Disable buttons while command is running
        self._set_buttons_state(tk.DISABLED)
        
        thread = threading.Thread(target=target_function, args=args, kwargs=kwargs)
        thread.daemon = True # Allow the main program to exit even if thread is running
        thread.start()
        # Re-enable buttons after a short delay (or when thread finishes, more complex)
        # For simplicity, re-enable after thread starts. A more robust solution
        # would involve thread completion callbacks.
        self.master.after(100, lambda: self._check_thread_completion(thread))

    def _check_thread_completion(self, thread):
        if thread.is_alive():
            self.master.after(100, lambda: self._check_thread_completion(thread))
        else:
            self._set_buttons_state(tk.NORMAL)
            self._log_message("INFO: Command thread finished.\n", "info")


    def _set_buttons_state(self, state):
        self.login_button.config(state=state)
        self.init_button.config(state=state)
        self.deploy_button.config(state=state)
        self.browse_button.config(state=state)
        self.install_cli_button.config(state=state) # New: Manage state of install button

    def _run_firebase_login(self):
        def login_task():
            try:
                self._log_message("INFO: Attempting Firebase login. Please follow browser prompts.\n", "info")
                run_firebase_command(['firebase', 'login'], output_widget=self.output_text)
                self._log_message("INFO: Firebase login successful!\n", "info")
            except subprocess.CalledProcessError as e:
                error_output = self.output_text.get("1.0", tk.END)
                if "not recognized as an internal or external command" in error_output or "command not found" in error_output:
                    self._log_message("ERROR: 'firebase' command not found. Please ensure Firebase CLI is installed and added to your system's PATH.\n", "error")
                    self._log_message("Consider clicking '4. Install Firebase CLI' if Node.js/npm is already installed.\n", "error")
                    self._log_message("Refer to Firebase CLI installation guide: https://firebase.google.com/docs/cli#install_the_firebase_cli\n", "error")
                else:
                    self._log_message(f"ERROR: Firebase login failed with exit code {e.returncode}.\n", "error")
            except Exception as e:
                self._log_message(f"ERROR: An unexpected error occurred during login: {e}\n", "error")
        self._run_command_in_thread(login_task)

    def _run_firebase_init_hosting(self):
        project_id = self.project_id_entry.get().strip()
        public_dir = self.public_dir_entry.get().strip()

        if not project_id:
            messagebox.showerror("Input Error", "Please enter a Firebase Project ID.")
            self._log_message("ERROR: Firebase Project ID not provided for initialization.\n", "error")
            return
        if not public_dir:
            messagebox.showerror("Input Error", "Please enter a Public Directory.")
            self._log_message("ERROR: Public Directory not provided for initialization.\n", "error")
            return

        def init_task():
            try:
                self._log_message(f"INFO: Initializing Firebase Hosting for project '{project_id}' in directory '{public_dir}'...\n", "info")
                self._log_message("NOTE: This command might still require interactive input in the console for some prompts (e.g., single-page app, GitHub setup).\n", "info")
                
                run_firebase_command(['firebase', 'use', project_id], output_widget=self.output_text)
                
                init_command = ['firebase', 'init', 'hosting', '--project', project_id, '--public', public_dir, '--confirm']
                run_firebase_command(init_command, output_widget=self.output_text)
                
                self._log_message("INFO: Firebase Hosting initialization process completed.\n", "info")
                self._log_message("Please check the console for any remaining interactive prompts.\n", "info")
            except subprocess.CalledProcessError as e:
                error_output = self.output_text.get("1.0", tk.END)
                if "not recognized as an internal or external command" in error_output or "command not found" in error_output:
                    self._log_message("ERROR: 'firebase' command not found. Please ensure Firebase CLI is installed and added to your system's PATH.\n", "error")
                    self._log_message("Consider clicking '4. Install Firebase CLI' if Node.js/npm is already installed.\n", "error")
                    self._log_message("Refer to Firebase CLI installation guide: https://firebase.google.com/docs/cli#install_the_firebase_cli\n", "error")
                else:
                    self._log_message(f"ERROR: Firebase Hosting initialization failed with exit code {e.returncode}.\n", "error")
            except Exception as e:
                self._log_message(f"ERROR: An unexpected error occurred during initialization: {e}\n", "error")
        self._run_command_in_thread(init_task)

    def _run_firebase_deploy(self):
        project_id = self.project_id_entry.get().strip()
        public_dir = self.public_dir_entry.get().strip()

        if not public_dir:
             messagebox.showerror("Input Error", "Public Directory is required to determine deployment source.")
             self._log_message("ERROR: Public Directory not specified for deployment.\n", "error")
             return

        project_root = os.path.dirname(public_dir) if os.path.isabs(public_dir) and "firebase.json" in os.listdir(os.path.dirname(public_dir)) else os.getcwd()
        if not os.path.exists(os.path.join(project_root, 'firebase.json')):
            messagebox.showwarning("Warning", "firebase.json not found in the inferred project root. Deployment might fail. Ensure 'firebase init' was run correctly.")
            self._log_message("WARNING: firebase.json not found in inferred project root. Deployment might fail.\n", "error")


        def deploy_task():
            try:
                self._log_message(f"INFO: Deploying to Firebase Hosting...\n", "info")
                command = ['firebase', 'deploy', '--only', 'hosting']
                if project_id:
                    command.extend(['--project', project_id])
                    self._log_message(f"INFO: Deploying to explicit project: {project_id}\n", "info")
                else:
                    self._log_message("INFO: Deploying to project linked in .firebaserc (current directory).\n", "info")

                run_firebase_command(command, cwd=project_root, output_widget=self.output_text)
                self._log_message("INFO: Deployment to Firebase Hosting successful!\n", "info")
            except subprocess.CalledProcessError as e:
                error_output = self.output_text.get("1.0", tk.END)
                if "not recognized as an internal or external command" in error_output or "command not found" in error_output:
                    self._log_message("ERROR: 'firebase' command not found. Please ensure Firebase CLI is installed and added to your system's PATH.\n", "error")
                    self._log_message("Consider clicking '4. Install Firebase CLI' if Node.js/npm is already installed.\n", "error")
                    self._log_message("Refer to Firebase CLI installation guide: https://firebase.google.com/docs/cli#install_the_firebase_cli\n", "error")
                else:
                    self._log_message(f"ERROR: Firebase deployment failed with exit code {e.returncode}. Ensure 'firebase init' was run in the project directory and you are logged in.\n", "error")
            except Exception as e:
                self._log_message(f"ERROR: An unexpected error occurred during deployment: {e}\n", "error")
        self._run_command_in_thread(deploy_task)

    def _run_firebase_install(self):
        """Attempts to install Firebase CLI globally using npm."""
        def install_task():
            self._log_message("INFO: Attempting to install Firebase CLI globally via npm...\n", "info")
            self._log_message("NOTE: This requires Node.js and npm to be installed and accessible in your PATH.\n", "info")
            self._log_message("You might need to run this Python script with administrator/root privileges if installation fails due to permissions.\n", "info")
            try:
                # Check if npm is available first
                subprocess.run(['npm', '--version'], check=True, capture_output=True, text=True, shell=True if sys.platform == "win32" else False)
                self._log_message("INFO: npm found. Proceeding with Firebase CLI installation.\n", "info")
                run_firebase_command(['npm', 'install', '-g', 'firebase-tools'], output_widget=self.output_text)
                self._log_message("INFO: Firebase CLI installation completed successfully!\n", "info")
                self._log_message("Please restart this application or your terminal for PATH changes to take effect if you were prompted to add npm to PATH.\n", "info")
            except FileNotFoundError:
                self._log_message("ERROR: 'npm' command not found. Please install Node.js (which includes npm) from https://nodejs.org/ and ensure it's in your PATH.\n", "error")
            except subprocess.CalledProcessError as e:
                self._log_message(f"ERROR: Firebase CLI installation failed with exit code {e.returncode}.\n", "error")
                self._log_message("This often indicates a permissions issue even when running as administrator. Please try the following:\n", "error")
                self._log_message("  1. Open a NEW command prompt/terminal AS ADMINISTRATOR/ROOT.\n", "error")
                self._log_message("  2. Manually run: npm install -g firebase-tools\n", "error")
                self._log_message("  3. If that fails, try clearing npm cache: npm cache clean --force\n", "error")
                self._log_message("  4. Then retry 'npm install -g firebase-tools'.\n", "error")
                self._log_message("  5. Refer to Firebase CLI installation guide for more details: https://firebase.google.com/docs/cli#install_the_firebase_cli\n", "error")
            except Exception as e:
                self._log_message(f"ERROR: An unexpected error occurred during installation: {e}\n", "error")
        self._run_command_in_thread(install_task)


# --- Main execution block ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FirebaseAutomationGUI(root)
    root.mainloop()
