
# Dataflow Automation

## Project Overview

This project enables **bulk operations** on Gmail, Discord, and potentially other platforms, using **advanced data filtering techniques** powered by **nuShell**, which is known for its robust data manipulation capabilities.

### Key Features:
- **Plugin for nuShell**: This project extends nuShell functionality.
- **Web Scraping**: Utilizes nuShell's piping features to scrape web pages.
- **Caching Techniques**: Reduces bandwidth and latency through intelligent caching mechanisms.

For more information on nuShell and its plugin capabilities, refer to the [nuShell Documentation](https://www.nushell.sh/book/plugins.html).

---

## System Requirements

The system configuration I am currently using.:
- **Operating System**: Linux
- **Display Server**: Wayland
- **Shell**: nuShell
- **Browser**: Chromium

---

## Project Setup and Execution

### 1. Start Chromium with Remote Debugging:

Open a terminal and run the following command:


`chromium --enable-features=UseOzonePlatform,WebRTCPipeWireCapturer --ozone-platform=wayland --remote-debugging-port=9222 & disown`


This command starts Chromium with the specified debugging port.

### 2. Set Up nuShell:

In a new terminal session, navigate to your project directory and run the locked version of nuShell:

`./nu-0.78.0-x86_64-unknown-linux-gnu/nu`

### 3. Register Plugins:

To enable Gmail or Discord functionality, register the respective plugin by running:

`register nu_plugin_discord.py` or `register nu_plugin_gmail.py`

Once registered, you can execute the rest of the nuShell commands as required.

---


## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/avinashkrishna07/dataflow-automation/blob/main/LICENSE) file for more details.

