#!/usr/bin/env python3
# Author: Shubham Vishwakarma
# git/twitter: ShubhamVis98

import gi, threading, subprocess, psutil, signal, csv, os, glob, time
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib


class AppDetails:
    name = 'Hijacker'
    version = '1.0'
    # install_path = '/usr/lib/hijacker'
    install_path = '.'
    ui = f'{install_path}/hijacker.ui'
    applogo = 'in.fossfrog.hijacker'

class Functions:
    def set_app_theme(theme_name, isdark=False):
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-theme-name", theme_name)
        settings.set_property("gtk-application-prefer-dark-theme", isdark)

    def execute_cmd(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, cwd=None, bufsize=0):
        proc = subprocess.Popen(cmd.split(), stdout=stdout, stderr=stderr, stdin=stdin, cwd=cwd, bufsize=bufsize)
        return proc

    def interrupt_proc(proc):
        os.kill(proc.pid, signal.SIGINT)
        while proc.poll() is None:
            pass

    def terminate_proc(proc):
        if proc.poll() is None:
            proc.terminate()

    def extract_data(csv_file='_tmp-01.csv'):
        while not os.path.exists(csv_file):
            pass
        with open(csv_file, 'r') as f:
            csv_data = f.read()

        aps = []
        clients = {}

        reader = csv.reader(csv_data.splitlines())

        for row in reader:
            if len(row) == 15:
                bssid = row[0].strip()
                channel = row[3].strip()
                enc = row[5].strip()
                pwr = row[8].strip()
                essid = row[13].strip()
                clients[bssid] = []
                vendor = subprocess.Popen(f"macchanger -l | grep -i {bssid[:8]} | cut -d '-' -f3", shell=True, stdout=subprocess.PIPE).communicate()[0].decode().strip()
                if not vendor:
                    vendor = 'Unknown Manufacturer'
                aps.append([bssid, channel, enc, pwr, essid, vendor])
            
            if len(row) == 7:
                station = row[0].strip()
                bssid = row[5].strip()
                if bssid != '(not associated)':
                    clients[bssid].append(station)

        return [aps, clients]

    def remove_files(name='_tmp'):
        for filename in glob.glob(f'{name}*'):
            if os.path.isfile(filename):
                os.remove(filename)
                print(f"Deleted: {filename}")

class WifiRow(Gtk.ListBoxRow):
    def __init__(self, bssid, ch, sec, pwr, ssid, manufacturer):
        super(WifiRow, self).__init__()
        self.bssid = bssid
        self.ch = ch
        self.sec = sec
        self.pwr = pwr
        self.ssid = ssid
        self.manufacturer = manufacturer

        # Create a button to hold the row content
        button = Gtk.Button()
        button.connect("clicked", self.on_button_clicked)

        # Main container inside the button
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button.add(hbox)

        # Icon
        icon = Gtk.Image.new_from_icon_name("network-wireless", Gtk.IconSize.MENU)
        hbox.pack_start(icon, False, False, 0)

        # Details Box
        details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        hbox.pack_start(details_box, True, True, 0)

        # First Line: SSID, BSSID, Manufacturer
        ssid_label = Gtk.Label(label=f"<b>{ssid}</b>", use_markup=True, xalign=0)
        manufacturer_label = Gtk.Label(label=manufacturer, xalign=1)
        first_line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        first_line.pack_start(ssid_label, True, True, 0)
        first_line.pack_start(manufacturer_label, False, False, 0)
        details_box.pack_start(first_line, False, False, 0)

        # Second Line: Power, Security, Channel
        bssid_label = Gtk.Label(label=bssid, xalign=0)
        pwr_label = Gtk.Label(label=f"PWR: {pwr}", xalign=0)
        sec_label = Gtk.Label(label=f"SEC: {sec}", xalign=0)
        ch_label = Gtk.Label(label=f"CH: {ch}", xalign=0)
        # other_label = Gtk.Label(label=other, xalign=0)
        second_line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        second_line.pack_start(bssid_label, True, True, 0)
        second_line.pack_start(pwr_label, True, True, 0)
        second_line.pack_start(sec_label, True, True, 0)
        second_line.pack_start(ch_label, True, True, 0)
        details_box.pack_start(second_line, False, False, 0)

        # Add the button to the ListBoxRow
        self.add(button)

    def on_button_clicked(self, widget):
        # Handle the button click event
        print(f"Clicked on SSID: {self.ssid}, BSSID: {self.bssid}, Manufacturer: {self.manufacturer}, PWR: {self.pwr}, SEC: {self.sec}, CH: {self.ch}")


