#/usr/bin/env bash -e

if [ ! -e "./config.ini" ]; then
    cp config.ini.default config.ini
fi

VENV=venv

if [ ! -d "$VENV" ]
then

    PYTHON=`which python3.7`

    if [ ! -f $PYTHON ]
    then
        echo "Could not find Python 3.7"
    fi
    virtualenv -p $PYTHON $VENV

fi

. $VENV/bin/activate

pip3 install -r requirements.txt
