import os
import tempfile
import traceback

print("Python executable:", os.sys.executable)

try:
    print("tempfile.gettempdir() ->", tempfile.gettempdir())
except Exception as e:
    print("tempfile.gettempdir() raised:", repr(e))
    traceback.print_exc()

candidates = []
env_names = ["TMPDIR", "TEMP", "TMP"]
for n in env_names:
    v = os.environ.get(n)
    if v and v not in candidates:
        candidates.append(v)

additional = [
    os.path.expanduser(r"~\\AppData\\Local\\Temp"),
    r"C:\\WINDOWS\\Temp",
    r"c:\\temp",
    r"c:\\tmp",
    r"\\temp",
    r"\\tmp",
    r"E:\\Projects\\Development",
]
for p in additional:
    if p not in candidates:
        candidates.append(p)

print("\nCandidate temp directories to probe:")
for p in candidates:
    print("\n---")
    print("path:", p)
    try:
        print("exists:", os.path.exists(p))
        print("isdir:", os.path.isdir(p))
        try:
            print("access_w (os.access):", os.access(p, os.W_OK))
        except Exception as ex:
            print("access_w error:", repr(ex))
        # Try to create a subdir
        testdir = os.path.join(p, "tmp_probe_test_dir")
        try:
            if not os.path.exists(p):
                print("parent does not exist, skipping mkdir test")
            else:
                if not os.path.exists(testdir):
                    os.makedirs(testdir, exist_ok=True)
                    print("mkdir OK:", testdir)
                    # create a small file
                    with open(os.path.join(testdir, "probe.txt"), "w") as f:
                        f.write("ok")
                    print("file write OK")
                    # cleanup
                    try:
                        os.remove(os.path.join(testdir, "probe.txt"))
                    except Exception:
                        pass
                    try:
                        os.rmdir(testdir)
                    except Exception:
                        pass
                else:
                    print("testdir already exists")
        except Exception as ex:
            print("mkdir/file test error:", repr(ex))
    except Exception as ex:
        print("probe error for path", p, repr(ex))

print("\nProbe complete")
