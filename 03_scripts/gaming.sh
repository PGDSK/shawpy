#!/bin/bash

qdbus org.kde.ActivityManager /ActivityManager/Activities org.kde.ActivityManager.Activities.SetCurrentActivity 55420184-615d-4d8f-ad23-5f70aad9669c

powerprofilesctl set performance

kscreen-doctor output.1.brightness.100 output.2.brightness.100 output.3.brightness.100

night=$(qdbus org.kde.KWin /org/kde/KWin/NightLight org.kde.KWin.NightLight.running)

if [ "$night" = "true" ]; then
    qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut "Toggle Night Color"
fi
