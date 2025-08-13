import win32gui
import win32con
import win32api
import win32process
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
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[0] + 50
            y = rect[1] + 15
            
            pyautogui.click(x, y)
            print(f"Foco obtido com sucesso através de simulação de clique.")

        except Exception as e:
            print(f"Falha total ao focar a janela, mesmo com simulação de clique. Verifique o estado do jogo. Erro: {e}")

    def flash_window(self, hwnd):
        if not hwnd or not win32gui.IsWindow(hwnd):
            return
        
        win32gui.FlashWindow(hwnd, True)

    def send_keys_with_post_message(self, hwnd, keys):
        if not hwnd or not win32gui.IsWindow(hwnd):
            print(f"Erro: HWND inválido ou janela não existe: {hwnd}")
            return

        print(f"Enviando macro para a janela em segundo plano via PostMessage: {hwnd}")

        vk_map = {
            'F1': win32con.VK_F1, 'F2': win32con.VK_F2, 'F3': win32con.VK_F3,
            'F4': win32con.VK_F4, 'F5': win32con.VK_F5, 'F6': win32con.VK_F6,
            'F7': win32con.VK_F7, 'F8': win32con.VK_F8,
            'enter': win32con.VK_RETURN
        }
        
        for key in keys:
            vk_code = vk_map.get(key)
            if vk_code:
                # Envia o evento de tecla pressionada
                win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                time.sleep(0.05)
                # Envia o evento de tecla solta
                win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
                time.sleep(0.05)
        print(f"Macro enviada para {hwnd}")

    def _window_enum_handler(self, hwnd, result_list):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            result_list.append((hwnd, pid))