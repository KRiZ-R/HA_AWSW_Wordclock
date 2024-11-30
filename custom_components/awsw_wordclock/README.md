
# AWSW WordClock Integration for Home Assistant

This is a custom integration for controlling the AWSW WordClock using Home Assistant.

## Features
- Control 12 extra words as switches.
- Automatically detects and registers a WordClock device using its IP address.
- Direct link to the WordClock Web Interface for configuration.
- Supports unique entities for each word.

## Requirements
- A working AWSW WordClock with API access enabled.
- https://www.printables.com/model/768062-wordclock-16x16-2024 is the one i use
- Home Assistant version 2024.11 or higher.

## Installation

### Manual Installation
1. Download the latest release from the [Releases](https://github.com/bluenazgul/HA_AWSW_Wordclock/releases) page.
2. Extract the contents and copy the `awsw_wordclock` folder to your `custom_components` directory in Home Assistant.
   - The path should be: `custom_components/awsw_wordclock/`
3. Restart Home Assistant.

### Installation via HACS (Recommended)
1. Add this repository to HACS as a custom repository.
2. Search for "AWSW WordClock" in the HACS store and install it.
3. Restart Home Assistant.

## Setup
1. Go to `Settings > Devices & Services > Add Integration`.
2. Search for "AWSW WordClock".
3. Enter the IP address of your WordClock and click "Submit".

## Usage
- Each of the 12 extra words will appear as switches in Home Assistant.
- You can turn these words on or off directly from the dashboard or use them in automations.
- A direct link to the WordClock Web Interface is available under the device details.

## Troubleshooting
- Ensure the WordClock is reachable and the IP address is correct.
- Check the Home Assistant logs for any errors.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### Credits
Idea by myself, most of the work is done by ChatGPT, created for the AWSW WordClock community.
