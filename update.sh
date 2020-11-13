ID=$(ps aux | grep python | grep main.py | awk '{ print $2 }')
if [ -z "$ID" ]
then
  sudo kill $ID
fi

ID=$(ps aux | grep python | grep server.py | awk '{ print $2 }')
if [ -z "$ID" ]
then
  sudo kill $ID
fi

cd /home/pi/pi-ink-newsframe && git fetch -a && git reset --hard origin/master && chown pi.pi -R *

# python3 /home/pi/pi-ink-newsframe/main.py & 
# python3 /home/pi/pi-ink-newsframe/server.py & 
