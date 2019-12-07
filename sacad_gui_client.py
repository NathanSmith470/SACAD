"""
======================================
Smith Airfoil CAD
SACAD v1.0.0
Scripted by Nathan Smith

======================================
"""

import os, time, webbrowser
from tkinter import *
import numpy as np
import random as rd
import easygui as eg
from program_data import version_info, last_update, tutorial_page_url

# CANVAS VARIABLES
canvas_width = 500
cw_old = 0
canvas_height = 500
ch_old = 0

# PAN AND ZOOM VARIABLES
zoom_factor = 1.00
pan_x = 0
pan_y = 0
cx_old = 0
cy_old = 0

naca4_active = False

# MISC VARIABLES ==============
colors = [
    "red",
    "orange",
    "green",
    "teal",
    "cyan",
    "light blue",
    "purple",
    "magenta",
    "pink"
]

updateTime = time.time()
fdi = ""
line_color = rd.choice(colors)
run = True

# NACA 4-DIGIT VARIABLES =====================================
M = 2 / 100  # Maximum Camber        (from 0 - 9.5)
P = 40 / 100  # Max Camber Position   (from 0 - 90)
T = 12 / 100  # Thiccness             (from 1 - 40)
p = 200 / 20  # Precision            (from 20 - 200)
inv = False
xu = []
yu= []
xl = []
yl = []


# FUNCTIONS ============================================
def donothing():
    print("Nothing...")


def main_loop(event):
    global canvas_width, canvas_height
    time.sleep(1 / 60)
    canvas_width = event.width
    canvas_height = event.height
    root.update_idletasks()
    root.update()
    updateGraph(force=True)


def set_cs_variables():
    global M,P,T,p
    M = 2 / 100
    P = 40 / 100
    T = 12 / 100
    p = 100 / 20


def is_close(ox,oy,tx,ty,d):
    if np.sqrt((tx-ox)**2 + (ty-oy)**2) <= d:
        return True
    else:
        return False


def are_you_sure(after=None, after2=None):
    def save_as(win=None, post=None):
        if "NoneType" not in str(type(win)):
            win.destroy()
        save_as_file = Tk()
        save_as_file.title("Export as...")
        if system_type.startswith("win32"):
            save_as_file.iconbitmap("{}\sacad_icon.ico".format(cur_dir))
        save_as_file.minsize(250, 100)
        save_as_file.maxsize(250, 100)
        sa_cancel_button = Button(save_as_file, text="Cancel", command=lambda: save_as_file.destroy())
        sa_dat_button = Button(save_as_file, text="Export as Dat File",
                               command=lambda: export_as_dat(win=save_as_file, next1=post, next2=after2))
        sa_txt_button = Button(save_as_file, text="Export as Txt File",
                               command=lambda: export_as_txt(win=save_as_file, next1=post, next2=after2))

        sa_cancel_button.grid(row=3, column=0)
        sa_dat_button.grid(row=0, column=0)
        sa_txt_button.grid(row=1, column=0)

    are_you_sure_w = Tk()
    are_you_sure_w.title("Unsaved Data!")
    if system_type.startswith("win32"):
        are_you_sure_w.iconbitmap("{}\sacad_icon.ico".format(cur_dir))
    are_you_sure_w.minsize(350, 100)
    are_you_sure_w.maxsize(350, 100)

    ays_text = Label(are_you_sure_w, text="You have unsaved data.\nWould you like to save first?")
    ays_no_button = Button(are_you_sure_w, text="Don't Save", command=lambda: new_graph(force=True, win=are_you_sure_w))
    ays_cancel_button = Button(are_you_sure_w, text="Cancel", command=are_you_sure_w.destroy)
    ays_yes_button = Button(are_you_sure_w, text="Save", command=lambda: save_as(win=are_you_sure_w, post=after))

    ays_text.grid(row=0, column=1)
    ays_no_button.grid(row=1, column=0)
    ays_cancel_button.grid(row=1, column=1)
    ays_yes_button.grid(row=1, column=2)


def new_graph(force=False, win=None):
    global naca4_active
    if not force:
        if naca4_active:
            are_you_sure(after=clear_data())
        else:
            clear_data()
    else:
        if "NoneType" not in str(type(win)):
            win.destroy()
        clear_data()


