
Files for running YaDDNEt and Snargate monitor (and dix aprs database)


the Crontab file controls the processes necessary to keep YaDDNet running, 
pruning databases of un-wanted messages etc.

===== CRONTAB ======

15 * * * * /home/gm4slv/yaddnet/purge_err.sh > /dev/null 2>&1
00 */2 * * * /home/gm4slv/yaddnet/purge_ship_unk.sh > /dev/null 2>&1
*/5 * * * * /home/gm4slv/yaddnet/plot_rate.sh > /dev/null 2>&1
#* * * * * /home/gm4slv/bin/webstat.sh > /dev/null 2>&1
45 * * * * /home/gm4slv/bin/yaddlog_tail.sh > /dev/null 2>&1
40 02,14 * * * /home/gm4slv/bin/backup_yadd.sh > /dev/null 2>&1

* * * * * /home/gm4slv/check_monitor.sh
~                                        

===================================================

This is a list of functions not contained in the main ~/yaddnet project

===================================================

Running YaDDNet:

yaddnet is started by an entry in rc.local - running 
under the user "gm4slv" it starts the tmux session that 
then creates 3 windows, one starts "yadd_udp.py" which is
the main YaDD message handling function, one starts "dscd_udp.py"
which handles DSCDecoder UDP messages and the third starts
the Dixaprs udp receiver & database 


=============== /etc/rc.local =====================

sleep 60; su gm4slv -c /home/gm4slv/bin/tmux_yadd.sh &
exit 0


===================================================



============ ~/bin/tmux_yadd.sh =========================

#!/bin/sh

/usr/bin/tmux new-session -d -s YaDDNet

/usr/bin/tmux new-window -t YaDDNet:2 -n 'yUDP' '/usr/bin/python /home/gm4slv/yaddnet/yadd_udp.py'
/usr/bin/tmux new-window -t YaDDNet:3 -n 'dUDP' '/usr/bin/python /home/gm4slv/yaddnet/dscd_udp.py'
/usr/bin/tmux new-window -t YaDDNet:6 -n 'dix' '/usr/bin/python /home/gm4slv/dix_udp.py'

===========================================================


Yaddnet writes all resolver activity (and potentially much more) into a logfile which
will grow indefinitely if not regularly tailed. Cron runs yaddlog_tail to keep the
log at 200 lines.

============= ~/bin/yaddlog_tail.sh =======


#!/bin/bash

DIR=/var/www/html/pages/php/test
INFILE=$DIR/logfile.txt
TMPFILE=$DIR/log.tail

tail -n 200 $INFILE > $TMPFILE

mv $TMPFILE $INFILE

========================================


backup_yadd.sh takes a dump of the yadd SQL database 
twice a day (driven by CRON) and copies it to 
NAS box. Yesterday's local copies are removed from 
the yadd backup directory. This means there is always
a local copy of the recent dumps, and a remote (NAS)
copy of all dumps (unless deleted manually on the NAS box)

========= backup_yadd.sh ===============

#!/bin/bash

DATE=`date +%Y-%m-%d_%H%M%S`
YESTERDAY=`date +%Y-%m-%d -d 'yesterday'`

mysqldump -u root yadd > /home/gm4slv/backup/yadd_$DATE.sql
rsync -av /home/gm4slv/backup/* 192.168.21.5::Backup/

rm -f /home/gm4slv/backup/yadd_$YESTERDAY*.sql

================================================================


check_monitor looks for the existence of the "w2w_monitor" client
if it isn't found (eg it exited due to loss of contact with Snargate)
the script ~/monitor.sh runs to (attempt to) start it again.


============= ~/check_monitor.sh =========


#!/bin/bash

ps auxw | grep w2w  | grep -v grep > /dev/null

if [ $? != 0 ]
then
echo "Not running"
cp /var/www/html/pages/php/test/down.html /var/www/html/pages/php/test/snargate_status.html
/home/gm4slv/monitor.sh
fi


=========================================

monitor.sh creates a new tmux window, attached to the "YaDDNet" session and runs the
w2w_monitor to retrieve status from Snargate.

============ ~/monitor.sh =================


#!/bin/bash
/usr/bin/tmux new-window -t YaDDNet:5 -n 'Snargate' '/usr/bin/python /home/gm4slv/w2w_monitor.py'


==========================================


All the other necessary files should be in the yaddnet project directory. The graph plotting function
writes two *.png files outside the yaddnet directory for copying to the webserver directory.

The files in the "yaddnet" directory shouldn't change while yaddnet is running and are under 
version control by HG, with no default push path they are "pulled" from elsewhere when
necessary to keep the remote clone(s) up to date.


~                   
YaDDNet DSC Message collection, database, website.

    Copyright (C) 2019  John Pumford-Green

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
