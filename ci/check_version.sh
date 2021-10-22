#!/usr/bin/env sh

# Script to check if app version has been bumped
# To be used with Merge Request CI checks

set -e

VERSION_FILE="ci/build.env"

git fetch origin
if ! git diff --unified=0 origin/master.. -- $VERSION_FILE | grep '^[+-]' | grep -i "version" >/dev/null
then
  printf 'Version check \e[1;31mFAILED!! \e[0mBump the version and update your branch\n'
  exit 1
else
  printf 'Version check \e[1;32mPASSED\e[0m\n'
fi