#!/bin/bash

username=yaroslav
device=KINGSTON32

# echo "Лікування картинки, що посунулася вліво"
# xrandr --newmode "1280x1024_60.00"  109.00  1280 1368 1496 1712  1024 1027 1034 1063 -hsync +vsync
# xrandr --addmode VGA-1 1280x1024_60.00
# xrandr --output VGA-1 --mode 1280x1024_60.00

# echo "Створення скрипта для лікування картинки, що посунулася вліво"
# echo """#!/bin/bash

# xrandr --newmode \"1280x1024_60.00\"  109.00  1280 1368 1496 1712  1024 1027 1034 1063 -hsync +vsync
# xrandr --addmode VGA-1 1280x1024_60.00
# xrandr --output VGA-1 --mode 1280x1024_60.00
# """> ~/.xprofile


sudo apt update -y
sudo apt upgrade -y

mkdir ~/temp
echo "Black Background for Desktop"; sudo cp -v /media/$username/$device/install/blackbackground.jpg /usr/share/xfce4/backdrops/
echo "ico for user"; cp -v /media/$username/$device/install/forXFCE4/.face /home/$username/
echo "Копіювання панелі Redmond7"; echo "Копіювання панелі Redmond7" >>~/temp/scriptlog
cd /media/$username/$device/install/forXFCE4/
sudo cp Redmond\ 7.tar.bz2 /usr/share/xfce4-panel-profiles/layouts/
echo "Копіювання бекапа панелі Redmond7"; echo "Копіювання бекапа панелі Redmond7" >>~/temp/scriptlog
sudo cp Backup_21.06.23_08-45-30.tar.bz2 /usr/share/xfce4-panel-profiles/layouts/

echo 'doublecmd-gtk:'; echo 'doublecmd-gtk:' >>~/temp/scriptlog
sudo apt install -y doublecmd-gtk 2>>~/temp/scriptlog

echo "install gnome-disk-utility"; echo "install gnome-disk-utility" >>~/temp/scriptlog
sudo apt install -y gnome-disk-utility 2>>~/temp/scriptlog

echo "install gnome-calculator"; echo "install gnome-calculator" >>~/temp/scriptlog
sudo apt install -y gnome-calculator 2>>~/temp/scriptlog

sudo apt install -y apt-transport-https wget

echo 'WINE:'; echo 'WINE:' >>~/temp/scriptlog
sudo apt -y install wine 2>>~/temp/scriptlog

echo 'dos2unix:'; echo 'dos2unix:' >>~/temp/scriptlog
sudo apt install -y dos2unix 2>>~/temp/scriptlog

echo 'net-tools:'; echo 'net-tools:' >>~/temp/scriptlog
sudo apt install -y net-tools 2>>~/temp/scriptlog

echo 'ssh:'; echo 'ssh:' >>~/temp/scriptlog
sudo apt install -y ssh 2>>~/temp/scriptlog

echo 'git:'; echo 'git:' >>~/temp/scriptlog
sudo apt install -y git 2>>~/temp/scriptlog

echo 'vlc:'; echo 'vlc:' >>~/temp/scriptlog
sudo apt install -y vlc 2>>~/temp/scriptlog

# echo 'guvcview:'; echo 'guvcview:' >>~/temp/scriptlog
# sudo apt install -y guvcview 2>>~/temp/scriptlog

echo 'ark:'; echo 'ark:' >>~/temp/scriptlog
sudo apt install -y ark 2>>~/temp/scriptlog

# Installing from DEB packages
echo 'google-chrome:'; echo 'google-chrome:' >>~/temp/scriptlog
cd ~/temp/; wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb 2>>~/temp/scriptlog
rm google-chrome-stable_current_amd64.deb

echo 'Skype:'; echo 'Skype:' >>~/temp/scriptlog
wget https://go.skype.com/skypeforlinux-64.deb
sudo apt install -y ./skypeforlinux-64.deb 2>>~/temp/scriptlog
rm skypeforlinux-64.deb

