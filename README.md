# Divvy Station Monitor

_A real-time monitor of the Divvy Stations in Chicago._

## Introduction
[Divvy](https://www.divvybikes.com/) is Chicago's bike share system, with 580 stations and 5,800 bikes across Chicagoland. It’s a fun, affordable and convenient way to get around. 

## Divvy Station Status Monitor
Live station info on each Divvy station can be accessed throught Divvy [GBFS JSON Feed](https://gbfs.divvybikes.com/gbfs/gbfs.json).

To visualize the trend of station info, we provide a live Divvy Station Monitor with station status for the past week. 

[![Alt text](/static/img/snapshot.png?raw=true "Optional Title")](https://divvystationmonitor.herokuapp.com)

## Data Infrastructure
The infrastructure is constructed on [Google Cloud Platform](https://cloud.google.com/). A Cloud PostgreSOL is used to store the real-time station info data. The detailed work flow can be view below.

These data can be further used to perform time-series analysis and forecasting.

[![Work Flow](/static/img/wf.png?raw=true "Optional Title")](https://divvystationmonitor.herokuapp.com/about)


(*Desktop View Only. Google Chrome is recommended.*)
