#!/bin/bash

powerprofilesctl set balanced

kscreen-doctor \
    output.1.brightness.80 \
    output.2.brightness.80 \
    output.3.brightness.80
