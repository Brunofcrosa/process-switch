import psutil
from src.utils.config import PERFECT_WORLD_PROCESS_NAME

class ProcessHandler:
    def find_processes(self):
        found_processes = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] == PERFECT_WORLD_PROCESS_NAME:
                    found_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return found_processes