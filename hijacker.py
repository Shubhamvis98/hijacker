#!/usr/bin/env python3
# Author Shubham Vishwakarma
# git/twitter: ShubhamVis98

import gi, threading, subprocess, psutil, signal, csv
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib


class AppDetails:
    appname = 'Hijacker'
    appversion = '1.0'
    appinstallpath = '/usr/lib/hijacker'
    # ui = f'{appinstallpath}/hijacker.ui'
    ui = 'hijacker.ui'
    applogo = f'{appinstallpath}/logo.svg'

class Functions:
    def execute_cmd(self, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, cwd=None, bufsize=0):
        proc = subprocess.Popen(cmd.split(), stdout=stdout, stderr=stderr, stdin=stdin, cwd=cwd, bufsize=bufsize)
        return [run.poll(), proc]

    def interrupt_proc(self, proc):
        os.kill(proc.pid, signal.SIGINT)
        GLib.timeout_add(1000, terminate_proc, proc)

    def terminate_proc(self, proc):
        if proc.poll() is None:
            proc.terminate()

    def extract_data(csv_file):
        with open(csv_file, 'r') as f:
            csv_data = f.read()

        aps = []
        clients = {}

        reader = csv.reader(csv_data.splitlines())

        for row in reader:
            if len(row) == 15:
                bssid = row[0].strip()
                channel = row[3].strip()
                auth = row[7].strip()
                essid = row[13].strip()
                clients[bssid] = []
                aps.append([bssid, channel, auth, essid])
            
            if len(row) == 7:
                station = row[0].strip()
                bssid = row[5].strip()
                if bssid != '(not associated)':
                    clients[bssid].append(station)

        return [aps, clients]

class Airodump(Functions):
    def __init__(self, builder):
        builder.get_object('btn_quit').connect('clicked', Gtk.main_quit)
        self.btn_toggle = builder.get_object('btn_toggle')
        self.btn_toggle_img = builder.get_object('btn_toggle_img')
        self.btn_menu = builder.get_object('btn_menu')
        self.tab_airodump = builder.get_object('tab_airodump')
        self.ap_list = builder.get_object("ap_list")

        self.btn_toggle.connect('clicked', self.scan_toggle)
        self.ap_list.set_homogeneous(False)
    
    def run(self):
        pass

    def scan_toggle(self, widget):
        current = self.btn_toggle_img.get_property('icon-name')
        tmp = 'start' if 'stop' in current else 'stop'
        self.btn_toggle_img.set_property('icon-name', f'media-playback-{tmp}')

        if tmp == 'start':
            Functions.get_output

    def add_btn(self):
        button = Gtk.Button(label=f"Button")
        button.set_size_request(-1, 50)
        self.ap_list.pack_start(button, True, True, 0)
        self.ap_list.show_all()

class HijackerGUI(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id="in.fossfrog.hijacker")

    def do_activate(self):
        builder = Gtk.Builder()
        builder.add_from_file(AppDetails.ui)

        # Initialize Functions
        Airodump(builder).run()

        # Get The main window from the glade file
        window = builder.get_object('main')
        window.set_title(AppDetails.appname)
        window.set_default_size(600, 400)

        # Show the window
        window.connect('destroy', Gtk.main_quit)
        window.show_all()

if __name__ == "__main__":
    nh = HijackerGUI().run(None)
    Gtk.main()
