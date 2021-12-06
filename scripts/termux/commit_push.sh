cd /storage/emulated/0/.dev/project_mono/
pwd
git checkout develop
git status
git add .
read -p "Commit message: " message
git commit -m "$message"
git push
exit 1