git checkout master
git clean -fxd && git reset --hard
git checkout master
git branch | grep -v '^* master$' | xargs git branch -D
git clean -fxd && git reset --hard
git update
