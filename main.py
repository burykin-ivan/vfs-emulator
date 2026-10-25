import tkinter as tk
from tkinter import messagebox
import os

class ShellEmulator:
    """Класс для графического эмулятора оболочки."""
    
    def __init__(self, root, vfs_name):
        """Инициализация окна и компонентов интерфейса."""
        self.root = root
        self.vfs_name = vfs_name
        
        # Настройка главного окна
        self.root.title(f"Эмулятор оболочки - {self.vfs_name}")
        self.root.geometry("600x400")

        # Поле вывода
        self.output_text = tk.Text(root, height=15, width=70, state='disabled', bg="black", fg="white")
        self.output_text.pack(pady=10, padx=10)

        # Рамка для ввода
        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.entry_label = tk.Label(input_frame, text=f"{self.vfs_name}> ", font=("Courier", 10, "bold"))
        self.entry_label.pack(side=tk.LEFT)

        self.command_entry = tk.Entry(input_frame, font=("Courier", 10))
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.execute_command)
        self.command_entry.focus_set()

    def print_output(self, text):
        """Вывод текста в консольное окно."""
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.config(state='disabled')
        self.output_text.see(tk.END)

    def execute_command(self, event):
        """Обработка введенной команды."""
        command_line = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)

        if not command_line:
            return

        # Требование 3: Раскрытие переменных окружения (например, $HOME)
        expanded_line = os.path.expandvars(command_line)
        self.print_output(f"{self.entry_label.cget('text')}{command_line}")

        parts = expanded_line.split()
        command = parts[0]
        args = parts[1:]

        # Требование 6: Команда exit
        if command == "exit":
            self.root.quit()
            
        # Требование 4: Заглушки ls и cd
        elif command in ["ls", "cd"]:
            self.print_output(f"[Заглушка] Команда: '{command}', Аргументы: {args}")
            
        # Требование 4: Сообщение об ошибке
        else:
            messagebox.showerror("Ошибка", f"Команда не найдена: {command}")
            self.print_output(f"Ошибка: неизвестная команда '{command}'")

def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = ShellEmulator(root, "my_vfs")
    root.mainloop()

if __name__ == "__main__":
    main()
