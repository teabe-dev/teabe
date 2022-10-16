#!/bin/bash

PROJECT=teabe
PY_VERSION=3.10

cd ..
VENV_DIR=venv_$PROJECT
VERSION=$(python$PY_VERSION -V 2>&1)
echo $VERSION

case $VERSION in (*"Python $PY_VERSION"*)
        echo exist python $PY_VERSION
    ;;
(*)
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt install python$PY_VERSION -y
;;esac

sudo apt install python$PY_VERSION-venv -y
sudo apt install libpython$PY_VERSION-dev -y

if [ ! -d "$VENV_DIR" ]; then
    python$PY_VERSION -m venv $VENV_DIR
fi

cd $PROJECT

. ../$VENV_DIR/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

# sudo apt install memcached -y
# sudo apt install rabbitmq-server -y
# sudo apt install redis -y
# python manage.py makemigrations
# python manage.py migrate

