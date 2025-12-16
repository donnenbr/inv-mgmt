#!/bin/bash
app="invmgmt-flask"
sudo docker run -p 5100:80 \
  --name=${app} \
  --env LIL_CUBBY=Matty --env OLD_GUY=Jimbo \
  ${app}
