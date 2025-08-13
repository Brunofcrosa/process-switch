# Arquivo: src/ui/main_window.py

import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import time
from src.core.window_manager import WindowManager

class MainWindow(tk.Tk):
    def __init__(self, find_windows_callback, focus_callback, set_global_cycle_hotkey, set_global_toggle_hotkey, set_global_macro_hotkey, set_macro_keys_callback, set_focus_on_macro_callback, set_background_macro_mode_callback):
        super().__init__()
        self.title("Perfect World Automation")
        self.geometry("450x500")

        self.find_windows_callback = find_windows_callback
        self.focus_callback = focus_callback
        self.set_global_cycle_hotkey_callback = set_global_cycle_hotkey
        self.set_global_toggle_hotkey_callback = set_global_toggle_hotkey
        self.set_global_macro_hotkey_callback = set_global_macro_hotkey
        self.set_macro_keys_callback = set_macro_keys_callback
        self.set_focus_on_macro_callback = set_focus_on_macro_callback
        self.set_background_macro_mode_callback = set_background_macro_mode_callback

        self.hotkey_map = {}
        self.active_listener = None
        self.listening_for = None
        self.macro_keys = []
        self.focus_on_macro_var = tk.BooleanVar(value=True)
        self.background_macro_var = tk.BooleanVar(value=False)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.main_frame.columnconfigure(0, weight=1)

        self.update_button = ttk.Button(self.main_frame, text="Atualizar Janelas", command=self.update_window_list)
        self.update_button.grid(row=0, column=0, pady=10)

        cycle_hotkey_frame = ttk.Frame(self.main_frame)
        cycle_hotkey_frame.grid(row=1, column=0, pady=5, sticky="ew")
        cycle_hotkey_frame.columnconfigure(1, weight=1)

        self.cycle_hotkey_label = ttk.Label(cycle_hotkey_frame, text="Atalho para Ciclo:")
        self.cycle_hotkey_label.grid(row=0, column=0, padx=5, sticky="w")

        self.cycle_hotkey_button = ttk.Button(cycle_hotkey_frame, text="Definir Atalho", command=lambda: self.set_global_hotkey_mode("cycle"))
        self.cycle_hotkey_button.grid(row=0, column=2, padx=5, sticky="e")

        self.cycle_hotkey_status_label = ttk.Label(cycle_hotkey_frame, text="Nenhum atalho", foreground="red")
        self.cycle_hotkey_status_label.grid(row=0, column=1, padx=5, sticky="w")

        toggle_hotkey_frame = ttk.Frame(self.main_frame)
        toggle_hotkey_frame.grid(row=2, column=0, pady=5, sticky="ew")
        toggle_hotkey_frame.columnconfigure(1, weight=1)

        self.toggle_hotkey_label = ttk.Label(toggle_hotkey_frame, text="Atalho para Alternar:")
        self.toggle_hotkey_label.grid(row=0, column=0, padx=5, sticky="w")

        self.toggle_hotkey_button = ttk.Button(toggle_hotkey_frame, text="Definir Atalho", command=lambda: self.set_global_hotkey_mode("toggle"))
        self.toggle_hotkey_button.grid(row=0, column=2, padx=5, sticky="e")

        self.toggle_hotkey_status_label = ttk.Label(toggle_hotkey_frame, text="Nenhum atalho", foreground="red")
        self.toggle_hotkey_status_label.grid(row=0, column=1, padx=5, sticky="w")

        macro_hotkey_frame = ttk.Frame(self.main_frame)
        macro_hotkey_frame.grid(row=3, column=0, pady=5, sticky="ew")
        macro_hotkey_frame.columnconfigure(1, weight=1)

        self.macro_hotkey_label = ttk.Label(macro_hotkey_frame, text="Atalho para Macro:")
        self.macro_hotkey_label.grid(row=0, column=0, padx=5, sticky="w")

        self.macro_set_button = ttk.Button(macro_hotkey_frame, text="Definir Macro", command=self._show_macro_modal)
        self.macro_set_button.grid(row=0, column=2, padx=5, sticky="e")

        self.macro_hotkey_status_label = ttk.Label(macro_hotkey_frame, text="Nenhuma macro definida", foreground="red")
        self.macro_hotkey_status_label.grid(row=0, column=1, padx=5, sticky="w")

        self.macro_hotkey_button = ttk.Button(macro_hotkey_frame, text="Definir Atalho", command=lambda: self.set_global_hotkey_mode("macro"), state=tk.DISABLED)
        self.macro_hotkey_button.grid(row=1, column=2, padx=5, sticky="e")

        self.macro_sequence_label = ttk.Label(macro_hotkey_frame, text="Sequência: Nenhuma", foreground="gray")
        self.macro_sequence_label.grid(row=1, column=0, columnspan=2, padx=5, sticky="w")

        ttk.Separator(self.main_frame, orient='horizontal').grid(row=4, column=0, sticky="ew", pady=5)

        self.focus_on_macro_checkbutton = ttk.Checkbutton(self.main_frame, text="Focar nas janelas ao executar o macro", variable=self.focus_on_macro_var, command=self.on_focus_on_macro_toggle)
        self.focus_on_macro_checkbutton.grid(row=5, column=0, sticky="w", pady=5)
        self.set_focus_on_macro_callback(self.focus_on_macro_var.get())

        self.background_macro_checkbutton = ttk.Checkbutton(self.main_frame, text="Combar em segundo plano", variable=self.background_macro_var, command=self.on_background_macro_toggle)
        self.background_macro_checkbutton.grid(row=6, column=0, sticky="w", pady=5)
        self.set_background_macro_mode_callback(self.background_macro_var.get())

        self.main_frame.rowconfigure(7, weight=1)
        self.scroll_canvas = tk.Canvas(self.main_frame, borderwidth=0, background="#ffffff")
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.scroll_canvas.yview)

        self.scrollbar.grid(row=7, column=1, sticky="ns")
        self.scroll_canvas.grid(row=7, column=0, sticky="nsew")

        self.scroll_frame = ttk.Frame(self.scroll_canvas)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_canvas.create_window((4,4), window=self.scroll_frame, anchor="nw", tags="self.scroll_frame")

        self.scroll_frame.bind("<Configure>", self.on_frame_configure)
        self.scroll_canvas.bind('<Enter>', self._bind_mouse_wheel)
        self.scroll_canvas.bind('<Leave>', self._unbind_mouse_wheel)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_window_list()

    def _show_macro_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Definir Sequência de Macro")
        modal.geometry("300x250")
        modal.transient(self)
        modal.grab_set()
        modal.resizable(False, False)

        main_frame = ttk.Frame(modal, padding="10")
        main_frame.pack(fill="both", expand=True)

        available_keys = [f"F{i}" for i in range(1, 9)] + ["enter"]

        def update_sequence_display():
            if self.macro_keys:
                sequence_text = " ".join(self.macro_keys)
            else:
                sequence_text = "Nenhuma tecla selecionada"
            sequence_label.config(text=sequence_text)

        def add_key(combobox):
            selected_key = combobox.get()
            if selected_key and selected_key in available_keys:
                self.macro_keys.append(selected_key)
                update_sequence_display()

        def clear_keys():
            self.macro_keys = []
            update_sequence_display()

        def save_macro():
            self.macro_sequence_label.config(text=f"Sequência: {' '.join(self.macro_keys) if self.macro_keys else 'Nenhuma'}", foreground="black")
            self.macro_set_button.config(text="Alterar Macro")
            if self.macro_keys:
                self.macro_hotkey_button.config(state=tk.NORMAL)
            else:
                self.macro_hotkey_button.config(state=tk.DISABLED)
            self.set_macro_keys_callback(self.macro_keys)
            modal.destroy()

        def cancel_macro():
            modal.destroy()

        ttk.Label(main_frame, text="Teclas Disponíveis:").pack(fill="x")
        keys_combobox = ttk.Combobox(main_frame, values=available_keys, state="readonly")
        keys_combobox.set(available_keys[0])
        keys_combobox.pack(fill="x", pady=(0, 5))

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x")
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)

        ttk.Button(buttons_frame, text="Adicionar", command=lambda: add_key(keys_combobox)).grid(row=0, column=0, sticky="ew", padx=(0, 2))
        ttk.Button(buttons_frame, text="Limpar", command=clear_keys).grid(row=0, column=1, sticky="ew", padx=(2, 0))

        ttk.Label(main_frame, text="Sequência Atual:").pack(fill="x", pady=(10, 5))
        sequence_label = ttk.Label(main_frame, text="Nenhuma tecla selecionada", background="#f0f0f0", anchor="w", wraplength=280)
        sequence_label.pack(fill="x", pady=(0, 10), ipady=5)

        ttk.Separator(main_frame, orient='horizontal').pack(fill="x", pady=5)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x")

        ttk.Button(action_frame, text="OK", command=save_macro).pack(side="right", padx=5)
        ttk.Button(action_frame, text="Cancelar", command=cancel_macro).pack(side="right")

        update_sequence_display()

    def on_focus_on_macro_toggle(self):
        state = self.focus_on_macro_var.get()
        self.set_focus_on_macro_callback(state)
        if state:
            self.background_macro_var.set(False)
            self.background_macro_checkbutton.config(state=tk.DISABLED)
            self.set_background_macro_mode_callback(False)
        else:
            self.background_macro_checkbutton.config(state=tk.NORMAL)

    def on_background_macro_toggle(self):
        state = self.background_macro_var.get()
        self.set_background_macro_mode_callback(state)
        if state:
            self.focus_on_macro_var.set(False)
            self.focus_on_macro_checkbutton.config(state=tk.DISABLED)
            self.set_focus_on_macro_callback(False)
        else:
            self.focus_on_macro_checkbutton.config(state=tk.NORMAL)

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

        self.set_global_macro_hotkey_callback(hotkey_string=None)
        self.macro_hotkey_status_label.config(text="Nenhum atalho", foreground="red")
        self.macro_sequence_label.config(text="Sequência: Nenhuma", foreground="gray")
        self.macro_set_button.config(text="Definir Macro")
        self.macro_hotkey_button.config(state=tk.DISABLED)
        self.macro_keys = []
        self.set_macro_keys_callback(self.macro_keys)

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
        window_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(window_frame, text=title)
        title_label.grid(row=0, column=0, padx=5, sticky="w")

        hotkey_label = ttk.Label(window_frame, text="Nenhum atalho", foreground="grey")
        hotkey_label.grid(row=0, column=1, padx=5, sticky="e")

        hotkey_button = ttk.Button(window_frame, text="Definir Atalho", command=lambda: self.set_hotkey_mode_individual(hwnd, hotkey_label, hotkey_button))
        hotkey_button.grid(row=0, column=2, padx=5, sticky="e")

        focus_button = ttk.Button(window_frame, text="Focar", command=lambda: self.focus_callback(hwnd))
        focus_button.grid(row=0, column=3, padx=5, sticky="e")

        self.hotkey_map[hwnd] = {
            "button": hotkey_button,
            "label": hotkey_label,
            "hotkey_string": None
        }

    def set_global_hotkey_mode(self, hotkey_type):
        self.cancel_hotkey_listener()

        if hotkey_type == "cycle":
            button = self.cycle_hotkey_button
        elif hotkey_type == "toggle":
            button = self.toggle_hotkey_button
        else:
            button = self.macro_hotkey_button

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
            elif self.listening_for == "macro":
                if self.macro_keys:
                    self.set_global_macro_hotkey_callback(hotkey_string)
                    self.macro_hotkey_status_label.config(text=f"Ativo: '{hotkey_string}'", foreground="green")
                else:
                    self.macro_hotkey_status_label.config(text="Macro vazia, atalho não ativado.", foreground="red")
                self.macro_hotkey_button.config(text="Definir Atalho", state=tk.NORMAL)
            else:
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
            elif self.listening_for == "macro":
                self.macro_hotkey_button.config(text="Definir Atalho", state=tk.NORMAL)
            elif self.listening_for:
                hwnd = self.listening_for
                if hwnd in self.hotkey_map:
                    button = self.hotkey_map[hwnd]["button"]
                    button.config(text="Definir Atalho", state=tk.NORMAL)

            self.active_listener = None
            self.listening_for = None