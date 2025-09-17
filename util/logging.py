def log(message: str):
    print(message)

def info(message: str):
    log(f"[INFO] {message}")

def warn(message: str):
    log(f"[WARN] {message}")

def error(message: str):
    log(f"[ERROR] {message}")