cd /media/$username/$device/install/Programs/

echo 'viber:' >>~/temp/scriptlog
sudo apt install -y ./viber.deb 2>>~/temp/scriptlog

echo 'libqt5gui5:' >>~/temp/scriptlog
sudo apt install -y libqt5gui5 2>>~/temp/scriptlog

echo 'WhatsApp:' >>~/temp/scriptlog
sudo dpkg -i whatsapp-webapp_1.0_all.deb 2>>~/temp/scriptlog

echo 'Unpacking 1C'
7z x 1cv82.7z -o/home/$username/Public/
cp -v /media/$username/$device/install/forXFCE4/Enterprise.desktop ~/Desktop/
chmod 755 ~/Desktop/Enterprise.desktop

echo 'Unpacking JetBrains IDE(s)'
7z x pycharm_community.7z -o/home/$username/Public/
7z x intellij_idea_ce.7z -o/home/$username/Public/
cp -v /media/$username/$device/install/forXFCE4/PyCharm\ CE.desktop ~/Desktop/
cp -v /media/$username/$device/install/forXFCE4/IntelliJ\ IDEA\ CE.desktop ~/Desktop/
chmod 755 ~/Desktop/PyCharm\ CE.desktop
chmod 755 ~/Desktop/IntelliJ\ IDEA\ CE.desktop

# echo 'Unpacking Tor-Browser'
# mkdir /home/$username/Public/tor-browser
# 7z x tor-browser-linux64-12.0_ALL.7z -o/home/$username/Public/tor-browser/

echo 'Installing AIMP5'; echo 'Installing AIMP5' >>~/temp/scriptlog
sudo dpkg -i aimp_5.11-2432_amd64.deb 2>>~/temp/scriptlog

echo "Windows fonts to Linux"
sudo 7z x /media/$username/$device/install/msttcorefonts.7z -o/usr/share/fonts/truetype/
sudo fc-cache -fv

echo "Download and unpack Telegram"
cd /home/$username/Public/
wget https://telegram.org/dl/desktop/linux/tsetup.tar.xz
tar -xf tsetup.tar.xz
rm tsetup.tar.xz

sudo apt update -y 2>>~/temp/scriptlog
sudo apt upgrade -y 2>>~/temp/scriptlog

echo 'Start uninstall/install LibreOffice'
sudo apt remove --purge libreoffice* -y
sudo apt clean -y
sudo apt autoremove -y
cd /media/$username/$device/install/Programs/LibreOffice_7/LibreOffice_7_program/
sudo dpkg -i *.deb
cd /media/$username/$device/install/Programs/LibreOffice_7/LibreOffice_7_langpack_uk
sudo dpkg -i *.deb
cd /media/$username/$device/install/Programs/LibreOffice_7/LibreOffice_7_helppack_uk
sudo dpkg -i *.deb
cd /media/$username/$device/install/Programs/LibreOffice_7/LibreOffice_7_langpack_ru
sudo dpkg -i *.deb
cd /media/$username/$device/install/Programs/LibreOffice_7/LibreOffice_7_helppack_ru
sudo dpkg -i *.deb
echo 'End of install LibreOffice'

echo "Proton VPN"; echo "Proton VPN" >>~/temp/scriptlog
cd /media/$username/$device/install/Programs/
sudo dpkg -i protonvpn-stable-release_1.0.3-2_all.deb
sudo apt update -y
sudo apt install -y protonvpn 2>>~/temp/scriptlog

cd ~/temp/
echo 'Opera:'; echo 'Opera:' >>~/temp/scriptlog
wget -r -l1 -nd -A.deb https://deb.opera.com/opera-stable/pool/non-free/o/opera-stable/
sudo dpkg -i *.deb 2>>~/temp/scriptlog
rm *.deb

sudo apt clean -y
sudo apt autoremove -y
