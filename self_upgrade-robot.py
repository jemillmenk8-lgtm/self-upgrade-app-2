import os
import subprocess
import requests
from pathlib import Path
import importlib.util
from queue import Queue
import threading
import time

class SelfUpgradeRobot:
    def _init_(self, skills_folder="skills"):
        self.skills_folder = Path(skills_folder)
        self.skills_folder.mkdir(exist_ok=True)
        self.loaded_modules = {}
        self.task_queue = Queue()
        self.processing = False

    # ===== Install libraries =====
    def install_library(self, library_name):
        try:
            subprocess.check_call([os.sys.executable, "-m", "pip", "install", library_name])
            print(f"[✅] Library '{library_name}' installed successfully!")
        except Exception as e:
            print(f"[❌] Failed to install '{library_name}': {e}")

    # ===== Download feature =====
    def download_feature(self, url, filename):
        try:
            response = requests.get(url)
            file_path = self.skills_folder / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"[✅] Feature '{filename}' downloaded successfully!")
        except Exception as e:
            print(f"[❌] Failed to download '{filename}': {e}")

    # ===== Add/load feature =====
    def add_feature(self, filename):
        try:
            file_path = self.skills_folder / filename
            if file_path.exists():
                module_name = filename.replace(".py", "")
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.loaded_modules[module_name] = module
                print(f"[✅] Feature '{filename}' loaded successfully!")
                return module
            else:
                print(f"[❌] Feature '{filename}' not found.")
        except Exception as e:
            print(f"[❌] Failed to add feature '{filename}': {e}")

    # ===== Run a feature =====
    def run_feature(self, module_name, function_name="run", *args, **kwargs):
        module = self.loaded_modules.get(module_name)
        if module and hasattr(module, function_name):
            func = getattr(module, function_name)
            print(f"[⚡] Running {module_name}.{function_name}...")
            return func(*args, **kwargs)
        else:
            print(f"[❌] Module '{module_name}' or function '{function_name}' not found.")

    # ===== Self-update =====
    def self_update(self, repo_url):
        try:
            os.system(f"git clone {repo_url} temp_update")
            os.system("cp -r temp_update/* .")  # Linux/Mac
            os.system("rm -rf temp_update")
            print(f"[✅] Robot updated from {repo_url}!")
        except Exception as e:
            print(f"[❌] Self-update failed: {e}")

    # ===== Task Queue System =====
    def add_task(self, module_name, function_name="run", *args, **kwargs):
        task = {"module": module_name, "function": function_name, "args": args, "kwargs": kwargs}
        self.task_queue.put(task)
        print(f"[📝] Task added: {module_name}.{function_name}")

        # Start processing if not already running
        if not self.processing:
            threading.Thread(target=self._process_tasks, daemon=True).start()

    def _process_tasks(self):
        self.processing = True
        while not self.task_queue.empty():
            task = self.task_queue.get()
            self.run_feature(task["module"], task["function"], *task["args"], **task["kwargs"])
            self.task_queue.task_done()
            time.sleep(1)  # Optional delay between tasks
        self.processing = False