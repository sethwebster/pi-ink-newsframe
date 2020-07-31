
echo "Installing docker."
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker ${USER}
sudo systemctl restart docker
docker pull cjimti/iotwifi
wget https://raw.githubusercontent.com/txn2/txwifi/master/cfg/wificfg.json
sed -i 's/iot-wifi-cfg-3/NewsFrame Config/g' wificfg.json

docker run --rm --privileged --net host \
      -v $(pwd)/wificfg.json:/cfg/wificfg.json \
      cjimti/iotwifi \
      --restart=unless-stopped

echo "Reboot required..."
echo "Wait 5 seconds for reboot, or ctrl-c to cancel"
sleep 5
sudo shutdown -r now