def open_graph():
    global xu, yu, xl, yl, fdi, naca4_active
    if naca4_active:
        are_you_sure(after=open_graph, after2=naca4_active)
    else:
        clear_data()
        zoom_pan_reset()
        input_file = eg.fileopenbox("Open:", version_info)
        file = open(input_file, "r+")

        line_index = 1
        while True:
            line_data = file.readline()
            if line_index == 1:
                fdi = line_data.split()[1]
                line_index += 1
                continue
            try:
                line_data = list((float(line_data.split()[0]), float(line_data.split()[1])))
            except ValueError:
                break
            except EOFError:
                break
            except TypeError:
                continue
            finally:

                if line_data[0] == 0 and line_data[1] == 0:
                    xu.append(line_data[0])
                    yu.append(line_data[1])
                    line_index += 1
                    break
                else:
                    xu.append(line_data[0])
                    yu.append(line_data[1])
                    line_index += 1

        while True:
            line_data = file.readline()
            try:
                if line_data == "":
                    break
                line_data = list((float(line_data.split()[0]), float(line_data.split()[1])))
                xl.append(line_data[0])
                yl.append(line_data[1])
            except ValueError:
                break
            except EOFError:
                break
            except TypeError:
                line_index += 1
                continue
            finally:
                line_index += 1

        naca4_active = True
        naca4digit_graph()
        updateGraph(force=True)


def compare(fdi_n, ixu, iyu, ixl, iyl):
    global colors
    color = rd.choice(colors)
    cc_width = 300
    cc_height = 300
    def compare_main(event):
        nonlocal cc_width, cc_height
        cc_width = event.width
        cc_height = event.height
        compare_screen.update_idletasks()
        compare_screen.update()
        compare_updateGraph(force=True)

    def compare_graph():
        nonlocal ixu,iyu,ixl,iyl
        for cxi in range(len(ixu) - 1):
            compare_canvas.create_line(((3 / 4) * cc_width * ixu[cxi] + (cc_width / 8),
                                -(3 / 4) * cc_width * iyu[cxi] + ((1 / 2) * cc_height)),
                               ((3 / 4) * cc_width * ixu[cxi + 1] + (cc_width / 8),
                                -(3 / 4) * cc_width * iyu[cxi + 1] + ((1 / 2) * cc_height)),
                               fill=color)

        compare_canvas.create_line(((3 / 4) * cc_width * ixu[len(ixu) - 1] + (cc_width / 8),
                            -(3 / 4) * cc_width * iyu[len(ixu) - 1] + ((1 / 2) * cc_height)),
                           ((3 / 4) * cc_width * ixl[0] + (cc_width / 8),
                            -(3 / 4) * cc_width * iyl[0] + ((1 / 2) * cc_height)),
                           fill=color)

        for cxi2 in range(len(ixl) - 1):
            compare_canvas.create_line(((3 / 4) * cc_width * ixl[cxi2] + (cc_width / 8),
                                -(3 / 4) * cc_width * iyl[cxi2] + ((1 / 2) * cc_height)),
                               ((3 / 4) * cc_width * ixl[cxi2 + 1] + (cc_width / 8),
                                -(3 / 4) * cc_width * iyl[cxi2 + 1] + ((1 / 2) * cc_height)),
                               fill=color)

    def compare_updateGraph(force=False):
        nonlocal compare_canvas,cc_width, cc_height
        if force:
            # BG
            compare_canvas.create_rectangle(0, 0, cc_width, cc_height, fill="black")
            # AXES
            compare_canvas.create_line((cc_width / 8, 0), (cc_width / 8, cc_height), fill="grey")
            compare_canvas.create_line((0, cc_height / 2), (cc_width, cc_height / 2), fill="grey")
            # INDICATOR
            compare_canvas.create_line((cc_width - 60, 20), (cc_width - 60, 60), fill="cyan")
            compare_canvas.create_line((cc_width - 60, 20), (cc_width - 55, 25), fill="cyan")
            compare_canvas.create_line((cc_width - 60, 20), (cc_width - 65, 25), fill="cyan")

            compare_canvas.create_line((cc_width - 20, 60), (cc_width - 60, 60), fill="red")
            compare_canvas.create_line((cc_width - 20, 60), (cc_width - 25, 55), fill="red")
            compare_canvas.create_line((cc_width - 20, 60), (cc_width - 25, 65), fill="red")
            # INDICATOR TEXT
            compare_canvas.create_text((cc_width - 50, 15), text="y", fill="cyan")
            compare_canvas.create_text((cc_width - 15, 50), text="x", fill="red")

            compare_graph()

        ccw_old = cc_width
        cch_old = cc_height

    def export_as_dat_fc():
        nonlocal fdi_n
        if len(fdi_n) == 0:
            fdi_n = "0000"
        file_save_name = eg.filesavebox("Save As:", version_info, default=str("NACA_" + fdi_n + ".dat"))
        af = open(file_save_name, 'w+')

        af.write("NACA {} Airfoil M={}%, P={}%, T={}{}%".format(fdi_n, fdi_n[0], int(fdi_n[1]) * 10, fdi_n[2], fdi_n[3]))
        af.write("\n")

        for x, y in zip(ixu, iyu):
            line = str(x) + " " + str(y)
            af.write(line)
            af.write("\n")

        for x, y in zip(ixl, iyl):
            line = str(x) + " " + str(y)
            if line != "0.0 0.0":
                af.write(line)
                af.write("\n")
        af.close()

    def export_as_txt_fc():
        nonlocal fdi_n
        if len(fdi_n) == 0:
            fdi_n = "0000"
        file_save_name = eg.filesavebox("Save As:", version_info, default=str("NACA_" + fdi + ".txt"))
        af = open(file_save_name, 'w+')

        xu.reverse()
        yu.reverse()

        for x, y in zip(ixu, iyu):
            line = str(0.0) + " " + str(x) + " " + str(y)
            af.write(line)
            af.write("\n")

        for x, y in zip(ixl, iyl):
            line = str(0.0) + " " + str(x) + " " + str(y)
            if line != "0.0 0.0":
                af.write(line)
                af.write("\n")
        af.close()

    compare_screen = Tk()
    compare_screen.title("NACA " + str(fdi_n))
    if system_type.startswith("win32"):
        compare_screen.iconbitmap("{}\sacad_icon.ico".format(cur_dir))
    compare_screen.minsize(200, 200)
    compare_canvas = Canvas(compare_screen,bg="black")
    compare_canvas.pack(fill=BOTH, expand=YES)

    menubar_c = Menu(compare_screen)
    # FILE MENU ==============================================
    filemenu_c = Menu(menubar_c, tearoff=0)
    filemenu_c.add_command(label="Export as Dat File", command=lambda: export_as_dat_fc())
    filemenu_c.add_command(label="Export as Txt File", command=lambda: export_as_txt_fc())
    filemenu_c.add_separator()
    filemenu_c.add_command(label="Exit", command=lambda: compare_screen.destroy())

    # ORGANIZE MENUBAR ========================================
    menubar_c.add_cascade(label="File", menu=filemenu_c)
    compare_screen.config(menu=menubar_c)

    compare_screen.bind("<Configure>", compare_main)


