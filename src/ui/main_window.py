import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import time
from src.core.window_manager import WindowManager

class MainWindow(tk.Tk):
    def __init__(self, find_windows_callback, focus_callback, set_global_cycle_hotkey, set_global_toggle_hotkey):
        super().__init__()
        self.title("Perfect World Automation")
        self.geometry("450x400")
        self.resizable(False, False)

        self.find_windows_callback = find_windows_callback
        self.focus_callback = focus_callback
        self.set_global_cycle_hotkey_callback = set_global_cycle_hotkey
        self.set_global_toggle_hotkey_callback = set_global_toggle_hotkey
        
        self.hotkey_map = {}
        self.active_listener = None
        self.listening_for = None # "cycle", "toggle", or hwnd for individual

        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.update_button = ttk.Button(self.main_frame, text="Atualizar Janelas", command=self.update_window_list)
        self.update_button.pack(pady=10)

        # Seção para o atalho de alternância entre todas as janelas (ciclo)
        cycle_hotkey_frame = ttk.Frame(self.main_frame)
        cycle_hotkey_frame.pack(pady=5, fill='x')

        self.cycle_hotkey_label = ttk.Label(cycle_hotkey_frame, text="Atalho para Ciclo:")
        self.cycle_hotkey_label.pack(side="left", padx=5)

        self.cycle_hotkey_button = ttk.Button(cycle_hotkey_frame, text="Definir Atalho", command=lambda: self.set_global_hotkey_mode("cycle"))
        self.cycle_hotkey_button.pack(side="left", padx=5)

        self.cycle_hotkey_status_label = ttk.Label(cycle_hotkey_frame, text="Nenhum atalho", foreground="red")
        self.cycle_hotkey_status_label.pack(side="left", padx=5)
        
        # Seção para o atalho de alternância entre as duas últimas janelas (toggle)
        toggle_hotkey_frame = ttk.Frame(self.main_frame)
        toggle_hotkey_frame.pack(pady=5, fill='x')
        
        self.toggle_hotkey_label = ttk.Label(toggle_hotkey_frame, text="Atalho para Alternar:")
        self.toggle_hotkey_label.pack(side="left", padx=5)
        
        self.toggle_hotkey_button = ttk.Button(toggle_hotkey_frame, text="Definir Atalho", command=lambda: self.set_global_hotkey_mode("toggle"))
        self.toggle_hotkey_button.pack(side="left", padx=5)
        
        self.toggle_hotkey_status_label = ttk.Label(toggle_hotkey_frame, text="Nenhum atalho", foreground="red")
        self.toggle_hotkey_status_label.pack(side="left", padx=5)

        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=5)

        self.scroll_canvas = tk.Canvas(self.main_frame, borderwidth=0, background="#ffffff")
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_frame = ttk.Frame(self.scroll_canvas)

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scroll_canvas.create_window((4,4), window=self.scroll_frame, anchor="nw", tags="self.scroll_frame")

        self.scroll_frame.bind("<Configure>", self.on_frame_configure)
        self.scroll_canvas.bind('<Enter>', self._bind_mouse_wheel)
        self.scroll_canvas.bind('<Leave>', self._unbind_mouse_wheel)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_window_list()

    def on_frame_configure(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _bind_mouse_wheel(self, event):
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _unbind_mouse_wheel(self, event):
        self.scroll_canvas.unbind_all("<MouseWheel>")

    def _on_mouse_wheel(self, event):
        self.scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def on_closing(self):
        keyboard.unhook_all()
        self.destroy()

    def update_window_list(self):
        self.cancel_hotkey_listener()
        
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        keyboard.unhook_all()
        self.hotkey_map = {}
        
        self.set_global_cycle_hotkey_callback(hotkey_string=None, handles=[])
        self.cycle_hotkey_status_label.config(text="Nenhum atalho", foreground="red")
        
        self.set_global_toggle_hotkey_callback(hotkey_string=None, handles=[])
        self.toggle_hotkey_status_label.config(text="Nenhum atalho", foreground="red")
        
        windows = self.find_windows_callback()

        if not windows:
            label = ttk.Label(self.scroll_frame, text="Nenhuma janela do Perfect World encontrada.", foreground="red")
            label.pack(pady=10)
        else:
            for title, hwnd in windows:
                self.create_window_widgets(title, hwnd)
        
    def create_window_widgets(self, title, hwnd):
        window_frame = ttk.Frame(self.scroll_frame, padding="5", relief="solid", borderwidth=1)
        window_frame.pack(fill="x", pady=5)

        title_label = ttk.Label(window_frame, text=title)
        title_label.pack(side="left", padx=5)

        hotkey_label = ttk.Label(window_frame, text="Nenhum atalho", foreground="grey")
        hotkey_label.pack(side="right", padx=5)
        
        hotkey_button = ttk.Button(window_frame, text="Definir Atalho", command=lambda: self.set_hotkey_mode_individual(hwnd, hotkey_label, hotkey_button))
        hotkey_button.pack(side="right", padx=5)
        
        focus_button = ttk.Button(window_frame, text="Focar", command=lambda: self.focus_callback(hwnd))
        focus_button.pack(side="right", padx=5)
        
        self.hotkey_map[hwnd] = {
            "button": hotkey_button,
            "label": hotkey_label,
            "hotkey_string": None
        }

    def set_global_hotkey_mode(self, hotkey_type):
        self.cancel_hotkey_listener()
        
        if hotkey_type == "cycle":
            button = self.cycle_hotkey_button
            status_label = self.cycle_hotkey_status_label
        else: # hotkey_type == "toggle"
            button = self.toggle_hotkey_button
            status_label = self.toggle_hotkey_status_label

        button.config(text="Pressione...")
        button.config(state=tk.DISABLED)
        
        self.listening_for = hotkey_type
        self.active_listener = keyboard.hook(self.on_hotkey_press)

    def set_hotkey_mode_individual(self, hwnd, hotkey_label, hotkey_button):
        self.cancel_hotkey_listener()
        
        hotkey_button.config(text="Pressione...")
        hotkey_button.config(state=tk.DISABLED)
        
        self.listening_for = hwnd
        self.active_listener = keyboard.hook(self.on_hotkey_press)
    
    def on_hotkey_press(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            hotkey_string = keyboard.get_hotkey_name()
            
            if self.listening_for == "cycle":
                windows = self.find_windows_callback()
                self.set_global_cycle_hotkey_callback(hotkey_string, windows)
                self.cycle_hotkey_status_label.config(text=f"Ativo: '{hotkey_string}'", foreground="green")
                self.cycle_hotkey_button.config(text="Definir Atalho", state=tk.NORMAL)
            elif self.listening_for == "toggle":
                windows = self.find_windows_callback()
                self.set_global_toggle_hotkey_callback(hotkey_string, windows)
                self.toggle_hotkey_status_label.config(text=f"Ativo: '{hotkey_string}'", foreground="green")
                self.toggle_hotkey_button.config(text="Definir Atalho", state=tk.NORMAL)
            else: # Individual hotkey
                hwnd = self.listening_for
                hotkey_data = self.hotkey_map.get(hwnd)
                if hotkey_data:
                    if hotkey_data["hotkey_string"]:
                        keyboard.remove_hotkey(hotkey_data["hotkey_string"])
                    
                    keyboard.add_hotkey(hotkey_string, lambda h=hwnd: self.focus_callback(h))
                    
                    hotkey_data["label"].config(text=hotkey_string, foreground="green")
                    hotkey_data["button"].config(text="Definir Atalho", state=tk.NORMAL)
                    hotkey_data["hotkey_string"] = hotkey_string
            
            self.cancel_hotkey_listener()

    def cancel_hotkey_listener(self):
        if self.active_listener:
            keyboard.unhook(self.active_listener)
            
            if self.listening_for == "cycle":
                self.cycle_hotkey_button.config(text="Definir Atalho", state=tk.NORMAL)
            elif self.listening_for == "toggle":
                self.toggle_hotkey_button.config(text="Definir Atalho", state=tk.NORMAL)
            elif self.listening_for: # Individual hotkey
                hwnd = self.listening_for
                if hwnd in self.hotkey_map:
                    button = self.hotkey_map[hwnd]["button"]
                    button.config(text="Definir Atalho", state=tk.NORMAL)
            
            self.active_listener = None
            self.listening_for = None