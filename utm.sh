# sudo mount -t davfs http://127.0.0.1:9843 /media/shared
mkdir -p ~/git/nodesynth
cp -r . ~/git/nodesynth/
chmod +x ~/git/nodesynth
sudo rm /usr/local/bin/nodesynth
sudo ln -s ~/git/nodesynth/nodesynth.sh /usr/local/bin/nodesynth