def naca4digit_get_variables():
    def set_naca4_vars():
        global fdi, M, P, T, p, line_color
        clear_data()
        M = float(mc_entry.get()) / 100
        P = float(mcp_entry.get()) / 100
        T = float(tc_entry.get()) / 100
        p = float(pr_entry.get()) / 20
        naca4digit_calculate()
        naca4digit_graph()
        naca4digit.destroy()
        fdi = str(int(M * 100))[0] + str(int(P * 10))[0] + str(int(T * 100))[0] + str(int(T * 100))[1]
        root.title("{} - {}".format(version_info, "NACA " + str(fdi)))
    naca4digit = Tk()
    naca4digit.title("NACA 4-Digit Generator")
    if system_type.startswith("win32"):
        naca4digit.iconbitmap("{}\sacad_icon.ico".format(cur_dir))
    naca4digit.minsize(425, 130)
    naca4digit.maxsize(425, 130)

    # ADD TEXT FIELDS =========================
    mc_text = Label(naca4digit, text="Maximum Camber (from 0 - 9.5)")
    mcp_text = Label(naca4digit, text="Max Camber Position (from 0 - 90)")
    tc_text = Label(naca4digit, text="Thiccness (from 1 - 40)")
    pr_text = Label(naca4digit, text="Precision (from 20 - 200)")

    # ADD ENTRY FIELDS ========================
    mc_entry = Entry(naca4digit)
    mcp_entry = Entry(naca4digit)
    tc_entry = Entry(naca4digit)
    pr_entry = Entry(naca4digit)

    # ADD BUTTONS =============================
    naca_generate_button = Button(naca4digit, text="Generate", command=lambda : set_naca4_vars())
    naca_cancel_button = Button(naca4digit, text="Cancel", command=lambda: naca4digit.destroy())

    # ORGANIZE ================================
    mc_text.grid(row=0, column=0)
    mcp_text.grid(row=1, column=0)
    tc_text.grid(row=2, column=0)
    pr_text.grid(row=3, column=0)

    mc_entry.grid(row=0, column=1)
    mcp_entry.grid(row=1, column=1)
    tc_entry.grid(row=2, column=1)
    pr_entry.grid(row=3, column=1)

    naca_cancel_button.grid(row=4, column=0)
    naca_generate_button.grid(row=4, column=1)

    naca4digit.update()


def naca4digit_calculate():
    global xu, yu, xl, yl, M, P, T, p, naca4_active

    xc = np.arange(0.0, 1.0, 0.1 / p)

    # CAMBER
    yc = []
    for x in xc:
        if 0.0 <= x < P:
            yc.append((M / P ** 2) * ((2 * P * x) - (x ** 2)))
        elif x >= P:
            yc.append((M / ((1 - P) ** 2)) * (1 - (2 * P) + (2 * P * x) - (x ** 2)))

    # GRADIENT
    dyc = []
    for x in xc:
        if 0.0 <= x < P:
            dyc.append((((2 * M) / (P ** 2)) * (P - x)))
        elif x >= P:
            dyc.append((((2 * M) / ((1 - P) ** 2)) * (P - x)))

    # THICCNESS
    yt = []
    a0 = 0.2969
    a1 = -0.1260
    a2 = -0.3516
    a3 = 0.2843
    a4 = -0.1036
    for x in xc:
        yt.append((T / 0.2) * ((a0 * (x ** 0.5)) + (a1 * x) + (a2 * (x ** 2)) + (a3 * (x ** 3)) + (a4 * (x ** 4))))

    # THETA
    O = []
    for d in dyc:
        O.append(np.arctan(d))

    # UPPER SURFACE
    for x, t, o in zip(xc, yt, O):
        xu.append(x - t * np.sin(o))
    for y, t, o in zip(yc, yt, O):
        yu.append(y + t * np.cos(o))

    # LOWER SURFACE
    for x, t, o in zip(xc, yt, O):
        xl.append(x + t * np.sin(o))
    for y, t, o in zip(yc, yt, O):
        yl.append(y - t * np.cos(o))

    naca4_active = True
    xu.reverse()
    yu.reverse()


