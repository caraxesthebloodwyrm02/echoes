import venv, sys, traceback, os
try:
    target = r'E:\Projects\Development\tmp_debug_venv'
    if os.path.exists(target):
        import shutil
        shutil.rmtree(target)
    print('Creating venv programmatically at', target)
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(target)
    print('Venv created')
except Exception:
    traceback.print_exc()
    sys.exit(1)
