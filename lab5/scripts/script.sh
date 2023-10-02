#!/bin/bash
sudo yum install npm -y
sudo mkdir /var/application/
cd /var/application
sudo mkidr portfolio

sudo aws s3 sync s3://thedarksoul/portfolio/ /var/application/portfolio/
cd portfolio

sudo npm install
sudo node app