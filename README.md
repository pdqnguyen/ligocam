Welcome to LIGO Channel Activity Monitor (ligocam).

ligocam is an efficient diagnostic tool for monitoring auxiliary channels.
The utilities include locating a malfunctioning channel, graphic information
of channel's time series and spectral data, and spectral change to understand
various band-limited environmental disturbances of non-astrophysical origin.

More information can be found here: http://pem.ligo.org

To install ligocam locally:
```
python setup.py install --user
```

The most current ligocam development version is available from
the git repository:
```
git clone https://github.com/pdqnguyen/ligocam
```

Install ligocam directly from this repository via
```
python -m pip install git+https://github.com/gwdetchar/gwdetchar.git
```

For first-time setup, edit the configuration file for the desired ifo/subsystem
to your liking and run ligocam-setup, e.g.:
```
ligocam-setup <config file> <share directory>
```
