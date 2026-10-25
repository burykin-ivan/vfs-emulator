import tkinter as tk
from tkinter import messagebox
import os
import argparse

class ShellEmulator:
    """Эмулятор оболочки с графическим интерфейсом."""

    def __init__(self, root, vfs_path, script_path):
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.vfs_name = os.path.basename(os.path.normpath(vfs_path)) if vfs_path else "vfs"
        
        self.root.title(f"Эмулятор оболочки - {self.vfs_name}")
        self.root.geometry("800x600")

        self.output_text = tk.Text(root, height=20, width=80, state='disabled', bg="black", fg="white")
        self.output_text.pack(pady=10, padx=10)

        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.entry_label = tk.Label(input_frame, text=f"{self.vfs_name}> ", font=("Courier", 10, "bold"))
        self.entry_label.pack(side=tk.LEFT)

        self.command_entry = tk.Entry(input_frame, font=("Courier", 10))
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.execute_command)
        self.command_entry.focus_set()

        self.print_output("--- Отладка ---")
        self.print_output(f"Путь к VFS: {self.vfs_path}")
        self.print_output(f"Путь к скрипту: {self.script_path}")
        self.print_output("---------------")

        if self.script_path:
            if os.path.exists(self.script_path):
                self.root.after(500, self.run_script)
            else:
                self.print_output(f"Ошибка: Скрипт {self.script_path} не найден.")

    def print_output(self, text):
        """Вывод текста в консольное окно."""
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.config(state='disabled')
        self.output_text.see(tk.END)

    def run_script(self):
        """Выполнение команд из стартового скрипта."""
        self.print_output(f"--- Выполнение скрипта: {self.script_path} ---")
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                for line in f:
                    cmd = line.strip()
                    if not cmd or cmd.startswith('#'):
                        continue
                    
                    self.print_output(f"Скрипт> {cmd}")
                    if not self.process_command(cmd, is_script=True):
                        self.print_output("Остановка: ошибка в скрипте.")
                        break
        except Exception as e:
            self.print_output(f"Ошибка чтения: {e}")
        self.print_output("--- Скрипт завершен ---")

    def execute_command(self, event):
        """Обработка ввода пользователя."""
        cmd = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)
        
        if not cmd:
            return
            
        self.print_output(f"{self.entry_label.cget('text')}{cmd}")
        self.process_command(cmd)

    def process_command(self, cmd_line, is_script=False):
        """Разбор и выполнение команды."""
        expanded = os.path.expandvars(cmd_line)
        parts = expanded.split()
        cmd = parts[0]
        args = parts[1:]

        if cmd == "exit":
            self.root.quit()
            return True
        elif cmd in ["ls", "cd"]:
            self.print_output(f"[Заглушка] {cmd} {args}")
            return True
        elif cmd == "conf-dump":
            self.print_output(f"vfs_path={self.vfs_path}")
            self.print_output(f"script_path={self.script_path}")
            return True
        else:
            err = f"Команда не найдена: {cmd}"
            if not is_script:
                messagebox.showerror("Ошибка", err)
            self.print_output(f"Ошибка: {err}")
            return False

def parse_args():
    """Парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--vfs", type=str, default="./vfs_data")
    parser.add_argument("--script", type=str, default="")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    root = tk.Tk()
    app = ShellEmulator(root, args.vfs, args.script)
    root.mainloop()
