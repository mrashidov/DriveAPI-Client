from cx_Freeze import setup, Executable

base = None


executables = [Executable("gui_corrected.py", base=base)]
"""
packages = ["idna"]
options = {
    'build_exe': {

        'packages':packages,
    },

}
"""
setup(
    name = "Drive API App",
    version = "6.6.6.6",
    description = 'Simplistic Drive API client. Python 3 based.',
    executables = executables
)