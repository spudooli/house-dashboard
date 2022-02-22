#!/bin/bash

echo "Copying the app..."

cp -p /home/dave/Sites/house-dashboard/app.py /var/www/dashboard.spudooli.com/


echo "Deploying the static assets..."

cp -p /home/dave/Sites/house-dashboard/static/* /var/www/dashboard.spudooli.com/static/

echo "Deploying the templates..."
cp -p /home/dave/Sites/house-dashboard/templates/* /var/www/dashboard.spudooli.com/templates/*

echo "Clearing the production cache..."
rm -rf /var/www/dashboard.spudooli.com/__pycache__

echo "Restarting Gunicorn..."
cd /etc/systemd/system/
systemctl restart dashboard.spudooli.com.service

echo "Done"
