from util.config import CFG

def log(message: str, verbose = False, iserror = False):
    if CFG["debug"] or iserror:
        if verbose and CFG["verbose"]: print(message)
        if not verbose: print(message)

def info(message: str, verbose = False):
    log(f"\x1b[36m[INFO]\x1b[0m {message}", verbose)

def warn(message: str, verbose = False):
    log(f"\x1b[33m[WARN]\x1b[0m {message}", verbose)

def error(message: str, verbose = False):
    log(f"\x1b[31m[ERROR]\x1b[0m {message}", verbose, True)