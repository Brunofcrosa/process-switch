import keyboard
from src.core.process_handler import ProcessHandler
from src.core.window_manager import WindowManager
from src.ui.main_window import MainWindow
import time

window_manager = WindowManager()
process_handler = ProcessHandler()

global_cycle_hotkey_handle = None
global_toggle_hotkey_handle = None
global_macro_hotkey_handle = None

window_handles_for_cycle = []
last_window_handles = []

def find_perfect_world_windows():
    processes = process_handler.find_processes()
    found_windows = []
    if not processes:
        return found_windows
    for proc in processes:
        hwnd = window_manager.get_window_by_pid(proc.pid)
        if hwnd:
            window_title = window_manager.get_window_title(hwnd)
            if not window_title:
                window_title = f"Perfect World (PID: {proc.pid})"
            found_windows.append((window_title, hwnd))
    return found_windows

def focus_on_window(hwnd):
    global last_window_handles
    
    if hwnd in last_window_handles:
        last_window_handles.remove(hwnd)
    
    last_window_handles.insert(0, hwnd)
    
    if len(last_window_handles) > 2:
        last_window_handles.pop()
    
    window_manager.bring_to_foreground(hwnd)

def cycle_windows():
    global window_handles_for_cycle
    
    if not window_handles_for_cycle:
        return
    
    try:
        current_hwnd = window_manager.get_current_foreground_window()
        if current_hwnd in window_handles_for_cycle:
            current_index = window_handles_for_cycle.index(current_hwnd)
            next_index = (current_index + 1) % len(window_handles_for_cycle)
            focus_on_window(window_handles_for_cycle[next_index])
        else:
            focus_on_window(window_handles_for_cycle[0])
    except Exception:
        focus_on_window(window_handles_for_cycle[0])
        
def toggle_last_windows():
    global last_window_handles
    
    if len(last_window_handles) < 2:
        return
        
    next_hwnd = last_window_handles[1]
    focus_on_window(next_hwnd)

def send_macro_to_windows(keys):
    windows = find_perfect_world_windows()
    if not windows:
        return
    
    current_hwnd = window_manager.get_current_foreground_window()
    
    for _, hwnd in windows:
        window_manager.bring_to_foreground(hwnd)
        time.sleep(0.1)
        for key in keys:
            keyboard.send(key)
            time.sleep(0.05)

    if current_hwnd:
         window_manager.bring_to_foreground(current_hwnd)

def set_global_cycle_hotkey(hotkey_string, handles):
    global global_cycle_hotkey_handle, window_handles_for_cycle
    
    if global_cycle_hotkey_handle:
        keyboard.remove_hotkey(global_cycle_hotkey_handle)
        global_cycle_hotkey_handle = None
        
    if hotkey_string and handles:
        window_handles_for_cycle = [hwnd for _, hwnd in handles]
        global_cycle_hotkey_handle = keyboard.add_hotkey(hotkey_string, cycle_windows)

def set_global_toggle_hotkey(hotkey_string, handles):
    global global_toggle_hotkey_handle, last_window_handles
    
    if global_toggle_hotkey_handle:
        keyboard.remove_hotkey(global_toggle_hotkey_handle)
        global_toggle_hotkey_handle = None
    
    if hotkey_string and handles:
        last_window_handles = [h for t, h in handles]
        if len(last_window_handles) > 2:
            last_window_handles = last_window_handles[:2]
        
        global_toggle_hotkey_handle = keyboard.add_hotkey(hotkey_string, toggle_last_windows)

def set_global_macro_hotkey(hotkey_string, keys):
    global global_macro_hotkey_handle
    
    if global_macro_hotkey_handle:
        keyboard.remove_hotkey(global_macro_hotkey_handle)
        global_macro_hotkey_handle = None
        
    if hotkey_string and keys:
        global_macro_hotkey_handle = keyboard.add_hotkey(hotkey_string, lambda: send_macro_to_windows(keys))

def main():
    root = MainWindow(find_perfect_world_windows, focus_on_window, set_global_cycle_hotkey, set_global_toggle_hotkey, set_global_macro_hotkey)
    root.mainloop()

if __name__ == "__main__":
    main()