from cx_Freeze import setup, Executable

modules = [
    "tkinter", "sqlite3", "datetime",
    "socket", "pickle", "configparser"
    "threading", "bcrypt"
]

include_files = ["config.ini"]

executables = [Executable("recebimento.py", base="Win32GUI")]

setup(
    name="Solicitação SETUP (Recebimento)",
    version="1.0.0",
    description="Aplicativo para recebimento de soliticações SETUP.",
    options={
        "build_exe": {
            "packages": modules,
            "include_files": include_files,
            "include_msvcr": True,
        }
    },
    executables=executables
)
