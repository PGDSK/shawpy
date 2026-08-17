#!/bin/bash

qdbus org.kde.ActivityManager /ActivityManager/Activities \
org.kde.ActivityManager.Activities.SetCurrentActivity \
284c05c2-88db-47bc-bf80-627d1610ebba

powerprofilesctl set power-saver

kscreen-doctor \
    output.1.brightness.40 \
    output.2.brightness.40 \
    output.3.brightness.40

night=$(qdbus org.kde.KWin /org/kde/KWin/NightLight org.kde.KWin.NightLight.running)

if [ "$night" = "false" ]; then
    qdbus org.kde.kglobalaccel /component/kwin \
        org.kde.kglobalaccel.Component.invokeShortcut "Toggle Night Color"
fi
