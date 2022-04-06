import sys
import time
import binascii

import tb as traceback
import javascript

from browser import document, html, window, console, bind, websocket
import browser.widgets.dialog as dialog
import turtle


def reset_src():
    if "code" in document.query:
        code = document.query.getlist("code")[0]
        editor.setValue(code)
    else:
        if storage is not None and "py_src" in storage:
            editor.setValue(storage["py_src"])
        else:
            editor.setValue("for i in range(10):\n\tprint(i)")
        if "py_test" in storage and "files" in document:
            document["files"].selectedIndex = int(storage["py_test"])
    editor.scrollToRow(0)
    editor.gotoLine(0)


def reset_src_area():
    if storage and "py_src" in storage:
        editor.value = storage["py_src"]
    else:
        editor.value = "for i in range(10):\n\tprint(i)"


def reset_editor():
    if has_ace:
        reset_src()
    else:
        reset_src_area()


def reset_turtle():
    turtle.restart()
    turtle.set_defaults(turtle_canvas_wrapper=document['turtle-div'])
    

# Run the script
def btn_run_click(*args):
    document["console"].value = ""
    src = editor.getValue()
    if storage is not None:
        storage["py_src"] = src

    reset_turtle()
    
    t0 = time.perf_counter()
    try:
        ns = {"__name__": "__main__"}
        exec(src, ns)
        state = 1
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        state = 0
    sys.stdout.flush()

    print("<completed in %6.2f ms>" % ((time.perf_counter() - t0) * 1000.0))
    
    return state


# Clear output and restart turtle
def btn_clear_click(*args):
    document["console"].value = ""
    reset_turtle()


class cOutput:
    encoding = "utf-8"

    def __init__(self):
        self.cons = document["console"]
        self.buf = ""

    def write(self, data):
        self.buf += str(data)

    def flush(self):
        self.cons.value += self.buf
        self.buf = ""

    def __len__(self):
        return len(self.buf)


# console.log(window.M)

# from interpreter import Interpreter
# Interpreter(globals=globals())

# set height of editor_container to 80% of screen
_height = document.documentElement.clientHeight
document["editor"].style.height = f"{int(_height * 0.80)}px"
document["console"].style.height = f"{int(_height * 0.80)}px"
document["turtle-div"].style.height = f"{int(_height * 0.80)}px"

try:
    editor = window.ace.edit("editor")
    editor.setTheme("ace/theme/chrome")
    editor.session.setMode("ace/mode/python")
    editor.focus()
    editor.setOptions(
        {
            "enableLiveAutocompletion": True,
            "highlightActiveLine": True,
            "highlightSelectedWord": True,
        }
    )
    
    has_ace = True
except:
    editor = html.TEXTAREA(rows=20, cols=70)
    document["editor"] <= editor

    def get_value():
        return editor.value

    def set_value(x):
        editor.value = x

    editor.getValue = get_value
    editor.setValue = set_value
    
    has_ace = False

# Expose editor to glabal environment, so it can be tuned on the fly
window.editor = editor

if hasattr(window, "localStorage"):
    from browser.local_storage import storage
else:
    storage = None

if "set_debug" in document:
    __BRYTHON__.debug = int(document["set_debug"].checked)


if "console" in document:
    cOut = cOutput()
    sys.stdout = cOut
    sys.stderr = cOut


reset_editor()
reset_turtle()

document["btn_run"].bind("click", lambda *args: btn_run_click())
#document["btn_clear"].bind("click", lambda *args: btn_clear_click())

# Must do window.M.AutoInit() after all html being loaded!
window.M.AutoInit()
