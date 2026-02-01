#!/bin/sh
WORKDIR=/www/htdocs/${USER##*\-}/cloud.hufak.net
echo $WORKDIR
cd $WORKDIR && rmdir tmp && php updater/updater.phar && echo "opcache.file_cache_only=0" >> .user.ini
mkdir tmp

