import win32gui
import win32con
import win32process
import win32api
import time
import pywintypes
import pyautogui

class WindowManager:
    def get_current_foreground_window(self):
        return win32gui.GetForegroundWindow()

    def get_window_by_pid(self, pid):
        top_windows = []
        win32gui.EnumWindows(self._window_enum_handler, top_windows)
        for hwnd, process_id in top_windows:
            if process_id == pid:
                return hwnd
        return None

    def get_window_title(self, hwnd):
        return win32gui.GetWindowText(hwnd)

    def bring_to_foreground(self, hwnd):
        if not hwnd or not win32gui.IsWindow(hwnd):
            print(f"Erro: HWND inválido ou janela não existe: {hwnd}")
            return
        
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            win32gui.SetForegroundWindow(hwnd)
            print(f"Foco definido para a janela com HWND: {hwnd}")
        except pywintypes.error as e:
            print(f"Falha ao focar com SetForegroundWindow, tentando método alternativo. Erro: {e}")
            self._force_focus_on_window(hwnd)

    def _force_focus_on_window(self, hwnd):
        try:
            # Tenta simular um clique na barra de título da janela.
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[0] + 50  # 50 pixels da borda esquerda
            y = rect[1] + 15  # 15 pixels do topo (na barra de título)
            
            pyautogui.click(x, y)
            print(f"Foco obtido com sucesso através de simulação de clique.")

        except Exception as e:
            print(f"Falha total ao focar a janela, mesmo com simulação de clique. Verifique o estado do jogo. Erro: {e}")

    def _window_enum_handler(self, hwnd, result_list):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            result_list.append((hwnd, pid))