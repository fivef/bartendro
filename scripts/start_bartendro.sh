#/bin/bash

cd ../ui

# TODO: get uwsgi to work for global lock and for production server 
#uwsgi --socket 192.168.0.26:8000 --protocol=http --enable-threads -w bartendro_server
sudo python bartendro_server.py -t 192.168.0.1
