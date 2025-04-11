import json
import os
from datetime import datetime

class Settings:
    def __init__(self):
        self.settings_file = "settings.json"
        self.default_settings = {
            "work_time": 25 * 60,  # 25 минут в секундах
            "break_time": 5 * 60,   # 5 минут в секундах
            "long_break_time": 15 * 60,  # 15 минут в секундах
            "daily_goal": 8,  # Цель по количеству помидоров в день
            "custom_goals": [],  # Список пользовательских целей
            "statistics": {
                "total_pomodoros": 0,
                "daily_pomodoros": {},
                "achievements": {
                    "first_pomodoro": False,
                    "five_pomodoros": False,
                    "ten_pomodoros": False,
                    "daily_goal": False
                }
            }
        }
        self.settings = self.load_settings()
        
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    old_settings = json.load(f)
                    
                # Если это старые настройки (без statistics)
                if "statistics" not in old_settings:
                    # Создаем новые настройки с дефолтными значениями
                    new_settings = self.default_settings.copy()
                    # Копируем существующие значения
                    for key in ["work_time", "break_time", "long_break_time", "daily_goal"]:
                        if key in old_settings:
                            new_settings[key] = old_settings[key]
                    # Сохраняем обновленные настройки
                    self.settings = new_settings
                    self.save_settings()
                    return new_settings
                    
                return old_settings
            except json.JSONDecodeError:
                return self.default_settings
        return self.default_settings
        
    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
            
    def update_daily_stats(self, pomodoros_completed, comment=""):
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Обновляем общую статистику
        self.settings["statistics"]["total_pomodoros"] += pomodoros_completed
        
        # Обновляем ежедневную статистику
        if today not in self.settings["statistics"]["daily_pomodoros"]:
            self.settings["statistics"]["daily_pomodoros"][today] = {
                "count": 0,
                "comments": []
            }
            
        self.settings["statistics"]["daily_pomodoros"][today]["count"] += pomodoros_completed
        if comment:
            self.settings["statistics"]["daily_pomodoros"][today]["comments"].append({
                "time": datetime.now().strftime("%H:%M"),
                "comment": comment
            })
            
        # Проверяем достижения
        self.check_achievements()
        
        # Сохраняем изменения
        self.save_settings()
        
    def check_achievements(self):
        stats = self.settings["statistics"]
        achievements = stats["achievements"]
        
        # Первый помидор
        if stats["total_pomodoros"] >= 1:
            achievements["first_pomodoro"] = True
            
        # 5 помидоров
        if stats["total_pomodoros"] >= 5:
            achievements["five_pomodoros"] = True
            
        # 10 помидоров
        if stats["total_pomodoros"] >= 10:
            achievements["ten_pomodoros"] = True
            
        # Достижение ежедневной цели
        today = datetime.now().strftime("%Y-%m-%d")
        if today in stats["daily_pomodoros"]:
            if stats["daily_pomodoros"][today]["count"] >= self.settings["daily_goal"]:
                achievements["daily_goal"] = True
                
    def get_statistics(self):
        return self.settings["statistics"]
        
    def get_today_comments(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.settings["statistics"]["daily_pomodoros"]:
            return self.settings["statistics"]["daily_pomodoros"][today]["comments"]
        return []

    def add_custom_goal(self, title, target_count):
        """Добавляет новую пользовательскую цель"""
        if "custom_goals" not in self.settings:
            self.settings["custom_goals"] = []
            
        self.settings["custom_goals"].append({
            "title": title,
            "target": target_count,
            "current": 0,
            "date_added": datetime.now().strftime("%Y-%m-%d")
        })
        self.save_settings()
        
    def update_custom_goals(self, pomodoros_completed):
        """Обновляет прогресс пользовательских целей"""
        if "custom_goals" in self.settings:
            for goal in self.settings["custom_goals"]:
                if goal["current"] < goal["target"]:
                    goal["current"] += pomodoros_completed
            self.save_settings()
            
    def get_custom_goals(self):
        """Возвращает список пользовательских целей"""
        return self.settings.get("custom_goals", [])

    def remove_custom_goal(self, title):
        """Удаляет пользовательскую цель по названию"""
        if "custom_goals" in self.settings:
            self.settings["custom_goals"] = [
                goal for goal in self.settings["custom_goals"] 
                if goal["title"] != title
            ]
            self.save_settings()

    def clear_today_history(self):
        """Очищает историю помидоров за сегодня"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.settings["statistics"]["daily_pomodoros"]:
            self.settings["statistics"]["daily_pomodoros"][today]["comments"] = []
            self.settings["statistics"]["daily_pomodoros"][today]["count"] = 0
            self.save_settings() 