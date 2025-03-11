from cx_Freeze import setup, Executable

modules = [
    "tkinter", "sqlite3", "datetime",
    "socket", "pickle", "configparser"
]

include_files = ["config.ini"]

executables = [Executable("envio.py", base="Win32GUI")]

setup(
    name="Solicitação SETUP (Envio)",
    version="1.0.0",
    description="Aplicativo para envio de soliticações SETUP.",
    options={
        "build_exe": {
            "packages": modules,
            "include_files": include_files,
            "include_msvcr": True,
        }
    },
    executables=executables
)
