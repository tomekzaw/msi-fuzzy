def fix_scaling():
    import sys
    if sys.platform == 'win32':
        import ctypes
        PROCESS_SYSTEM_DPI_AWARE = 1
        ctypes.OleDLL('shcore').SetProcessDpiAwareness(PROCESS_SYSTEM_DPI_AWARE)