def naca4digit_graph():
    global xu, yu, xl, yl, canvas_width, canvas_height, line_color, pan_x, pan_y

    for xi in range(len(xu) - 1):
        canvas.create_line(((3 / 4) * canvas_width / zoom_factor * xu[xi] + (canvas_width / 8) + pan_x,
                            -(3 / 4) * canvas_width / zoom_factor * yu[xi] + ((1 / 2) * canvas_height) + pan_y),
                           ((3 / 4) * canvas_width / zoom_factor * xu[xi + 1] + (canvas_width / 8) + pan_x,
                            -(3 / 4) * canvas_width / zoom_factor * yu[xi + 1] + ((1 / 2) * canvas_height) + pan_y),
                           fill=line_color)

    canvas.create_line(((3 / 4) * canvas_width / zoom_factor * xu[len(xu) - 1] + (canvas_width / 8) + pan_x,
                        -(3 / 4) * canvas_width / zoom_factor * yu[len(xu) - 1] + ((1 / 2) * canvas_height) + pan_y),
                       ((3 / 4) * canvas_width / zoom_factor * xl[0] + (canvas_width / 8) + pan_x,
                        -(3 / 4) * canvas_width / zoom_factor * yl[0] + ((1 / 2) * canvas_height) + pan_y),
                       fill=line_color)

    for xi2 in range(len(xl) - 1):
        canvas.create_line(((3 / 4) * canvas_width / zoom_factor * xl[xi2] + (canvas_width / 8) + pan_x,
                            -(3 / 4) * canvas_width / zoom_factor * yl[xi2] + ((1 / 2) * canvas_height) + pan_y),
                           ((3 / 4) * canvas_width / zoom_factor * xl[xi2 + 1] + (canvas_width / 8) + pan_x,
                            -(3 / 4) * canvas_width / zoom_factor * yl[xi2 + 1] + ((1 / 2) * canvas_height) + pan_y),
                           fill=line_color)


