touch /tmp/dependancy_edisio_in_progress
echo 0 > /tmp/dependancy_edisio_in_progress
echo "********************************************************"
echo "*             Installation des dépendances             *"
echo "********************************************************"
apt-get update
echo 50 > /tmp/dependancy_edisio_in_progress
apt-get install -y python-serial python-requests python-pyudev
echo 100 > /tmp/dependancy_edisio_in_progress
echo "********************************************************"
echo "*             Installation terminée                    *"
echo "********************************************************"
rm /tmp/dependancy_edisio_in_progress