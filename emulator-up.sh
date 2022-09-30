#!/bin/bash -i
#uing shebang with -i to enable interactive mode (auto load .bashrc)
#this script was inspired from https://docs.travis-ci.com/user/languages/android/
set -e #stop immediately if any error happens

avd_name=$1

if [[ -z "$avd_name" ]]; then
  avd_name="avd31"
fi

#check if emulator work well
emulator -version

# create virtual device, default using Android 12 Pie image (API Level 31)
echo no | avdmanager create avd --force -n avd31 -k "system-images;android-31;google_apis;x86_64"

# start the emulator
emulator -avd avd31 -no-audio -no-window -no-accel -qemu & > ./emulator_out.txt &

# show connected virtual device
adb devices
