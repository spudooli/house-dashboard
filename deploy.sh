#!/bin/bash

echo "Copying the app..."

cp /home/dave/Sites/house-dashboard/app.py /var/www/dashboard.spudooli.com/


echo "Deploying the static assets..."

cp /home/dave/Sites/house-dashboard/static/* /var/www/dashboard.spudooli.com/static/

echo "Deploying the templates..."
cp /home/dave/Sites/house-dashboard/templates/* /var/www/dashboard.spudooli.com/templates/*

echo "Done"
