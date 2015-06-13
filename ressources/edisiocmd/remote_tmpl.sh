#!/bin/sh
data=""
for var in "$@"
do
	data="${data}${var}&"
done	
curl -G -k -s "#ip_master#/plugins/edisio/core/php/jeeEdisio.php" -d "apikey=#apikey#&${data}"
exit 0