import tkinter as tk
from tkinter import ttk, messagebox, font
import webbrowser

class AmmoCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор ленты ПКТ для МОГ")
        self.root.geometry("380x480")
        self.root.resizable(False, False)
        
        #
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (380 // 2)
        y = (self.root.winfo_screenheight() // 2) - (480 // 2)
        self.root.geometry(f"380x480+{x}+{y}")
        
        # Основной контейнер
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        self.create_widgets(main_frame)
    
    def create_widgets(self, parent):
        # Заголовок
        title = tk.Label(parent, text="Расчёт ленты ПКТ для МОГ", 
                        font=("Arial", 13, "bold"))
        title.pack(pady=(0, 15))
        
        # Фрейм ввода
        input_frame = tk.LabelFrame(parent, text="Ввод", font=("Arial", 10, "bold"))
        input_frame.pack(pady=(0, 15), fill="x")
        
        i_frame = tk.Frame(input_frame, padx=15, pady=12)
        i_frame.pack()
        
        # Номер отрезка
        tk.Label(i_frame, text="Отрезок (1-10):", 
                font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=8)
        self.segment_var = tk.StringVar()
        self.segment_entry = tk.Entry(i_frame, textvariable=self.segment_var, 
                                    width=8, font=("Arial", 11), justify="center")
        self.segment_entry.grid(row=0, column=1, pady=8)
        
        # Оставшиеся патроны
        tk.Label(i_frame, text="Осталось:", 
                font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=8)
        self.remaining_var = tk.StringVar()
        self.remaining_entry = tk.Entry(i_frame, textvariable=self.remaining_var, 
                                      width=8, font=("Arial", 11), justify="center")
        self.remaining_entry.grid(row=1, column=1, pady=8)
        
        # Кнопки РАСЧИТАТЬ и СБРОСИТЬ
        btn_frame = tk.Frame(i_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        self.calc_btn = tk.Button(btn_frame, text="РАСЧИТАТЬ", command=self.calculate, 
                                bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), 
                                width=11, height=2, relief="flat", bd=0)
        self.calc_btn.pack(side="left", padx=5)
        
        self.reset_btn = tk.Button(btn_frame, text="СБРОСИТЬ", command=self.reset, 
                                 bg="#f44336", fg="white", font=("Arial", 11, "bold"), 
                                 width=11, height=2, relief="flat", bd=0)
        self.reset_btn.pack(side="left", padx=5)
        
        # Результат (только чтение)
        result_frame = tk.LabelFrame(parent, text="Результат", font=("Arial", 10, "bold"))
        result_frame.pack(fill="both", expand=True)
        
        self.result_text = tk.Text(result_frame, height=12, width=38, 
                                 font=("Consolas", 10), wrap="none", state="disabled")
        scrollbar = tk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Нижняя информация
        info_frame = tk.Frame(parent)
        info_frame.pack(pady=5)
        
        # Telegram
        telegram_font = font.Font(family="Arial", size=9, weight="bold")
        telegram_btn = tk.Label(info_frame, text="Telegram автора", 
                               font=telegram_font, fg="#1DA1F2", cursor="hand2")
        telegram_btn.pack()
        telegram_btn.bind("<Button-1>", lambda e: self.open_telegram())
        
        # Информация
        info_label = tk.Label(info_frame, text="250 патронов (Т>БР>ЛПС)", 
                            font=("Arial", 8), fg="gray50")
        info_label.pack(pady=(2, 0))
        
        # Enter
        self.root.bind('<Return>', lambda e: self.calculate())
    
    def open_telegram(self):
        webbrowser.open("https://t.me/wtfneponn")
    
    def reset(self):
        self.segment_var.set("")
        self.remaining_var.set("")
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")
    
    def get_ammo_type(self, position):
        cycle = (position - 1) % 3
        if cycle == 0: return "Т"
        elif cycle == 1: return "БР"
        else: return "ЛПС"
    
    def count_ammo_by_position(self, total_used):
        t = total_used // 3 + (1 if total_used % 3 >= 1 else 0)
        br = total_used // 3 + (1 if total_used % 3 >= 2 else 0)
        lps = total_used // 3
        return t, br, lps
    
    def calculate(self):
        try:
            segment = int(self.segment_var.get())
            remaining = int(self.remaining_var.get())
            
            if not (1 <= segment <= 10):
                messagebox.showerror("Ошибка", "Отрезок: 1-10")
                return
            if not (0 <= remaining <= 25):
                messagebox.showerror("Ошибка", "Патроны: 0-25")
                return
            
            used_in_segment = 25 - remaining
            total_used = (segment - 1) * 25 + used_in_segment
            
            last_fired = self.get_ammo_type(total_used) if total_used > 0 else "-"
            next_pos = total_used + 1
            next_type = self.get_ammo_type(next_pos) if remaining > 0 else "-"
            
            t_used, br_used, lps_used = self.count_ammo_by_position(total_used)
            
            report = f"""Отрезок:           {segment:2d}
Осталось:          {remaining:2d}
В отрезке:         {used_in_segment:2d}

Всего:             {total_used:3d}/250
Ленте осталось:    {250-total_used:3d}

Последний:         {last_fired}
Следующий:         {next_type}

T:  {t_used:3d}
БР: {br_used:3d}
ЛПС:{lps_used:3d}"""
            
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, report)
            self.result_text.config(state="disabled")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Только числа!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AmmoCalculator(root)
    root.mainloop()