#!/bin/bash -x

VERSION=$(grep version setup.py | cut -d\' -f 2)
MAJOR=${VERSION//.*}
MINOR=${VERSION##*.}
if [ "$1" = "-m" ]; then
  MAJOR=$(($MAJOR + 1))
  MINOR="0"
  shift
else
  MINOR=$(($MINOR + 1))
fi
sed -i "s/$VERSION/$MAJOR.$MINOR/g" setup.py
git commit -m "$1" setup.py
git tag "$MAJOR.$MINOR" -m "$1"
git push --tags origin master

python setup.py register -r pypi
python setup.py sdist upload -r pypi --sign
