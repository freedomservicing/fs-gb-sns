# This is a fairly simple installer script.
# In order to use it, you'll need to install pyinstaller
# Do this via pip install pyinstaller (on your system you may need to do pip3 install pyinstaller if you have python 2 installed)
echo "----------------------------------------------------------"
echo "Welcome to the Freedom Gateway GB_SNS Tool Build Script"
echo "----------------------------------------------------------"
echo "This script was authored by Noah"
echo "----------------------------------------------------------"
echo "Please insure that you have installed pyinstaller via the pip command line tool before proceeding"
echo "----------------------------------------------------------"

echo "Deleting previous build metadata"
echo "----------------------------------------------------------"
rm -rf ../fs-gb-sns_*

read -r -p "Would you like to automagically install all python deps? (Y/N)" pyDepsYN
if [[ "$pyDepsYN" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo "----------------------------------------------------------"
    pip3 install firebase_admin python_jwt gcloud sseclient pycrypto requests-toolbelt pyinstaller testresources
    pip3 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip3 install -U 
    echo "----------------------------------------------------------"
else
    # N/A
    echo "----------------------------------------------------------"
fi

read -r -p "Would you like to automagically install all other build deps (apt install) (Y/N)?" ubuntuDepsYN
if [[ "$ubuntuDepsYN" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo "----------------------------------------------------------"
    sudo apt install build-essential fakeroot devscripts debhelper dh-python python3-all python3-pip dput
    echo "----------------------------------------------------------"
else
    echo "----------------------------------------------------------"
fi

read -r -p "Would you like to proceed with the build (Y/N)?" buildYN
if [[ "$buildYN" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo "----------------------------------------------------------"
    echo "Executing build now..."
    echo "----------------------------------------------------------"
    debuild -k"B38C0477254E8B3D595DC3AD79C942F56CE04B00" -S
    echo "----------------------------------------------------------"
else
    echo "----------------------------------------------------------"
fi

read -r -p "Would you like to push to Launchpad (Y/N)?" pushYN
if [[ "$pushYN" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo "----------------------------------------------------------"
    echo "Executing push now..."
    echo "----------------------------------------------------------"
    cd ..
    dput -f ppa:freedomservicing/fs-gb-sns *.changes
fi

echo "----------------------------------------------------------"
echo "Qutting script now..."
echo "----------------------------------------------------------"
exit 1
