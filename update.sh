ID=$(ps aux | grep python | grep main.py | awk '{ print $2 }')
sudo kill $ID
cd /home/pi/pi-ink-newsframe && git pull origin master -f
python3 /home/pi/pi-ink-newsframe/main.py
