import tkinter as tk
from tkinter import ttk, messagebox
import time
import pygame
import threading
from settings import Settings
from datetime import datetime, timedelta
from plyer import notification

class SettingsWindow:
    def __init__(self, parent, settings, main_app):
        self.settings = settings
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("500x400")  # Уменьшаем высоту окна
        self.window.resizable(False, False)
        
        # Создаем основной фрейм с отступами
        self.frame = ttk.Frame(self.window, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Настройки таймера
        timer_settings_frame = ttk.LabelFrame(self.frame, text="Настройки времени", padding="10")
        timer_settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Время работы
        ttk.Label(timer_settings_frame, text="Время работы (мин):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.work_time_var = tk.StringVar(value=str(self.settings.settings["work_time"] // 60))
        ttk.Entry(timer_settings_frame, textvariable=self.work_time_var, width=5).grid(row=0, column=1, padx=5, pady=5)
        
        # Время перерыва
        ttk.Label(timer_settings_frame, text="Время перерыва (мин):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.break_time_var = tk.StringVar(value=str(self.settings.settings["break_time"] // 60))
        ttk.Entry(timer_settings_frame, textvariable=self.break_time_var, width=5).grid(row=1, column=1, padx=5, pady=5)
        
        # Длинный перерыв
        ttk.Label(timer_settings_frame, text="Длинный перерыв (мин):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.long_break_time_var = tk.StringVar(value=str(self.settings.settings["long_break_time"] // 60))
        ttk.Entry(timer_settings_frame, textvariable=self.long_break_time_var, width=5).grid(row=2, column=1, padx=5, pady=5)
        
        # Ежедневная цель
        ttk.Label(timer_settings_frame, text="Ежедневная цель:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.daily_goal_var = tk.StringVar(value=str(self.settings.settings["daily_goal"]))
        ttk.Entry(timer_settings_frame, textvariable=self.daily_goal_var, width=5).grid(row=3, column=1, padx=5, pady=5)
        
        # Кнопки управления внизу окна
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        # Стиль для кнопок
        self.style = ttk.Style()
        self.style.configure("Settings.TButton", font=("Arial", 10))
        
        # Кнопки управления (в обратном порядке для правильного отображения)
        ttk.Button(button_frame, text="Отмена", command=self.window.destroy, 
                  style="Settings.TButton", width=12).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Сохранить", command=self.save_settings, 
                  style="Settings.TButton", width=12).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Применить", command=self.apply_settings, 
                  style="Settings.TButton", width=12).pack(side=tk.RIGHT, padx=(0, 5))
        
    def apply_settings(self):
        try:
            self.settings.settings["work_time"] = int(self.work_time_var.get()) * 60
            self.settings.settings["break_time"] = int(self.break_time_var.get()) * 60
            self.settings.settings["long_break_time"] = int(self.long_break_time_var.get()) * 60
            self.settings.settings["daily_goal"] = int(self.daily_goal_var.get())
            
            # Обновляем настройки в основном окне
            self.main_app.update_settings()
            
            messagebox.showinfo("Успех", "Настройки применены!")
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа")
            
    def save_settings(self):
        self.apply_settings()  # Применяем настройки
        self.settings.save_settings()  # Сохраняем в файл
        self.window.destroy()  # Закрываем окно

class HistoryWindow:
    def __init__(self, parent, settings):
        self.settings = settings
        self.window = tk.Toplevel(parent)
        self.window.title("History")
        self.window.geometry("600x400")
        
        # Создаем основной фрейм с отступами
        self.frame = ttk.Frame(self.window, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель с кнопкой сброса
        top_frame = ttk.Frame(self.frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Создаем стиль для кнопки
        self.style = ttk.Style()
        self.style.configure("History.TButton", font=("Arial", 10))
        
        # Кнопка сброса
        ttk.Button(top_frame, 
                  text="Очистить историю", 
                  command=self.clear_history,
                  style="History.TButton").pack(side=tk.RIGHT)
        
        # История помидоров
        self.history_text = tk.Text(self.frame, wrap=tk.WORD, height=20)
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.configure(yscrollcommand=scrollbar.set)
        
        # Обновляем историю
        self.update_history()
        
    def clear_history(self):
        if messagebox.askyesno("Очистка истории", 
                             "Вы уверены, что хотите очистить историю помидоров за сегодня?"):
            self.settings.clear_today_history()
            self.update_history()
        
    def update_history(self):
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        comments = self.settings.get_today_comments()
        if comments:
            self.history_text.insert(tk.END, "История помидоров за сегодня:\n\n")
            for comment in comments:
                self.history_text.insert(tk.END, f"{comment['time']} - {comment['comment']}\n")
        else:
            self.history_text.insert(tk.END, "Сегодня еще не было завершенных помидоров")
            
        self.history_text.config(state=tk.DISABLED)

class GoalsWindow:
    def __init__(self, parent, settings, main_app):
        self.settings = settings
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Goals")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Создаем основной фрейм с отступами
        self.frame = ttk.Frame(self.window, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Форма добавления новой цели
        add_frame = ttk.LabelFrame(self.frame, text="Добавить новую цель", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Стиль для текста
        label_style = ("Arial", 10)
        entry_style = ("Arial", 10)
        
        ttk.Label(add_frame, text="Название цели:", font=label_style).pack(anchor=tk.W)
        self.title_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.title_var, width=40, font=entry_style).pack(fill=tk.X, pady=(2, 10))
        
        ttk.Label(add_frame, text="Количество помидоров:", font=label_style).pack(anchor=tk.W)
        self.count_var = tk.StringVar(value="1")
        ttk.Entry(add_frame, textvariable=self.count_var, width=10, font=entry_style).pack(anchor=tk.W, pady=(2, 10))
        
        ttk.Button(add_frame, text="Добавить цель", 
                  command=self.add_goal, style="Goals.TButton").pack(pady=(0, 5))
        
        # Создаем стиль для кнопки
        self.style = ttk.Style()
        self.style.configure("Goals.TButton", font=("Arial", 10))
        
        # Список текущих целей
        goals_frame = ttk.LabelFrame(self.frame, text="Текущие цели", padding="10")
        goals_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем фрейм для целей с прокруткой
        self.goals_canvas = tk.Canvas(goals_frame)
        scrollbar = ttk.Scrollbar(goals_frame, orient="vertical", command=self.goals_canvas.yview)
        self.goals_frame = ttk.Frame(self.goals_canvas)
        
        self.goals_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем элементы
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.goals_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Создаем окно для фрейма целей
        self.canvas_frame = self.goals_canvas.create_window((0, 0), window=self.goals_frame, anchor="nw", width=350)
        
        # Настраиваем обработку изменения размера
        self.goals_frame.bind("<Configure>", self.on_frame_configure)
        self.goals_canvas.bind("<Configure>", self.on_canvas_configure)
        
        self.update_goals_list()
        
    def on_frame_configure(self, event=None):
        self.goals_canvas.configure(scrollregion=self.goals_canvas.bbox("all"))
        
    def on_canvas_configure(self, event):
        self.goals_canvas.itemconfig(self.canvas_frame, width=event.width)
        
    def add_goal(self):
        try:
            title = self.title_var.get().strip()
            count = int(self.count_var.get())
            
            if not title:
                messagebox.showerror("Ошибка", "Введите название цели")
                return
                
            if count < 1:
                messagebox.showerror("Ошибка", "Количество помидоров должно быть больше 0")
                return
                
            self.settings.add_custom_goal(title, count)
            self.title_var.set("")
            self.count_var.set("1")
            self.update_goals_list()
            self.main_app.update_goals_display()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число помидоров")
            
    def update_goals_list(self):
        # Очищаем список
        for widget in self.goals_frame.winfo_children():
            widget.destroy()
            
        # Добавляем цели
        goals = self.settings.get_custom_goals()
        if not goals:
            ttk.Label(self.goals_frame, 
                     text="У вас пока нет целей", 
                     font=("Arial", 10)).pack(pady=5)
        else:
            for goal in goals:
                goal_frame = ttk.Frame(self.goals_frame)
                goal_frame.pack(fill=tk.X, pady=2)
                
                progress = goal["current"] / goal["target"] * 100
                
                # Создаем фрейм для текста и прогресс-бара
                info_frame = ttk.Frame(goal_frame)
                info_frame.pack(fill=tk.X, padx=5)
                
                # Создаем фрейм для заголовка и кнопки удаления
                header_frame = ttk.Frame(info_frame)
                header_frame.pack(fill=tk.X)
                
                ttk.Label(header_frame, 
                         text=f"{goal['title']}",
                         font=("Arial", 10, "bold")).pack(side=tk.LEFT)
                         
                # Кнопка удаления
                ttk.Button(header_frame,
                          text="✖",
                          width=3,
                          command=lambda g=goal: self.remove_goal(g['title']),
                          style="Goals.TButton").pack(side=tk.RIGHT)
                
                ttk.Label(info_frame, 
                         text=f"Прогресс: {goal['current']}/{goal['target']} ({progress:.1f}%)",
                         font=("Arial", 10)).pack(anchor=tk.W)
                
                # Добавляем разделитель между целями
                ttk.Separator(self.goals_frame, orient="horizontal").pack(fill=tk.X, pady=5)
                
    def remove_goal(self, title):
        if messagebox.askyesno("Удаление цели", f"Вы уверены, что хотите удалить цель '{title}'?"):
            self.settings.remove_custom_goal(title)
            self.update_goals_list()
            self.main_app.update_goals_display()

class PomodoroTimer:
    def __init__(self):
        self.settings = Settings()
        self.root = tk.Tk()
        self.root.title("Pomodoro")
        self.root.geometry("500x600")  # Увеличиваем высоту окна
        self.root.resizable(False, False)
        
        # Инициализация pygame для звука
        pygame.mixer.init()
        
        # Основные переменные
        self.work_time = self.settings.settings["work_time"]
        self.break_time = self.settings.settings["break_time"]
        self.long_break_time = self.settings.settings["long_break_time"]
        self.current_time = self.work_time
        self.is_running = False
        self.pomodoro_count = 0
        self.is_break = False
        
        # Создание GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Стиль
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 24))
        
        # Главный фрейм
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель с кнопками
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.history_button = ttk.Button(self.top_frame, text="📋", width=3,
                                       command=self.open_history)
        self.history_button.pack(side=tk.RIGHT, padx=5)
        
        self.settings_button = ttk.Button(self.top_frame, text="⚙", width=3, 
                                        command=self.open_settings)
        self.settings_button.pack(side=tk.RIGHT, padx=5)
        
        # Добавляем кнопку целей в верхнюю панель
        self.goals_button = ttk.Button(self.top_frame, text="🎯", width=3,
                                     command=self.open_goals)
        self.goals_button.pack(side=tk.RIGHT, padx=5)
        
        # Таймер
        self.timer_frame = ttk.Frame(self.main_frame)
        self.timer_frame.pack(pady=(0, 20))
        
        self.timer_label = ttk.Label(self.timer_frame, text="25:00", font=("Arial", 48))
        self.timer_label.pack()
        
        # Кнопки управления
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=(0, 20))
        
        self.start_button = ttk.Button(self.button_frame, text="Старт", 
                                     command=self.start_timer, width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(self.button_frame, text="Сброс", 
                                     command=self.reset_timer, width=15)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Счетчик помидоров
        self.pomodoro_counter = ttk.Label(self.main_frame, text="Помидоров: 0", font=("Arial", 14))
        self.pomodoro_counter.pack(pady=(0, 10))
        
        # Статус
        self.status_label = ttk.Label(self.main_frame, text="", font=("Arial", 14))
        self.status_label.pack(pady=(0, 20))
        
        # Поле для комментария
        self.comment_frame = ttk.LabelFrame(self.main_frame, text="Комментарий к текущему помидору")
        self.comment_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.comment_var = tk.StringVar()
        self.comment_entry = ttk.Entry(self.comment_frame, textvariable=self.comment_var, width=50)
        self.comment_entry.pack(padx=5, pady=5)
        
        # Достижения
        self.achievements_frame = ttk.LabelFrame(self.main_frame, text="Достижения")
        self.achievements_frame.pack(fill=tk.X)
        self.update_achievements()
        
        # Добавляем фрейм для отображения целей
        self.goals_display_frame = ttk.LabelFrame(self.main_frame, text="Мои цели")
        self.goals_display_frame.pack(fill=tk.X, pady=(0, 20))
        self.update_goals_display()
        
    def open_settings(self):
        SettingsWindow(self.root, self.settings, self)
        
    def open_history(self):
        history_window = HistoryWindow(self.root, self.settings)
        
    def open_goals(self):
        GoalsWindow(self.root, self.settings, self)
        
    def update_achievements(self):
        stats = self.settings.get_statistics()
        achievements = stats["achievements"]
        
        for widget in self.achievements_frame.winfo_children():
            widget.destroy()
            
        achievement_style = ("Arial", 12)
        
        ttk.Label(self.achievements_frame, 
                 text="✓ Первый помидор" if achievements["first_pomodoro"] else "✗ Первый помидор",
                 font=achievement_style).pack(padx=5, pady=2)
        ttk.Label(self.achievements_frame, 
                 text="✓ 5 помидоров" if achievements["five_pomodoros"] else "✗ 5 помидоров",
                 font=achievement_style).pack(padx=5, pady=2)
        ttk.Label(self.achievements_frame, 
                 text="✓ 10 помидоров" if achievements["ten_pomodoros"] else "✗ 10 помидоров",
                 font=achievement_style).pack(padx=5, pady=2)
        ttk.Label(self.achievements_frame, 
                 text="✓ Достигнута ежедневная цель" if achievements["daily_goal"] else "✗ Достигнута ежедневная цель",
                 font=achievement_style).pack(padx=5, pady=2)
            
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(text="Пауза")
            if not self.is_break:  # Если не перерыв, значит начинаем работу
                self.status_label.config(text="Работа")
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
        else:
            self.is_running = False
            self.start_button.config(text="Старт")
            self.status_label.config(text="Пауза")  # Меняем текст на "Пауза"
            
    def reset_timer(self):
        self.is_running = False
        self.current_time = self.work_time
        self.is_break = False
        self.update_timer_display()
        self.start_button.config(text="Старт")
        self.status_label.config(text="")  # Очищаем текст при сбросе
        
    def run_timer(self):
        while self.is_running and self.current_time > 0:
            time.sleep(1)
            self.current_time -= 1
            self.update_timer_display()
            
        if self.is_running:  # Если таймер дошел до 0
            self.is_running = False
            self.start_button.config(text="Старт")
            
            # Отправляем уведомление
            if self.is_break:
                notification.notify(
                    title="Помидор Таймер",
                    message="Перерыв окончен! Пора работать!",
                    app_icon=None,
                    timeout=10
                )
            else:
                # Сохраняем комментарий и обновляем статистику
                self.settings.update_daily_stats(1, self.comment_var.get())
                self.settings.update_custom_goals(1)  # Обновляем прогресс целей
                self.comment_var.set("")  # Очищаем поле комментария
                
                notification.notify(
                    title="Помидор Таймер",
                    message="Рабочее время окончено! Пора отдохнуть!",
                    app_icon=None,
                    timeout=10
                )
            
            # Переключаем режим
            self.is_break = not self.is_break
            if self.is_break:
                self.pomodoro_count += 1
                self.pomodoro_counter.config(text=f"Помидоров: {self.pomodoro_count}")
                if self.pomodoro_count % 4 == 0:
                    self.current_time = self.long_break_time
                    self.status_label.config(text="Длинный перерыв")
                else:
                    self.current_time = self.break_time
                    self.status_label.config(text="Перерыв")
            else:
                self.current_time = self.work_time
                self.status_label.config(text="Работа")
                
            self.update_timer_display()
            self.update_achievements()
            self.update_goals_display()  # Обновляем отображение целей
            
    def update_timer_display(self):
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
    def play_sound(self):
        if self.settings.settings["sound_enabled"]:
            pygame.mixer.Sound("alarm.wav").play()
        
    def update_settings(self):
        # Обновляем значения времени
        self.work_time = self.settings.settings["work_time"]
        self.break_time = self.settings.settings["break_time"]
        self.long_break_time = self.settings.settings["long_break_time"]
        
        # Сбрасываем таймер
        self.reset_timer()
        
    def update_goals_display(self):
        # Очищаем фрейм
        for widget in self.goals_display_frame.winfo_children():
            widget.destroy()
            
        # Добавляем цели
        goals = self.settings.get_custom_goals()
        if not goals:
            ttk.Label(self.goals_display_frame, 
                     text="Добавьте свои цели, нажав на кнопку 🎯",
                     font=("Arial", 10)).pack(pady=5)
        else:
            for goal in goals:
                progress = goal["current"] / goal["target"] * 100
                ttk.Label(self.goals_display_frame, 
                         text=f"{goal['title']} - {goal['current']}/{goal['target']} ({progress:.1f}%)",
                         font=("Arial", 10)).pack(pady=2)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PomodoroTimer()
    app.run() 