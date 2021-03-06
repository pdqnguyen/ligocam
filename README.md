# LIGO Channel Activity Monitor (ligocam).

ligocam is an efficient diagnostic tool for monitoring auxiliary channels.
The utilities include locating a malfunctioning channel, graphic information
of channel's time series and spectral data, and spectral change to understand
various band-limited environmental disturbances of non-astrophysical origin.

More information can be found here: http://pem.ligo.org

## Installation

Install ligocam locally from this repository via
```
python -m pip install --user git+https://github.com/pdqnguyen/ligocam.git
```

## Setup
Each ifo and subsystem is run from its own config file. For first-time setup,
edit the configuration file for the desired ifo and subsystem
to your liking and feed it to ligocam-setup with the directory containing
the necessary static files, e.g.
```
ligocam-setup <config_file> <share_directory>
```

## Running ligocam
Submit a batch of ligocam jobs to condor by running ligocam-batch with
the desired config file:
```
ligocam-batch <config_file>
```

## Resetting a channel's history
Acceptable reference PSDs and the number of hours a channel has been
disconnected or had a DAQ failure are all logged in the run directory.
These records can be deleted via
```
ligocam-reset <config_file> <channel_name>
```
