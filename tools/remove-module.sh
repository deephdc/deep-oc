#!/bin/bash

set -xe

git config -f .gitmodules --remove-section submodule.$1
git config -f .git/config --remove-section submodule.$1
git add .gitmodules
git rm --cached $1
git commit -m "Remove submodule in $1"
rm -rf $1
rm -rf .git/modules/$1
