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

read -r -p "Would you like to automatically install all dependencies including pyinstaller needed? (Y/N)" depsYN
if [[ "$depsYN" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo "----------------------------------------------------------"
    pip install firebase_admin python_jwt gcloud sseclient pycrypto requests-toolbelt pyinstaller
    echo "----------------------------------------------------------"
else
    # N/A
    echo "----------------------------------------------------------"
fi

read -r -p "Would you like to proceed with the build (Y/N)?" buildYN
if [[ "$buildYN" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo "----------------------------------------------------------"
    echo "Executing build now..."
    echo "----------------------------------------------------------"
    debuild -k"B38C0477254E8B3D595DC3AD79C942F56CE04B00" -S 
else
    echo "----------------------------------------------------------"
    echo "Qutting script now..."
    echo "----------------------------------------------------------"
    exit 1
fi

exit 1