def custom_spline():
    dps = []
    class drag_point:
        def __init__(self,can,x,y):
            self.x = x
            self.y = y
            self.size = 3
            self.color = "lime"
            self.can = can
            self.pan_cs_x = (1/8) * cs_width * 0
            self.pan_cs_y = (1/2) * cs_height * 0
            dps.append(self)

        def draw(self):
            nonlocal cs_width,cs_height
            self.can.create_oval(((3/4)*cs_width * self.x + (1/8)*cs_width - self.size + self.pan_cs_x,-(3/4)*cs_width*self.y + (1/2)*cs_height - self.size + self.pan_cs_y),
                                 ((3/4)*cs_width * self.x + (1/8)*cs_width + self.size + self.pan_cs_x,-(3/4)*cs_width*self.y + (1/2)*cs_height + self.size + self.pan_cs_y),
                                 fill=self.color)
            """self.can.create_oval(((3 / 4) * cs_width * self.x - self.size + self.pan_cs_x,
                                  -(3 / 4) * cs_width * self.y - self.size + self.pan_cs_y),

                                 ((3 / 4) * cs_width * self.x + self.size + self.pan_cs_x,
                                  -(3 / 4) * cs_width * self.y + self.size + self.pan_cs_y),
                                 fill=self.color)"""
    global colors
    color = rd.choice(colors)

    cs_width = 600
    cs_height = 500

    csx_old = 0
    csy_old = 0

    csxu = []
    csyu = []
    csxl = []
    csyl = []

    def cs_init():
        global xu, yu, xl, yl
        nonlocal csxu,csyu,csxl,csyl
        xu = []
        yu = []
        xl = []
        yl = []
        set_cs_variables()
        naca4digit_calculate()
        csxu = xu
        csyu = yu
        csxl = xl
        csyl = yl
        for i in range(len(xu)-1):
            i = drag_point(cs_canvas,xu[i],yu[i])
            i.draw()
        for i in range(len(xl)-1):
            i = drag_point(cs_canvas,xl[i],yl[i])
            i.draw()

    def cs_main(event):
        nonlocal cs_width, cs_height
        time.sleep(1 / 60)
        cs_width = event.width
        cs_height = event.height
        custom_spline_win.update_idletasks()
        custom_spline_win.update()
        cs_updateGraph(force=True)

    def cs_reset():
        nonlocal csxu, csyu, csxl, csyl, dps
        csxu = []
        csyu = []
        csxl = []
        csyl = []
        dps = []
        cs_init()
        cs_updateGraph(force=True)

    def cs_finish():
        global xu, yu, xl ,yl
        xu = csxu
        yu = csyu
        xl = csxl
        yl = csyl
        custom_spline_win.destroy()
        updateGraph(force=True)

    def cs_manual():
        def cs_on_configure(event):
            csm_canvas.configure(scrollregion=csm_canvas.bbox("all"))

        def csm_done():
            nonlocal das, dbs, dps
            for dr in range(len(dps)-1):
                dps[dr].x = float(das[dr].get())
                dps[dr].y = float(dbs[dr].get())
            cs_manual_win.destroy()
            cs_updateGraph(force=True)

        nonlocal dps
        das = []
        dbs = []
        cs_manual_win = Tk()
        cs_manual_win.title("Manual Edit")
        if system_type.startswith("win32"):
            cs_manual_win.iconbitmap("{}\sacad_icon.ico".format(cur_dir))
        cs_manual_win.minsize(500,500)

        csm_canvas = Canvas(cs_manual_win)
        csm_canvas.pack(side=LEFT,fill=BOTH, expand=YES)

        cs_scroll = Scrollbar(cs_manual_win, command=csm_canvas.yview)
        cs_scroll.pack(side=RIGHT, fill=Y)
        csm_canvas.configure(yscrollcommand=cs_scroll.set)
        csm_canvas.bind("<Configure>", cs_on_configure)

        csm_frame = Frame(csm_canvas)
        csm_canvas.create_window((0,0), window=csm_frame, anchor='nw')


        for d in dps:
            for da in range(1):
                da = Entry(csm_frame)
                da.insert(END,str(d.x))
                das.append(da)
            for db in range(1):
                db = Entry(csm_frame)
                db.insert(END,str(d.y))
                dbs.append(db)

        dp_index = 0
        for idp in range(len(dps)-1):
            for i in range(1):
                Label(csm_frame,text="Point #{}".format(idp)).grid(row=idp,column=0)
            for i in range(1):
                Label(csm_frame,text="   |  x:").grid(row=idp,column=1)
                das[idp].grid(row=idp,column=2)
            for i in range(1):
                Label(csm_frame,text="   |  y:").grid(row=idp,column=3)
                dbs[idp].grid(row=idp,column=4)


        # CSM MENU ========================================================================
        csm_menubar = Menu(cs_manual_win)

        # CSM FILE MENU =======================================
        csm_filemenu = Menu(csm_menubar, tearoff=0)
        csm_filemenu.add_command(label="Exit", command=lambda: cs_manual_win.destroy())

        # CSM GENERATE MENU ==================================
        csm_generatemenu = Menu(csm_menubar, tearoff=0)
        csm_generatemenu.add_command(label="Done",command=lambda : csm_done())

        # COMPILE MENU BARS ==================================
        csm_menubar.add_cascade(label="File", menu=csm_filemenu)
        csm_menubar.add_cascade(label="Generate", menu=csm_generatemenu)

        cs_manual_win.config(menu=csm_menubar)
        cs_manual_win.update_idletasks()
        cs_manual_win.update()

    def cs_graph():
        nonlocal csxu,csyu,csxl,csyl,cs_width,cs_height,color

        for dp in dps:
            dp.draw()


        for cxi in range(len(csxu) - 1):
            cs_canvas.create_line(((3 / 4) * cs_width * csxu[cxi] + (cs_width / 8),
                                        -(3 / 4) * cs_width * csyu[cxi] + ((1 / 2) * cs_height)),
                                       ((3 / 4) * cs_width * csxu[cxi + 1] + (cs_width / 8),
                                        -(3 / 4) * cs_width * csyu[cxi + 1] + ((1 / 2) * cs_height)),
                                       fill=color)

        cs_canvas.create_line(((3 / 4) * cs_width * csxu[len(csxu) - 1] + (cs_width / 8),
                                    -(3 / 4) * cs_width * csyu[len(csxu) - 1] + ((1 / 2) * cs_height)),
                                   ((3 / 4) * cs_width * csxl[0] + (cs_width / 8),
                                    -(3 / 4) * cs_width * csyl[0] + ((1 / 2) * cs_height)),
                                   fill=color)

        for cxi2 in range(len(csxl) - 1):
            cs_canvas.create_line(((3 / 4) * cs_width * csxl[cxi2] + (cs_width / 8),
                                        -(3 / 4) * cs_width * csyl[cxi2] + ((1 / 2) * cs_height)),
                                       ((3 / 4) * cs_width * csxl[cxi2 + 1] + (cs_width / 8),
                                        -(3 / 4) * cs_width * csyl[cxi2 + 1] + ((1 / 2) * cs_height)),
                                       fill=color)

        cs_canvas.create_line(((3 / 4) * cs_width * 1 + (cs_width / 8),
                               -(3 / 4) * cs_width * 0 + ((1 / 2) * cs_height)),
                              ((3 / 4) * cs_width * csxl[len(csxl) - 1] + (cs_width / 8),
                               -(3 / 4) * cs_width * csyl[len(csyl) - 1] + ((1 / 2) * cs_height)),
                              fill=color)

        cs_canvas.create_line(((3 / 4) * cs_width * csxu[0] + (cs_width / 8),
                               -(3 / 4) * cs_width * csyu[0] + ((1 / 2) * cs_height)),
                              ((3 / 4) * cs_width * 1 + (cs_width / 8),
                               -(3 / 4) * cs_width * 0 + ((1 / 2) * cs_height)),
                              fill=color)

    def cs_updateGraph(force=False):
        nonlocal cs_canvas, cs_width, cs_height
        cs_width = cs_canvas.winfo_width()
        cs_height = cs_canvas.winfo_height()
        if force:
            # BG
            cs_canvas.create_rectangle(0, 0, cs_width, cs_height, fill="black")
            # AXES
            cs_canvas.create_line((cs_width / 8, 0), (cs_width / 8, cs_height), fill="grey")
            cs_canvas.create_line((0, cs_height / 2), (cs_width, cs_height / 2), fill="grey")
            # INDICATOR
            cs_canvas.create_line((cs_width - 60, 20), (cs_width - 60, 60), fill="cyan")
            cs_canvas.create_line((cs_width - 60, 20), (cs_width - 55, 25), fill="cyan")
            cs_canvas.create_line((cs_width - 60, 20), (cs_width - 65, 25), fill="cyan")

            cs_canvas.create_line((cs_width - 20, 60), (cs_width - 60, 60), fill="red")
            cs_canvas.create_line((cs_width - 20, 60), (cs_width - 25, 55), fill="red")
            cs_canvas.create_line((cs_width - 20, 60), (cs_width - 25, 65), fill="red")
            # INDICATOR TEXT
            cs_canvas.create_text((cs_width - 50, 15), text="y", fill="cyan")
            cs_canvas.create_text((cs_width - 15, 50), text="x", fill="red")

            cs_recalculate()
            cs_graph()


    def cs_recalculate():
        nonlocal csxu, csyu, csxl, csyl
        xun = []
        yun = []
        xln = []
        yln = []
        rc_index = 0
        for pd in dps:
            if len(dps) > 0:
                if rc_index <= len(dps)/2:
                    xun.append(pd.x)
                    yun.append(pd.y)
                elif rc_index > len(dps)/2:
                    xln.append(pd.x)
                    yln.append(pd.y)
            rc_index += 1
        csxu = xun
        csyu = yun
        csxl = xln
        csyl = yln

    def cs_click(event):
        nonlocal csx_old, csy_old
        csx_old = event.x
        csy_old = event.y

    def move_dp(event):
        nonlocal csx_old, csy_old, cs_width, cs_height,dps
        csx = event.x
        csy = event.y
        move_cs_x = (csx - csx_old)
        move_cs_y = (csy - csy_old)
        #print(csx,csy)
        #print(move_cs_x,move_cs_y)

        for d in dps:
            if is_close(csx_old,csy_old,((3 / 4) * cs_width * d.x) + (cs_width / 8), (-(3 / 4) * cs_width * d.y) + ((1 / 2) * cs_height), 15):
                d.color = "yellow"
                d.x += move_cs_x / ((1/2) * cs_width)
                d.y -= move_cs_y / ((3/4) * cs_height)
                d.draw()
            else:
                d.color = "lime"


        csx_old = csx
        csy_old = csy
        cs_updateGraph(force=True)

    custom_spline_win = Tk()
    custom_spline_win.title("Custom Spline Generator")
    if system_type.startswith("win32"):
        custom_spline_win.iconbitmap("{}\sacad_icon.ico".format(cur_dir))
    custom_spline_win.minsize(600,500)
    cs_canvas = Canvas(custom_spline_win,bg="black")
    cs_canvas.pack(fill=BOTH,expand=YES)
    cs_init()
    cs_updateGraph(force=True)
    custom_spline_win.update()

    cs_canvas.bind("<Button-1>",cs_click)
    cs_canvas.bind("<B1-Motion>",move_dp)

    # CS MENU ============================================================================
    cs_menubar = Menu(custom_spline_win)

    # CS FILE MENU =======================================
    cs_filemenu = Menu(cs_menubar,tearoff=0)
    cs_filemenu.add_command(label="Exit",command=lambda : custom_spline_win.destroy())

    # CS GENERATE MENU ===================================
    cs_generatemenu = Menu(cs_menubar,tearoff=0)
    cs_generatemenu.add_command(label="Finish",command=lambda : cs_finish())
    cs_generatemenu.add_separator()
    cs_generatemenu.add_command(label="Manual Edit", command=lambda: cs_manual())
    cs_generatemenu.add_separator()
    cs_generatemenu.add_command(label="Reset", command=lambda : cs_reset())

    # COMPILE MENU BARS ==================================
    cs_menubar.add_cascade(label="File", menu=cs_filemenu)
    cs_menubar.add_cascade(label="Generate", menu=cs_generatemenu)

    custom_spline_win.config(menu=cs_menubar)
    # ====================================================

    custom_spline_win.bind("<Configure>", cs_main)


