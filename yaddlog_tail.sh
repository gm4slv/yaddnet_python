#!/bin/bash

DIR=/var/www/html/pages/php/test
INFILE=$DIR/logfile.txt
TMPFILE=$DIR/log.tail

tail -n 200 $INFILE > $TMPFILE

mv $TMPFILE $INFILE
