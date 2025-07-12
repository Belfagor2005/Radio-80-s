#!/bin/bash

## setup command=wget -q --no-check-certificate https://raw.githubusercontent.com/Belfagor2005/Radio-80-s/main/installer.sh -O - | /bin/sh

## Only This 2 lines to edit with new version ######
version='1.3'
changelog='\nRecoded tag stream'
##############################################################
TMPPATH=/tmp/Radio-80-s-main
FILEPATH=/tmp/main.tar.gz

if [ ! -d /usr/lib64 ]; then
	PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/RadioM
else
	PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/RadioM
fi

## check depends packges
if [ -f /var/lib/dpkg/status ]; then
   STATUS=/var/lib/dpkg/status
   OSTYPE=DreamOs
else
   STATUS=/var/lib/opkg/status
   OSTYPE=Dream
fi
echo ""

if [ -f /usr/bin/wget ]; then
    echo "wget exist"
else
	if [ $OSTYPE = "DreamOs" ]; then
		echo "dreamos"
		apt-get update && apt-get install wget -y
	else
		opkg update && opkg install wget
	fi
fi

if python --version 2>&1 | grep -q '^Python 3\.'; then
	echo "You have Python3 image"
	PYTHON=PY3
	Packagesix=python3-six
	Packagerequests=python3-requests
else
	echo "You have Python2 image"
	PYTHON=PY2
	Packagerequests=python-requests
fi

if [ $PYTHON = "PY3" ]; then
	if grep -qs "Package: $Packagesix" $STATUS ; then
		echo ""
	else
		echo "Need to install $Packagesix"
		if [ $OSTYPE = "DreamOs" ]; then
			apt-get update && apt-get install $Packagesix -y
		else
			opkg update && opkg install $Packagesix
		fi
	fi
fi
echo ""

if grep -qs "Package: $Packagerequests" $STATUS ; then
	echo ""
else
	echo "Need to install $Packagerequests"
	echo ""
	if [ $OSTYPE = "DreamOs" ]; then
		apt-get update && apt-get install $Packagerequests -y
	elif [ $PYTHON = "PY3" ]; then
		opkg update && opkg install python3-requests
	elif [ $PYTHON = "PY2" ]; then
		opkg update && opkg install python-requests
	fi
fi
echo ""

## Remove tmp directory
[ -r $TMPPATH ] && rm -rf $TMPPATH > /dev/null 2>&1

## Remove tmp file
[ -r $FILEPATH ] && rm -f $FILEPATH > /dev/null 2>&1

## Remove old plugin directory
[ -r $PLUGINPATH ] && rm -rf $PLUGINPATH > /dev/null 2>&1

## Download and install plugin
mkdir -p $TMPPATH
cd $TMPPATH
set -e
if [ $OSTYPE = "DreamOs" ]; then
   echo "# Your image is OE2.5/2.6 #"
   echo ""
else
   echo "# Your image is OE2.0 #"
   echo ""
fi

if [ $OSTYPE != "DreamOs" ]; then
	opkg update && opkg install ffmpeg gstplayer exteplayer3 enigma2-plugin-systemplugins-serviceapp
fi
sleep 2

wget --no-check-certificate 'https://github.com/Belfagor2005/Radio-80-s/archive/refs/heads/main.tar.gz'
tar -xzf main.tar.gz
cp -r 'Radio-80-s-main/usr' '/'
set +e
cd
sleep 2

## Check if plugin installed correctly
if [ ! -d $PLUGINPATH ]; then
	echo "Some thing wrong .. Plugin not installed"
	rm -rf $TMPPATH > /dev/null 2>&1
	exit 1
fi
rm -rf $TMPPATH > /dev/null 2>&1
sync

# Identify the box type from the hostname file
FILE="/etc/image-version"
box_type=$(head -n 1 /etc/hostname)
distro_value=$(grep '^distro=' "$FILE" 2>/dev/null | awk -F '=' '{print $2}')
distro_version=$(grep '^version=' "$FILE" 2>/dev/null | awk -F '=' '{print $2}')
python_vers=$(python --version 2>&1)
echo "#########################################################
#               INSTALLED SUCCESSFULLY                  #
#                developed by LULULLA                   #
#               https://corvoboys.org                   #
#########################################################
#           your Device will RESTART Now                #
#########################################################
^^^^^^^^^^Debug information:
BOX MODEL: $box_type
OO SYSTEM: $OSTYPE
PYTHON: $python_vers
IMAGE NAME: $distro_value
IMAGE VERSION: $distro_version"

sleep 5
killall -9 enigma2
exit 0