def invert_foil():
    global yu,yl,inv
    tyu = []
    tyl = []
    for y in yu:
        tyu.append(-y)
    for y in yl:
        tyl.append(-y)
    yu = tyu
    yl = tyl
    inv = not inv
    updateGraph(force=True)


def clear_data():
    global xu, yu, xl, yl, naca4_active
    xu = []
    yu = []
    xl = []
    yl = []
    naca4_active = False
    updateGraph(force=True)


def updateGraph(force=False):
    global canvas_width, canvas_height, naca4_active, pan_x, pan_y, zoom_factor
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    if root == None:
        quit()
    if force:
        # BG
        canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="black")
        # AXES
        canvas.create_line((canvas_width / 8 + pan_x, 0), (canvas_width / 8 + pan_x, canvas_height), fill="grey")
        canvas.create_line((0, canvas_height / 2 + pan_y), (canvas_width, canvas_height / 2 + pan_y), fill="grey")
        # INDICATOR
        canvas.create_line((canvas_width - 60, 20), (canvas_width - 60, 60), fill="cyan")
        canvas.create_line((canvas_width - 60, 20), (canvas_width - 55, 25), fill="cyan")
        canvas.create_line((canvas_width - 60, 20), (canvas_width - 65, 25), fill="cyan")

        canvas.create_line((canvas_width - 20, 60), (canvas_width - 60, 60), fill="red")
        canvas.create_line((canvas_width - 20, 60), (canvas_width - 25, 55), fill="red")
        canvas.create_line((canvas_width - 20, 60), (canvas_width - 25, 65), fill="red")
        # INDICATOR TEXT
        canvas.create_text((canvas_width - 50, 15), text="y", fill="cyan")
        canvas.create_text((canvas_width - 15, 50), text="x", fill="red")
        canvas.create_text((canvas_width - 35, 75), text="y: {}".format(pan_y), fill="white")
        canvas.create_text((canvas_width - 80, 75), text="x: {}".format(pan_x), fill="white")
        canvas.create_text((canvas_width - 60, 90), text="Zoom: {}".format(str(round(1/float(zoom_factor),2))+"x"), fill="white")

        if naca4_active:
            naca4digit_graph()


