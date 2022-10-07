#!/bin/bash

# Log files
ongoing_incidents="ongoing_incidents.log"
cups_log="cups.log"

# Ensure logfiles are available to use
test -e $ongoing_incidents || touch $ongoing_incidents
test -e $cups_log || touch $cups_log

# Variable to filter data from lpstat and to clean date
dt_today=$(date +"%d %b %Y %r")
cups_disabled_printers=$(lpstat -p | grep disabled | awk '{ print $2; }')

# Check if printers are up, and no existing data in log file, else enable disabled printers
if [ -z "$cups_disabled_printers" ] && [ ! -s "$ongoing_incidents" ]
then
        > $ongoing_incidents
        echo -e "[INFO] [$dt_today] CUPS PRINTERS OK! | CHECKED by cups self-healing script" >> $cups_log
else
        for printer in $cups_disabled_printers
        do
                cupsenable $printer
                enable_check="$(lpstat -p | grep "$printer" | awk '{ print $5; }')"
                if [[ $enable_check == "enabled" ]]
                then
                        sed -i "/$printer/d" "$ongoing_incidents"
                        echo -e "[ONLINE] [$dt_today]  Printer: $printer OK! | Automatically ENABLED by cups self-healing script" >> $cups_log
                else
                        echo -e "[OFFLINE] [$dt_today]  Printer: $printer is still DISABLED | FAILED | Please Investigate" >> $cups_log
                fi
        done
fi

# Handle manually enabled printers
dp_logs=$(cat "$ongoing_incidents" | awk '{ print $2 }')

if [ ! -z "$dp_logs" ]
then
        for p in $dp_logs
        do
                p_check="$(lpstat -p | grep "$p" | awk '{ print $5; }')"
                if [[ $p_check == "enabled" ]]
                then
                        sed -i "/$p/d" "$ongoing_incidents"
                        echo -e "[ONLINE] [$dt_today]  Printer: $p OK! | Manually ENABLED by user | Removed from $ongoing_incidents" >> $cups_log
                fi
        done
fi