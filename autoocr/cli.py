import os
import sys
import typing as typ
import threading
import re
import subprocess
import filelock


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
    if os.path.exists(_ocred_name(file)):
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
    targets = [lambda: _run_ocr_on_file(f) for f in files]
    threads = [threading.Thread(target=target) for target in targets]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def main(args=None):
    if args is None:
        args = sys.argv
    with filelock.FileLock(".autoocr_running"):
        _run_ocr_threaded(_need_ocr(set(args[1:])))
        os.remove(".autoocr_running")