class Airodump(Functions):
    def __init__(self, builder):
        Functions.set_app_theme("Adwaita", True)
        self.builder = builder
        self.builder.get_object('btn_quit').connect('clicked', self.quit)
        self.btn_toggle = builder.get_object('btn_toggle')
        self.btn_toggle_img = builder.get_object('btn_toggle_img')
        self.btn_menu = builder.get_object('btn_menu')
        self.tab_airodump = builder.get_object('tab_airodump')
        self.ap_list = builder.get_object("ap_list")

        self.btn_toggle.connect('clicked', self.scan_toggle)
        self.ap_list.set_homogeneous(False)
        self.listbox = Gtk.ListBox()

        self.builder.get_object('btn_about').connect('clicked', self.show_about)
    
    def run(self):
        pass

    def quit(self, widget):
        self._stop_signal = 1
        Gtk.main_quit()

    def show_about(self, widget=None):
        about_win = self.builder.get_object('about_dialog')
        about_win.connect('response', self.on_active_response)
        about_win.set_title(AppDetails.name)
        about_win.set_version(AppDetails.version)
        # about_win.set_default_size(400, 500)
        # about_win.set_size_request(400, 500)
        about_win.run()

    def on_active_response(self, dialog, response_id):
        dialog.hide()

    def scan_toggle(self, widget):
        current = self.btn_toggle_img.get_property('icon-name')
        if 'start' in current:
            Functions.remove_files()
            self.proc = Functions.execute_cmd('airodump-ng -w _tmp --write-interval 1 --output-format csv,pcap --background 1 wlan1')
            self.proc = Functions.execute_cmd('ls')
            self.btn_toggle_img.set_property('icon-name', 'media-playback-stop')
            self._stop_signal = 0
            threading.Thread(target=self.watchman).start()

            for child in self.listbox.get_children():
                self.listbox.remove(child)
            self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
            self.ap_list.pack_start(self.listbox, False, False, 0)
            self._tmp_aplist = []
        else:
            self._stop_signal = 1
            Functions.interrupt_proc(self.proc)
            self.btn_toggle_img.set_property('icon-name', 'media-playback-start')

    def add_btn(self):
        button = Gtk.Button(label=f"Button")
        button.set_size_request(-1, 50)
        self.ap_list.pack_start(button, True, True, 0)
        self.ap_list.show_all()

    def watchman(self):
        while True:
            if self._stop_signal:
                break
            time.sleep(1)

            aps, clients = Functions.extract_data()
            print(f'APS: {aps}\nClients: {clients}')

            networks = Functions.extract_data()[0][1:]
            for network in networks:
                if network[0] not in self._tmp_aplist:
                    row = WifiRow(*network)
                    self.listbox.add(row)
                    self._tmp_aplist.append(network[0])
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
        main_window = builder.get_object('hijacker_window')
        main_window.set_title(AppDetails.name)
        main_window.set_default_size(400, 500)
        main_window.set_size_request(400, 500)

        # Show the main_window
        main_window.connect('destroy', Gtk.main_quit)
        main_window.show_all()

if __name__ == "__main__":
    nh = HijackerGUI().run(None)
    Gtk.main()
