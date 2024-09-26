#!/bin/bash

#Colour Output
RED="\033[01;31m"
BOLD="\033[01;01m"
RESET="\033[00m"

banner()
{
clear
cat <<'eof'
    __    _   _            __            
   / /_  (_) (_)___ ______/ /_____  _____
  / __ \/ / / / __ `/ ___/ //_/ _ \/ ___/
 / / / / / / / /_/ / /__/ ,< /  __/ /    
/_/ /_/_/_/ /\__,_/\___/_/|_|\___/_/     
       /___/                             

eof
echo -e "\n${BOLD}Developer: Shubham Vishwakarma${RESET}"
echo -e "${BOLD}Git: ShubhamVis98${RESET}"
echo -e "${BOLD}Web: https://fossfrog.in${RESET}"
echo -e '____________________________________________________________________\n'
}

banner

[ `id -u` -ne 0 ] && echo -e "${RED}[!]Run as root${RESET}" && exit 1

install_dir='/usr/lib/in.fossfrog.hijacker'
desktop_file='/usr/share/applications/hijacker.desktop'
icon_path='/usr/share/icons/hicolor/scalable/apps/in.fossfrog.hijacker.svg'

case $1 in
	install)
		mkdir -v $install_dir
		cp -rv hijacker /usr/bin
		cp -rv `basename $icon_path` $icon_path
		cp -rv hijacker.py hijacker.ui $install_dir
		cp -v hijacker.desktop $desktop_file
		chown root:root -R $install_dir
		chmod 644 $desktop_file
		chmod +x $install_dir/hijacker.py /usr/bin/hijacker
		gtk-update-icon-cache /usr/share/icons/hicolor

		echo '[+]Installation Completed'
		;;
	uninstall)
		[ ! -d $install_dir ] && echo "Hijacker not found." && exit
		rm -v $icon_path
		rm -vrf $install_dir
		rm -v $desktop_file
		rm -v /usr/bin/hijacker

		echo '[+]Removed'
		;;
	*)
		echo -e "${RED}Usage:${RESET}"
		echo -e "\t$0 install"
		echo -e "\t$0 uninstall"
esac
