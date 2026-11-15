# COPYRIGHT (C) akettunen 2026
# imports
import turtle
import math
import time
import colorsys
import ctypes
import sys

# screen
screen = turtle.Screen()
screen.title("Loading...")
screen.bgcolor("black")
screen.setup(width=600, height=600)
screen.tracer(0)

# rm white edges (canvas)
root = screen._root
canvas = screen.getcanvas()
raw = canvas._canvas
root.config(bg="black")
canvas.config(bg="black", highlightthickness=0, bd=0)
raw.config(bg="black", highlightthickness=0, bd=0)
root.update()

# title bar to dark (only on windows)
if sys.platform == "win32":
    try:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
    except Exception:
        pass

# clean exit
running = True
def on_close():
    global running
    running = False
root.protocol("WM_DELETE_WINDOW", on_close)

# cube data
POINTS = [
    (-100, -100, -100), (100, -100, -100),
    (100, 100, -100),   (-100, 100, -100),
    (-100, -100, 100),  (100, -100, 100),
    (100, 100, 100),    (-100, 100, 100),
]

# one polyline
PATH = [0, 1, 2, 3, 0, 4, 5, 1, 5, 6, 2, 6, 7, 3, 7, 4]

# single line item (updates every frame)
line = raw.create_line(*([0] * (len(PATH) * 2)),
                       width=2, fill="#ff0000",
                       capstyle="round", joinstyle="round")

def main():
    cos, sin = math.cos, math.sin
    hsv_to_rgb = colorsys.hsv_to_rgb
    coords = raw.coords
    itemconfig = raw.itemconfig
    update = root.update
    clock = time.perf_counter

    start = last = clock()
    frames = 0
    last_color = ""

    while running:
        now = clock()
        t = now - start

        # same speed at any FPS
        rad = math.radians(t * 60)        
        c, s = cos(rad), sin(rad)
        hue = (t * 0.17) % 1.0            # rnbw cycle (hue)

        # rotate y
        proj = []
        for x, y, z in POINTS:
            z2 = -x * s + z * c
            f = 500 / (500 + z2)
            proj.append((x * c + z * s) * f)
            proj.append(-y * f)

        flat = []
        for i in PATH:
            flat.append(proj[i * 2])
            flat.append(proj[i * 2 + 1])
        coords(line, *flat)

        # only focus on color when it changes
        r, g, b = hsv_to_rgb(hue, 1, 1)
        color = "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
        if color != last_color:
            itemconfig(line, fill=color)
            last_color = color

        # draw (un capped fps)
        try:
            update()
        except Exception: # windows breaked
            break

        # fps counter
        frames += 1
        if now - last >= 0.01: # fps upd per millisec
            try:
                root.title(f"cubergb - {frames / (now - last):.1f} FPS")
            except Exception:
                break
            frames = 0
            last = now

    try:
        root.destroy()
    except Exception:
        pass

if __name__ == "__main__":
    main()