# Netatmo App for Splunk
- Authors: Simon Balz <simon@balz.me>, Meno Schnapauf <meno@atremar.com>, Chris Wiederkehr <sinloft@gmail.com>

## Changelog
- **2014-11-16** simon@balz.me - Major update at data fetcher (use splunk internals to store credentials and config, added app installer), released v1.0
- **2014-11-13** simon@balz.me - Better Splunk v6.2 compatibility, bugfix at pressure area icon, prettier single values
- **2014-06-16** simon@balz.me - Improvement data fetcher, dashbaords and props/transforms
- **2014-06-13** simon@balz.me - Added support for rain gauge. 
- **2014-05-25** simon@balz.me - Updates due (annoying) API change. Added datamodel
- **2014-03-25** simon@balz.me - Updates due API changes
- **2014-05-06** simon@balz.me - Updates due API changes
- **2014-03-15** simon@balz.me - Updates due API changes
- **2014-02-24** simon@balz.me - Added 'Periodenvergleich' dashboard with custom JS visualization
- **2014-01-16** simon@balz.me - Dashboard improvements
- **2014-01-01** sinloft@gmail.com - Added support for indoor co2
- **2013-12-24** simon@balz.me - Dashboard improvements
- **2013-12-23** simon@balz.me - Added Netatmo dashboard
- **2013-12-22** sinloft@gmail.com - Changed input do extract data by device
- **2013-11-09** meno@atrematrcom - Initial revision

## Release Notes
- **v1.0** First official release of the app

## Prerequisites
- Netatmo account
- Netatmo Dev App (see https://dev.netatmo.com/dev/listapps)
- Internet access from Splunk Web to http://api.netatmo.net

## Installaton
- Unpack in $SPLUNK_HOME/etc/apps
- Restart Splunk
- Open splunk web and point to the App
- Run the installer to store credentials

## Usage
- Use the weather dashboard
- Use Pivot with the Netatmo datamodel
- Browse data index=netatmo
- Use macro 'dewpoint' in combination with macro 'muggy' on outdoor data to get 'muggy' days, example:
	index=netatmo type_label="Outdoor Module" | `dewpoint(temperature, humidity)` | `muggy(dewpoint)` | timechart span=1d count(muggy) AS muggy by device