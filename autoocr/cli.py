import os
import sys
import typing as typ
import threading
import re
import subprocess
import filelock
from functools import partial


def _list_files(root_dir: str) -> typ.Set[str]:
    return set(f for f in os.listdir(root_dir)
               if os.path.isfile(f) and f.endswith('.pdf'))


_EXTRACT_NAME: re.Pattern = re.compile('^(.*?)(_ocr)?\\.pdf$')


def _ocred_name(path: str):
    match = _EXTRACT_NAME.match(path)
    if not match:
        return None
    return f"{match[1]}_ocr.pdf"


def _need_ocr(files: typ.Set[str]) -> typ.Set[str]:
    return set(f for f in files
               if not _ocred_name(f) in files)


def _run_ocr_on_file(file: str):
    result = _ocred_name(file)
    if result is not None and os.path.exists(result):
        return  # defensive programming
    print(f"Starting pdfsandwich {file}")
    subprocess.run(
        args=['pdfsandwich', file],
        capture_output=False,
        stdin=sys.stdin,
        stdout=sys.stdout,
        check=True
    )


def _run_ocr_threaded(files: typ.Set[str]):
    threads = []
    for f in files:
        threads.append(threading.Thread(target=partial(_run_ocr_on_file, f)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def _cleanup(all_pdf_files: typ.Set[str]):
    # lol let's just run _ocred_name like 1000 times
    to_remove = [f for f in all_pdf_files
                 if _ocred_name(f) is not None
                 and _ocred_name(f) != f
                 and os.path.exists(_ocred_name(f))]
    print(f"Would remove {to_remove}")


def main(args=None):
    if args is None:
        args = sys.argv
    with filelock.FileLock(".autoocr_running"):
        _run_ocr_threaded(_need_ocr(set(args[1:])))
        os.remove(".autoocr_running")
    # poor-man's arg-parsing :)
    if "--cleanup" in set(args[1:]):
        _cleanup(set(args[1:]))
