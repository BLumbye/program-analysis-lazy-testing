import os
import subprocess
import fnmatch
import stat
import shutil
from pathlib import Path
import argparse

def main():
    print("Start compiling...")
    for cb in find_codebases():
        next_dir = os.path.join(cb, "next")
        prev_dir = os.path.join(cb, "previous")
        compile(next_dir)
        compile(prev_dir)
        decompile(next_dir)
        decompile(prev_dir)
    print("Done!")

def find_codebases():
    cb_dir = os.path.join(os.path.dirname(__file__), "..", "codebases")
    return [ os.path.join(cb_dir, cb) for cb in os.listdir(cb_dir) ]

def find_files(folder, extension):
    matches = []
    for root, _, filenames in os.walk(folder):
        for filename in fnmatch.filter(filenames, "*." + extension):
            matches.append((root, root[len(folder) + 1:], filename))
    return matches

def find_files_root(folder, extension):
    matches = []
    for root, _, file in find_files(folder, extension):
        matches.append(os.path.join(root, file))
    return matches

def make_writeable(f, path, _):
        os.chmod(path, stat.S_IWRITE)
        f(path)

def compile(directory):
    generated_dir = os.path.join(directory, "generated")
    if os.path.exists(generated_dir):
        shutil.rmtree(generated_dir, onexc=make_writeable)
    Path(generated_dir).mkdir()

    compile_result = subprocess.run(
        [
            "javac",
            *(find_files_root(directory, "java")),
            os.path.join("utils", "Test.java"),
            "-d",
            generated_dir,
        ],
        shell=True,
    )

    if compile_result.returncode == 0:
        # print(f"Compiled to class")
        pass
    else:
        print(f"Error Compiling to class: {compile_result.returncode}")

def decompile(dir):
    generated_dir = os.path.join(dir, "generated")
    decompiled_dir = os.path.join(dir, "decompiled")
    if os.path.exists(decompiled_dir):
        shutil.rmtree(decompiled_dir, onexc=make_writeable)
    Path(decompiled_dir).mkdir()

    for _, file_dir, file in find_files(generated_dir, "class"):
        from_dir = os.path.join(generated_dir, file_dir, file)

        dest_dir = os.path.join(decompiled_dir, file_dir)
        Path(dest_dir).mkdir(exist_ok=True, parents=True)
        filename = os.path.splitext(file)[0]
        to_dir = os.path.join(dest_dir, filename + ".json")
        
        jvm2json = subprocess.run([os.path.join("utils", "jvm2json"),  "-s", from_dir , "-t", to_dir], shell = True)

        if jvm2json.returncode == 0:
            # print(f"Decompiled {file} to json")
            pass
        else:
            print(f"Error decompiling {file} to json: {jvm2json.returncode}")


def watch_codebase():
    main()
    import time
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    class MyEventHandler(FileSystemEventHandler):
        def on_any_event(self, event: FileSystemEvent) -> None:
            if ".java" in event.src_path:
                main()

    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, "codebases", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Java to JSON')
    parser.add_argument('-w', dest='watch_codebase', action='store_const', const=True, default=False, help='Watch the codebase for changes and automatically recompile and decompile')
    args = parser.parse_args()
    if args.watch_codebase:
        watch_codebase()
    else:
        main()
