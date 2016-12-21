#!/bin/bash -x

VERSION=$(grep version setup.py | cut -d\' -f 2)
MAJOR=${VERSION//.*}
MINOR=${VERSION##*.}
MINOR=$(($MINOR + 1))
sed -i "s/$VERSION/$MAJOR.$MINOR/g" setup.py
git commit -m "$1" setup.py
git tag "$MAJOR.$MINOR" -m "$1"
git push --tags origin master

python setup.py register -r pypi
python setup.py sdist upload -r pypi --sign
