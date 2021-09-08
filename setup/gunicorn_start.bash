#!/bin/bash
# If you use a username other than 'ubuntu' then substitute it where it is used in this file.

NAME="bitcoinExchange"
DJANGODIR=/home/ubuntu/start2impact_exchange/bitcoinExchange
SOCKFILE=/home/ubuntu/start2impact_exchange/venv/run/gunicorn.sock
USER=ubuntu
GROUP=ubuntu
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=bitcoinExchange.settings
DJANGO_WSGI_MODULE=bitcoinExchange.wsgi
echo "Starting $NAME as `whoami`"


cd $DJANGODIR
source /home/ubuntu/start2impact_exchange/venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
