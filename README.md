# AWSW WordClock Integration for Home Assistant

This is a custom integration for controlling the AWSW WordClock using Home Assistant.

![German WordClock](https://github.com/KRiZ-R/HA_AWSW_Wordclock/blob/main/WordClock%20Deutch.png)
![Dutch WordClock](https://github.com/KRiZ-R/HA_AWSW_Wordclock/blob/main/WordClock%20Nederlands.png)

I found this integration made by bluenazgul, who made this using ChatGPT.
That integration only had switches for turning on the extra words, and the language selection did not work.
I wanted it to have some more functionality, like changing the light colors of the Background, Text and extra words and an option of choosing the language. So that's why I made a fork of that integration and added these features.

## Features
- Controls the Background and Text lights, colors and intensity.
- Controls the extra words as lights and colors.
- Automatically detects and registers a WordClock device using its IP address.
- Direct link to the WordClock Web Interface for configuration.
- Supports 7 Languages (German, English, Dutch, French, Italian, Swedish, Spanish)
- Supports unique entities for each word.
  - German: "ALARM", "GEBURTSTAG", "MÜLL RAUS BRINGEN", "AUTO", "FEIERTAG", "FORMEL1", "GELBER SACK", "URLAUB", "WERKSTATT", "ZEIT ZUM ZOCKEN", "FRISEUR", "TERMIN"
  - English: "COME HERE", "LUNCH TIME", "ALARM", "GARBAGE", "HOLIDAY", "TEMPERATURE", "DATE", "BIRTHDAY", "DOORBELL"
  - Dutch: "KOM HIER", "LUNCH TIJD", "ALARM", "AFVAL", "VAKANTIE", "TEMPERATUUR", "DATUM", "VERJAARDAG", "DEURBEL"
  - French: "ALARME", "ANNIVERSAIRE", "POUBELLE", "A TABLE", "VACANCES", "VIENS ICI", "SONNETTE", "TEMPERATURE", "DATE"
  - Italian: "VIENI QUI", "ORA DI PRANZO", "ALLARME", "VACANZA", "TEMPERATURA", "DATA", "COMPLEANNO", "CAMPANELLO"
  - Swedish: "FÖDELSEDAG", "LARM", "HÖGTID", "SEMESTER", "LADDA NER", "LUNCHTID", "KOM HIT", "DÖRRKLOCKA", "TEMPERATUR"
  - Spanish: "CUMPLEAÑOS", "ALARMA", "VACACIONES", "DÍA DE BASURA", "FECHA", "HORA DE ALMUERZO", "VEN AQUÍ", "TIMBRE", "TEMPERATURA"

## Requirements
- A working AWSW WordClock with API access enabled with version V4.7.1 or higher.
- https://www.printables.com/model/768062-wordclock-16x16-2024 is the one i use
- Home Assistant version 2024.11 or higher.

## Installation

### Installation via HACS (Recommended)
1. Add this repository to HACS as a custom repository.
2. Search for "AWSW WordClock" in the HACS store and install it.
3. Restart Home Assistant.

### Manual Installation
1. Download the latest release from the [Releases](https://github.com/KRiZ-R/HA_AWSW_Wordclock/releases) page.
2. Extract the contents and copy the `awsw_wordclock` folder to your `custom_components` directory in Home Assistant.
   - The path should be: `custom_components/awsw_wordclock/`
3. Restart Home Assistant and configure the integration via the integrations page or press the blue button below.
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=awsw_wordclock)

## Setup
1. Go to `Settings > Devices & Services > Add Integration`.
2. Search for "AWSW WordClock".
3. Enter following settings:
  - the IP address of your WordClock
  - the name of your WordClock
  - the language you have set for your WordClock
  - the polling frequency
  - then press "Submit"

## Usage
- The Background and Text can be used as lights, so you can turn them on and off separately. Additionally, the colors and brightness can be changed. While the WordClock API currently does not support separate brightness levels for the background and text, the brightness is applied uniformly to all texts.
- Each of the extra words (the number of words differs from one language to another) now appears as a light in Home Assistant. You can turn these words on or off directly from the dashboard or use them in automations. In addition to setting a custom color, the integration now retrieves the current RGB LED color for each extra word from the WordClock API. This means that the displayed color in Home Assistant accurately reflects the device's actual state.
- A direct link to the WordClock Web Interface is available under the device details.

## Troubleshooting
- Ensure the WordClock is reachable and the IP address is correct.
- Check the Home Assistant logs for any errors.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### Credits
- [AWSW WordClock](https://www.printables.com/model/768062-wordclock-16x16-2024/) for making the WordClock 3D-Print files and software.
- https://github.com/bluenazgul/HA_AWSW_Wordclock | Forked project, initial inspiration!
