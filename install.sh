echo "Updating system..."
sudo apt-get update && sudo apt-get upgrade -y
echo "Enabling spi..."
sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
echo "Installing ImageMagick"
sudo apt-get install imagemagick -y
sudo sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/g' /etc/ImageMagick-6/policy.xml

pip3 install spidev
sudo shutdown -r now
