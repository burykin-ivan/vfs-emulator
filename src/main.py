import tkinter as tk
from tkinter import messagebox
import os
import argparse
import shutil


class VFSNode:
    """Узел виртуальной файловой системы (файл или директория)."""

    def __init__(self, name, is_dir=True):
        self.name = name
        self.is_dir = is_dir
        self.children = {} if is_dir else None
        self.content = ""


class ShellEmulator:
    """Эмулятор командной оболочки с графическим интерфейсом."""

    def __init__(self, root, vfs_path, script_path):
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.vfs_name = os.path.basename(os.path.normpath(vfs_path))
        self.vfs_name = self.vfs_name if self.vfs_name else "vfs"

        self.current_path = "/"
        self.vfs_root = VFSNode("/")
        self.load_vfs()

        self.root.title(f"Эмулятор оболочки - {self.vfs_name}")
        self.root.geometry("800x600")

        self.output_text = tk.Text(
            root, height=20, width=80, state='disabled', bg="black", fg="white"
        )
        self.output_text.pack(pady=10, padx=10)

        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.entry_label = tk.Label(
            input_frame, text=f"{self.vfs_name}> ",
            font=("Courier", 10, "bold")
        )
        self.entry_label.pack(side=tk.LEFT)

        self.command_entry = tk.Entry(input_frame, font=("Courier", 10))
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.execute_command)
        self.command_entry.focus_set()

        self.print_output(f"--- Отладка: {self.vfs_path} | {self.script_path} ---")

        if self.script_path and os.path.exists(self.script_path):
            self.root.after(500, self.run_script)
        elif self.script_path:
            self.print_output(f"Ошибка: Скрипт {self.script_path} не найден.")

    def load_vfs(self):
        """Загрузка физической директории в память (без изменения диска)."""
        self.vfs_root = VFSNode("/")
        if not os.path.exists(self.vfs_path):
            msg = f"Ошибка: Директория VFS '{self.vfs_path}' не найдена."
            self.print_output(msg)
            return

        try:
            for root, _, files in os.walk(self.vfs_path):
                rel_path = os.path.relpath(root, self.vfs_path)
                current_node = self.vfs_root

                if rel_path != '.':
                    parts = rel_path.replace('\\', '/').split('/')
                    for part in parts:
                        if part not in current_node.children:
                            current_node.children[part] = VFSNode(part)
                        current_node = current_node.children[part]

                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                    except Exception:
                        content = "[Бинарный файл]"
                    current_node.children[f] = VFSNode(f, is_dir=False)
                    current_node.children[f].content = content
        except Exception as e:
            self.print_output(f"Ошибка загрузки VFS: {e}")

    def normalize_path(self, base, target):
        """Нормализация пути (обработка .. и .)."""
        if target.startswith('/'):
            full = target
        else:
            full = os.path.join(base, target)
        return os.path.normpath(full).replace('\\', '/')

    def get_node(self, path):
        """Поиск узла в памяти по указанному пути."""
        norm_path = self.normalize_path(self.current_path, path)
        if norm_path == '/':
            return self.vfs_root

        parts = norm_path.strip('/').split('/')
        current = self.vfs_root
        for part in parts:
            if current and current.is_dir and part in current.children:
                current = current.children[part]
            else:
                return None
        return current

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
            self.print_output(f"Ошибка чтения скрипта: {e}")

    def execute_command(self, event):
        """Обработка ввода пользователя."""
        cmd = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)
        if not cmd:
            return
        self.print_output(f"{self.entry_label.cget('text')}{cmd}")
        self.process_command(cmd)

    def process_command(self, cmd_line, is_script=False):
        """Парсинг и маршрутизация команд."""
        expanded = os.path.expandvars(cmd_line)
        parts = expanded.split()
        cmd = parts[0]
        args = parts[1:]

        if cmd == "exit":
            self.root.quit()
            return True
        elif cmd == "ls":
            return self.cmd_ls(args)
        elif cmd == "cd":
            return self.cmd_cd(args)
        elif cmd == "vfs-init":
            return self.cmd_vfs_init()
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

    def cmd_ls(self, args):
        """Логика команды ls (работает только с VFS в памяти)."""
        target = args[0] if args else self.current_path
        node = self.get_node(target)
        if not node:
            self.print_output(f"ls: {target}: Нет такого файла или каталога")
            return False
        if not node.is_dir:
            self.print_output(node.name)
            return True

        for name, child in sorted(node.children.items()):
            suffix = "/" if child.is_dir else ""
            self.print_output(f"{name}{suffix}")
        return True

    def cmd_cd(self, args):
        """Логика команды cd (работает только с VFS в памяти)."""
        target = args[0] if args else "/"
        node = self.get_node(target)
        if not node:
            self.print_output(f"cd: {target}: Нет такого файла или каталога")
            return False
        if not node.is_dir:
            self.print_output(f"cd: {target}: Не является каталогом")
            return False

        self.current_path = self.normalize_path(self.current_path, target)
        self.entry_label.config(text=f"{self.vfs_name}:{self.current_path}> ")
        return True

    def cmd_vfs_init(self):
        """Сброс VFS к состоянию по умолчанию и очистка диска."""
        self.current_path = "/"
        self.vfs_root = VFSNode("/")
        self.entry_label.config(text=f"{self.vfs_name}:/ > ")

        if os.path.exists(self.vfs_path):
            try:
                shutil.rmtree(self.vfs_path)
                os.makedirs(self.vfs_path)
                self.print_output("Физическая директория очищена.")
            except Exception as e:
                self.print_output(f"Ошибка очистки диска: {e}")

        self.print_output("VFS сброшена к состоянию по умолчанию.")
        return True


def parse_args():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument("--vfs", type=str, default="tests/vfs_minimal")
    parser.add_argument("--script", type=str, default="")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    root = tk.Tk()
    app = ShellEmulator(root, args.vfs, args.script)
    root.mainloop()
