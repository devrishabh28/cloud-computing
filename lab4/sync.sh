#!/bin/bash
sudo yum install httpd -y
sudo service httpd start
sudo aws s3 sync s3://thedarksoul/website/ /var/www/html/