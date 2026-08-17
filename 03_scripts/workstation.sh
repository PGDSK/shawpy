#!/bin/bash

qdbus org.kde.ActivityManager /ActivityManager/Activities \
org.kde.ActivityManager.Activities.SetCurrentActivity \
2377149b-8e23-4537-9ae2-6d49e1854547

powerprofilesctl set balanced

kscreen-doctor \
    output.1.brightness.80 \
    output.2.brightness.80 \
    output.3.brightness.80

night=$(qdbus org.kde.KWin /org/kde/KWin/NightLight org.kde.KWin.NightLight.running)

if [ "$night" = "true" ]; then
    qdbus org.kde.kglobalaccel /component/kwin \
        org.kde.kglobalaccel.Component.invokeShortcut "Toggle Night Color"
fi
