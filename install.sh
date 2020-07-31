echo "Updating system..."
sudo apt-get update && sudo apt-get upgrade -y
echo "Enabling spi..."
sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
echo "Installing ImageMagick"
sudo apt-get install imagemagick -y
echo "Enabling PDF rendering"
sudo sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/g' /etc/ImageMagick-6/policy.xml
echo "Installing spidev..."
pip3 install spidev

echo "Reboot required..."
echo "Wait 5 seconds for reboot, or ctrl-c to cancel"
sleep 5
sudo shutdown -r now
