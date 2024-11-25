import sys, subprocess, os, bpy

def installModule(packageName):
    try:
        subprocess.call([python_exe, "import ", packageName])
    except:
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        subprocess.call([python_exe, "-m", "ensurepip"])
        if (4, 2, 0) <= bpy.app.version:
            try:
                subprocess.call([python_exe, "-m", "install", "--upgrade", "pip"])
                subprocess.call([python_exe, "-m", "install", packageName])
            except Exception as e:
                print(e)
            
            try:
                subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
                subprocess.call([python_exe, "-m", "pip", "install", packageName])
            except Exception as e:
                print(e)
        else:
            try:
                subprocess.call([python_exe, "-m", "install", "--upgrade", "pip"])
                subprocess.call([python_exe, "-m", "install", packageName])
            except Exception as e:
                print(e)
            
            try:
                subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
                subprocess.call([python_exe, "-m", "pip", "install", packageName])
            except Exception as e:
                print(e)

def initCS():
    installModule("pythonnet")
    import pythonnet # type: ignore
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs")
    dll_names = [
        "AshDumpLib.dll",
        "libHSON.dll",
        "Newtonsoft.Json.dll",
        "SharpNeedle.dll",
        "SharpNeedleWrap.dll"
    ]

    pythonnet.load("coreclr")

    import clr # type: ignore
    for dll_name in dll_names:
        dll_path = os.path.join(path, dll_name)
        try:
            clr.AddReference(dll_path)
            print(f"{dll_name} loaded successfully")
        except Exception as e:
            print(f"Failed to load {dll_name}: {e}")

def deinitCS():
    import pythonnet # type: ignore
    pythonnet.unload()