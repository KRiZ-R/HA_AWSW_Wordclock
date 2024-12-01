
# AWSW WordClock Integration for Home Assistant

This is a custom integration for controlling the AWSW WordClock using Home Assistant.

![Bildschirmfoto 2024-11-30 um 15 36 48](https://github.com/user-attachments/assets/9bc1ace4-eee2-4e9e-99b6-e08400a31fa1)
![Bildschirmfoto 2024-11-30 um 15 45 02](https://github.com/user-attachments/assets/0dac0164-196d-40bb-881a-427a641b7176)

As iam not an Developer iam not sure if iam able to expand Features or fix Bugs, all the work here was done by ChatGPT with a lot of
testing and troubbleshooting.


## Features
- Control up to 12 extra words as switches.
- Automatically detects and registers a WordClock device using its IP address.
- Direct link to the WordClock Web Interface for configuration.
- Supports 7 Languages (German, English, Dutch, French, Italian, Swedish, Spanish)
- Supports unique entities for each word.
  - German
        1: "ALARM"
        2: "GEBURTSTAG"
        3: "MÜLL RAUS BRINGEN"
        4: "AUTO"
        5: "FEIERTAG"
        6: "FORMEL1"
        7: "GELBER SACK"
        8: "URLAUB"
        9: "WERKSTATT"
        10: "ZEIT ZUM ZOCKEN"
        11: "FRISEUR"
        12: "TERMIN"
  - English
        1: "COME HERE"
        2: "LUNCH TIME"
        3: "ALARM"
        4: "GARBAGE"
        5: "HOLIDAY"
        6: "TEMPERATURE"
        7: "DATE"
        8: "BIRTHDAY"
        9: "DOORBELL"
  - Dutch
        1: "KOM HIER"
        2: "LUNCH TIJD"
        3: "ALARM"
        4: "AFVAL"
        5: "VAKANTIE"
        6: "TEMPERATUUR"
        7: "DATUM"
        8: "VERJAARDAG"
        9: "DEURBEL"
  - French
        1: "ALARME"
        2: "ANNIVERSAIRE"
        3: "POUBELLE"
        4: "A TABLE"
        5: "VACANCES"
        6: "VIENS ICI"
        7: "SONNETTE"
        8: "TEMPERATURE"
        9: "DATE"
  - Italian
        1: "VIENI QUI"
        2: "ORA DI PRANZO"
        3: "ALLARME"
        4: "VACANZA"
        5: "TEMPERATURA"
        6: "DATA"
        7: "COMPLEANNO"
        8: "CAMPANELLO"
  - Swedish
        1: "FÖDELSEDAG"
        2: "LARM"
        3: "HÖGTID"
        4: "SEMESTER"
        5: "LADDA NER"
        6: "LUNCHTID"
        7: "KOM HIT"
        8: "DÖRRKLOCKA"
        9: "TEMPERATUR"
  - Spanish
        1: "CUMPLEAÑOS"
        2: "ALARMA"
        3: "VACACIONES"
        4: "DÍA DE BASURA"
        5: "FECHA"
        6: "HORA DE ALMUERZO"
        7: "VEN AQUÍ"
        8: "TIMBRE"
        9: "TEMPERATURA"

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
Idea of this Intergration by myself, most of the work is done by ChatGPT, created for the [AWSW WordClock](https://www.printables.com/model/768062-wordclock-16x16-2024/) community.
