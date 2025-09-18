from util.config import CFG

def log(message: str, verbose = False):
    if CFG["debug"]:
        if verbose and CFG["verbose"]: print(message)
        if not verbose: print(message)

def info(message: str, verbose = False):
    log(f"[INFO] {message}", verbose)

def warn(message: str, verbose = False):
    log(f"[WARN] {message}", verbose)

def error(message: str, verbose = False):
    log(f"[ERROR] {message}", verbose)