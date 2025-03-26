#!/bin/sh
cd "/home/diver/Скрипты/tgb/NStgb/"
j=$(date)
git add .
git commit -m "$1 $j"
git push git@github.com:Vladgobelen/NStgb.git

