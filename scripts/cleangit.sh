cd ..
git checkout master
git clean -fxd && git reset --hard
git branch | grep -v '^* master$' | xargs git branch -D
git clean -fxd && git reset --hard