# 1. Install dependencies
sudo yum update
sudo yum install gcc -y
sudo yum install gcc-c++ -y
sudo yum install make -y
sudo yum install autoconf -y
sudo yum install automake -y
sudo yum install libtool -y
sudo yum install libjpeg-devel -y
sudo yum install libpng-devel -y
sudo yum install libtiff-devel -y
sudo yum install zlib-devel -y
sudo yum install mesa-libGL -y
sudo yum install kernel-devel -y
sudo yum install python3 -y

# 2. Compile and install leptonica
cd ~ || exit
mkdir leptonica
cd leptonica || exit
wget http://www.leptonica.org/source/leptonica-1.80.0.tar.gz
tar -zxvf leptonica-1.80.0.tar.gz
cd leptonica-1.80.0 || exit
./configure
make
sudo make install
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig

# 3. Compile and install tesseract
cd ~ || exit
mkdir tesseract
cd tesseract || exit
wget https://github.com/tesseract-ocr/tesseract/archive/4.1.1.tar.gz
tar -zxvf 4.1.1.tar.gz
cd tesseract-4.1.1 || exit
./autogen.sh
./configure
make
sudo make install
sudo ldconfig

# 4. Download trained language data to tessdata
cd /usr/local/share/tessdata || exit
sudo wget https://github.com/tesseract-ocr/tessdata/raw/master/eng.traineddata
# sudo mv -v eng.traineddata /usr/local/share/
export TESSDATA_PREFIX=/usr/local/share/
