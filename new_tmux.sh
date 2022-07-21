#!/bin/sh

session="YaDDNet"

tmux start-server

tmux new-session -d -s $session 

tmux rename-window "YaDDNET"

tmux selectp -t 0
tmux send-keys "/usr/bin/python /home/gm4slv/yaddnet/yadd_udp.py" C-m


tmux splitw -h -p 50
tmux send-keys "/usr/bin/python /home/gm4slv/yaddnet/dscd_udp.py" C-m

tmux selectp -t 0 -P 'fg=colour3'
tmux selectp -t 1 -P 'fg=colour3'

#tmux attach-session -t $session

