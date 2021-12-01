cd /storage/emulated/0/project_mono/
pwd
git checkout develop
git status
git add .
read -p "Commit message: " message
git commit -m "$message"
git push
exit 1

LDFLAGS="-L/system/lib/" CFLAGS="-I/data/data/com.termux/files/usr/include/" pipenv install Pillow