def zoom_in(event=None):
    global zoom_factor
    zoom_factor /= 1.1
    updateGraph(force=True)


def zoom_out(event=None):
    global zoom_factor
    zoom_factor *= 1.1
    updateGraph(force=True)


def zoom_pan_reset(event=None):
    global zoom_factor, pan_x, pan_y
    zoom_factor = 1
    pan_x = 0
    pan_y = 0
    updateGraph(force=True)


def mouse_zoom(event):
    if event.num == 5 or event.delta == -120:
        zoom_in()
    if event.num == 4 or event.delta == 120:
        zoom_out()


def mouse_click(event):
    global cx_old, cy_old
    cx_old = event.x
    cy_old = event.y


def pan_screen(event):
    global pan_x, pan_y, cx_old, cy_old
    cx = event.x
    cy = event.y
    pan_x += (cx - cx_old)
    pan_y += (cy - cy_old)
    cx_old = cx
    cy_old = cy

    updateGraph(force=True)


def export_as_dat(win=None, next1=None, next2=None):
    global fdi,inv
    if "NoneType" not in str(type(win)):
        win.destroy()
    if len(fdi) == 0:
        fdi = "0000"
    if not inv:
        file_save_name = eg.filesavebox("Save As:", version_info, default=str("NACA_" + fdi + ".dat"))
    else:
        file_save_name = eg.filesavebox("Save As:", version_info, default=str("NACA_" + fdi + "_INVERTED" + ".dat"))
    af = open(file_save_name, 'w+')
    if not inv:
        af.write("NACA {} Airfoil M={}%, P={}%, T={}{}%".format(fdi, fdi[0], int(fdi[1]) * 10, fdi[2], fdi[3]))
    else:
        af.write("NACA {}_INVERTED Airfoil M={}%, P={}%, T={}{}%".format(fdi, fdi[0], int(fdi[1]) * 10, fdi[2], fdi[3]))
    af.write("\n")

    for x, y in zip(xu, yu):
        line = str(x) + " " + str(y)
        af.write(line)
        af.write("\n")

    for x, y in zip(xl, yl):
        line = str(x) + " " + str(y)
        af.write(line)
        af.write("\n")
    af.close()

    if "NoneType" not in str(type(next2)):
        next2 = False
    if "NoneType" not in str(type(next1)):
        next1()


