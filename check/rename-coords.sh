#!/bin/bash

for NC_FILE in *.nc
do
    ncrename -h -O -d lon,longitude $NC_FILE
    ncrename -h -O -d lat,latitude $NC_FILE
    ncrename -h -O -v lon,longitude $NC_FILE
    ncrename -h -O -v lat,latitude $NC_FILE
done

