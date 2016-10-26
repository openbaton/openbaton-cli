#!/bin/bash

unset OB_NFVO_IP
unset OB_NFVO_PORT
unset OB_NFVO_PORT
unset OB_USERNAME
unset OB_PASSWORD

export OB_NFVO_IP=localhost
export OB_NFVO_PORT=8080
export OB_PROJECT_ID=1aac4c60-48df-46ba-a362-bd41b69beeb2
export OB_USERNAME=admin
echo -n Insert Open Baton Password: 
read -s password
export OB_PASSWORD=$password