def export_as_txt(win=None, next1=None, next2=None):
    global fdi,inv
    if "NoneType" not in str(type(win)):
        win.destroy()
    if len(fdi) == 0:
        fdi = "0000"
    if not inv:
        file_save_name = eg.filesavebox("Save As:", version_info, default=str("NACA_" + fdi + ".txt"))
    else:
        file_save_name = eg.filesavebox("Save As:", version_info, default=str("NACA_" + fdi + "_INVERTED" + ".txt"))
    af = open(file_save_name, 'w+')

    xu.reverse()
    yu.reverse()

    for x, y in zip(xu, yu):
        line = str(0.0) + " " + str(x) + " " + str(y)
        af.write(line)
        af.write("\n")

    for x, y in zip(xl, yl):
        line = str(0.0) + " " + str(x) + " " + str(y)
        af.write(line)
        af.write("\n")
    af.close()

    if "NoneType" not in str(type(next2)):
        next2 = False
    if "NoneType" not in str(type(next1)):
        next1()


def about():
    about_screen = Tk()
    about_screen.title("About - {}".format(version_info))
    if system_type.startswith("win32"):
        about_screen.iconbitmap("{}\sacad_icon.ico".format(cur_dir))
    about_screen.minsize(300,120)
    about_screen.maxsize(300,120)
    abt_text = Label(about_screen,text="==========================\n{}\nLast Updated on: {}\nPowered by Python, Tkinter, EasyGUI\nScripted by Nathan Smith\nEmail: ns4049@g.rit.edu\n==========================".format(version_info,last_update))
    abt_text.pack()
    about_screen.update()

# PROGRAM INITIALIZATION ================================================================================
system_type = sys.platform
cur_dir = os.getcwd()
root = Tk()
root.title(version_info)
root.minsize(600,500)
if system_type.startswith("win32"):
    root.iconbitmap("{}\sacad_icon.ico".format(cur_dir))

menubar = Menu(root)
# FILE MENU ==============================================
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=lambda : new_graph())
filemenu.add_command(label="Open", command=lambda : open_graph())
filemenu.add_separator()
filemenu.add_command(label="Export as Dat File", command=lambda : export_as_dat())
filemenu.add_command(label="Export as Txt File", command=lambda : export_as_txt())
filemenu.add_separator()
filemenu.add_command(label="Exit", command=lambda : root.destroy())

# VIEW MENU ==============================================
viewmenu = Menu(menubar,tearoff=0)
viewmenu.add_command(label="Zoom In (+)",command=lambda : zoom_in())
viewmenu.add_command(label="Zoom Out (-)",command=lambda : zoom_out())
viewmenu.add_separator()
viewmenu.add_command(label="Reset View (\)",command=lambda : zoom_pan_reset())
viewmenu.add_separator()
viewmenu.add_command(label="Compare",command=lambda : compare(fdi,xu,yu,xl,yl))

# GENERATE MENU ==========================================
generatemenu = Menu(menubar, tearoff=0)
generatemenu.add_command(label="NACA 4-Digit", command=lambda: naca4digit_get_variables())
generatemenu.add_command(label="NACA 5-Digit (WIP)", command=donothing)
generatemenu.add_command(label="Custom Spline", command=lambda : custom_spline())
generatemenu.add_separator()
generatemenu.add_command(label="Invert",command=lambda : invert_foil())
generatemenu.add_separator()
generatemenu.add_command(label="Clear", command=lambda : clear_data())

# HELP MENU ===============================================
helpmenu = Menu(menubar,tearoff=0)
helpmenu.add_command(label="About", command=lambda : about())
helpmenu.add_separator()
helpmenu.add_command(label="Tutorials", command=lambda : webbrowser.open(tutorial_page_url))

# ORGANIZE MENUBAR ========================================
menubar.add_cascade(label="File", menu=filemenu)
menubar.add_cascade(label="View",menu=viewmenu)
menubar.add_cascade(label="Generate", menu=generatemenu)
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)

# SETUP CANVAS =============================================
canvas = Canvas(root,bg="black")
updateGraph()
canvas.pack(fill=BOTH, expand=YES)

# BIND KEYS ================================================

# Both
root.bind("=", zoom_in)
root.bind("-", zoom_out)
root.bind("\\", zoom_pan_reset)
canvas.bind("<Button-1>", mouse_click)
canvas.bind("<B1-Motion>", pan_screen)
# Windows Scroll
root.bind("<MouseWheel>", mouse_zoom)
# Linux Scroll
root.bind("<Button-4>", mouse_zoom)
root.bind("<Button-5>", mouse_zoom)

root.bind("<Configure>", main_loop)

root.mainloop()
