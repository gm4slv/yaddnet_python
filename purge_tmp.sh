#!/bin/bash

find /var/www/html/pages/php/test/tmp/ -type f -mmin +30  -exec rm -f {} \;
