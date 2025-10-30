# Chunk 35 Summary

46202 INFO: Bootloader C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyInstaller\bootloader\Windows-64bit-intel\runw.exe
46202 INFO: checking EXE
46220 INFO: Building because toc changed
46220 INFO: Building EXE from EXE-00.toc
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Scripts\pyinstaller.exe\__main__.py", line 7, in <module>
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyInstaller\__main__.py", line 231, in _console_script_run
    run()
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyInstaller\__main__.py", line 215, in run
    run_build(pyi_config, spec_file, **vars(args))
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyInstaller\__main__.py", line 70, in run_build
    PyInstaller.building.build_main.main(pyi_config, spec_file, **kwargs)
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyInstaller\building\build_main.py", line 1282, in main
    build(specfile, distpath, workpath, clean_build)
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyInstaller\building\build_main.py", line 1220, in build
    exec(code, spec_namespace)
  File "chunker_hidden.spec", line 25, in <module>
    exe = EXE(
          ^^^^
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyInstaller\building\api.py", line 678, in __init__
    self.__postinit__()
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyInstaller\building\datastruct.py", line 184, in __postinit__
    self.assemble()
  File "C:\Users\carucci_r\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyInstaller\building\api.py", line 772, in assemble
    os.remove(self.name)
PermissionError: [WinError 5] Access is denied: 'C:\\Users\\carucci_r\\Documents\\chunker\\dist\\chunker_hidden.exe'

C:\Users\carucci_r\Documents\chunker>
ChatGPT said:
✅ You successfully built the PyInstaller EXE, but the final step failed due to a PermissionError:

PermissionError: [WinError 5] Access is denied: '...\\dist\\chunker_hidden.exe'
This typically means chunker_hidden.exe is still running, or open in another process (e.g. File Explorer or antivirus scan). ✅ To fix it:
Make sure the EXE is not running:

Open Task Manager (Ctrl+Shift+Esc)

Find and end any process named chunker_hidden.exe

Close any folder window showing dist\\chunker_hidden.exe

File Explorer might lock the file.
