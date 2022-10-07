#!/bin/bash

# Customizable variables 
IFS=$'\n'
counter=0
mins_threshold=60

# Log files
ongoing_incidents="ongoing_incidents.log"
cups_log="cups.log"

# Ensure logfiles are available to use
test -e $ongoing_incidents || touch $ongoing_incidents
test -e $cups_log || touch $cups_log

# Variable to filter data from lpstat and to clean date
dt_today=$(date +"%d %b %Y %r")
dt_today_epoch=$(date --date="$dt_today" +%s)
cups_disabled_printers=$(lpstat -p | grep disabled | awk '{ print $2; }')
cups_dates=$(lpstat -p | grep disabled | grep -o 'since.*' | cut -c11- | awk '{$6 = ""; print $0;}' | rev | cut -c4- | rev)

# Correct mismatched printer status/data between lpstat and logs; else retrieve disabled printers where downtime > threshold and save to incident logs
if [ -z "$cups_disabled_printers" ]  && [ ! -s "$ongoing_incidents" ]
then
        > $ongoing_incidents
        echo -e "[INFO] [$dt_today] CUPS PRINTERS OK! | CHECKED by CUPS incident script" >> $cups_log
else
        for dt in $cups_dates
        do
                dt_epoch=$(date --date="$dt" +%s)
                mins_passed=$((($dt_today_epoch - $dt_epoch)/60))
                IFS=$'\n' d_printers=($cups_disabled_printers)

                if (( $mins_passed > $mins_threshold ))
                then
                        grep -qF "${d_printers[$counter]}" "$ongoing_incidents" || echo "OFFLINE: ${d_printers[$counter]} | DOWNTIME: $dt" >> "$ongoing_incidents"
                        echo -e "[OFFLINE] [$dt_today]  Printer: ${d_printers[$counter]} is DISABLED | DOWNTIME: $dt ($mins_passed minutes ago) | Logged to $ongoing_incidents" >> $cups_log
                else
                        echo -e "[OFFLINE] [$dt_today]  Printer: ${d_printers[$counter]} is DISABLED | DOWNTIME: $dt ($mins_passed minutes ago)" >> $cups_log
                fi

                ((counter++))
        done
fi