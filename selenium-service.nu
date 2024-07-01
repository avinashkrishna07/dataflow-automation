#!/usr/bin/env nu

let CHROME_EXECUTABLE = ($env.CHROME_EXECUTABLE? | default "chromium")
^$CHROME_EXECUTABLE --remote-debugging-port=9222
