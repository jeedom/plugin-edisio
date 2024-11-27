PROGRESS_FILE=/tmp/dependancy_edisio_in_progress
if [ ! -z $1 ]; then
	PROGRESS_FILE=$1
fi
touch ${PROGRESS_FILE}
echo 0 > ${PROGRESS_FILE}
echo "********************************************************"
echo "*             Installation des dépendances             *"
echo "********************************************************"
echo 50 > ${PROGRESS_FILE}
sudo python3 -m pip install --force-reinstall --upgrade requests pyudev pyserial
echo 100 > ${PROGRESS_FILE}
echo "********************************************************"
echo "*             Installation terminée                    *"
echo "********************************************************"
rm ${PROGRESS_FILE}