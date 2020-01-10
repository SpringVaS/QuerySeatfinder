# Seatfinder Query to Excel

This is a little tool that writes Databank entries from the KIT Seatfinder Database into an excel file. In a small GUI you can select the time range in which the values should be. 


## Depencencies

All requirements can be installed through pip. Run

```
pip install -r requirements.txt
```


The script runs in python version 3, the newest stable release is recommended.
It is also useful to set up a virtual environment, so that you do not clutter your productive system with the requiered dependencies.

## Features

The database offers a value every 5 minutes. You can choose a down sampling interval. Furthermore the aggregation method when downsampling method can be specified. Implemented options are arithmetic mean and gaussian weighted around the sampling time. The derivation for the gaussian method is chosen such that the value at the furthest time in the interval would have a share of 20 percent


## Output

The tool outputs the estimated seat occupation of all libraries on campus into an excel file named 'data.xls'