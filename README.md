[![Build status][image-1]][1]
![CodeBeat][image-2]
![CodeCov][image-3]

## Download ERA5 and convert to ROMS format
**update 09.10.2024** 
Modified by Dylan Schlichting for work with the TXLA ROMS model. ```save_forcing_new.py``` added to ensure variables are compatible with COAWST v3.8.

**update 15.01.2022 All tests successful**
This latest version of the toolbox has now been tested for both the `Rutgers` and `Kate` Hedstroms versions of the code. For both versions, the correct forcing files are created and are read correctly by the ROMS source code. In both tests cases the results show an improvement in vertical mixing of heat in the water column due to the higher time frequency compared to ERA INTERIM.

The toolbox has also been tested for an Arctic model that covers 40-90N and -180 to 180E. Initially, ROMS did not accept the ERA5 data as the maximum longitude of the ERA5 data was slightly less than the model grid.
```sh
          Gridded:  LonMin = -180.0000 LonMax =  179.7500
                    LatMin =   40.0000 LatMax =   90.0000
          Model:    LonMin = -179.9848 LonMax =  179.9680
                    LatMin =   45.0081 LatMax =   89.9205
```

To resolve this issue you can pply a brillian [CDO](https://code.mpimet.mpg.de/projects/cdo) command called `sethalo` which basically replicates the last index value (-180E) at the maximum longitude (180E) to wrap the globe. To repeat this command on all files generated by this toolbox [run](https://gist.github.com/trondkr/6ae27a07424c15f585e7c0cbdf62fe98)(also new file added to repository [here](https://github.com/trondkr/ERA5-ROMS/blob/master/add_halo.sh):
```
for file in era5*.nc
do
 name=${file##*/}
 base=${name%.nc}
 echo "$file" new file "${base}_halo.nc"
 cdo sethalo,0,1 "$file" "${base}_halo.nc"
done
```
After runnning the `CDO` commands (`add_halo.sh`) you may need to update the attributes of the `.nc` files by running `add_attributes_to_netcdf4.sh` [found here](https://github.com/trondkr/ERA5-ROMS/blob/master/add_attributes_to_netcdf4.sh)

A new option to reduce the memory footprint of the result files has been implemented. The option `extract_data_every_6_hours` (defined as `True/False` in `ECMWF_query.py`) allow you to specify 6 hourly, instead of hourly, output to file frequency. For forcing files that cover large regions such as the entire Northern Hemisphere, this drastically reduces the total file size. The option can be used to specify other output frequency through the list of timesteps required (`ECMWF:tools.py`):

```
if self.config_ecmwf.extract_data_every_6_hours is True:
			times = ['00:00', '06:00', '12:00', '18:00']
```


**update 12.11.2021 - resolved**
Believe that the issue with ROMS reading ERA5 generated files using ERA5-ROMs has been resolved by inverting the latitude (and data array) of ERA5. Apparently ROMS is not able to read the ERA5 in the ECMWF standard way of representing latitude. Please create an issue if this is still a problem!

**update 10.08.2020**
After conversations with ECMWF support I changed the code to only use ERA5 parameter names and not parameter IDs as these did not
result in stable downloads (some parameter IDs seems to be missing for some months while the parameter names are consistent).

This toolbox enables you to download ERA5 atmospheric forcing data for your model domain for a specified period.  The toolbox uses the [*Climate Data Store*] Python API to connect and download specific variables required by ROMS to perform simulations with atmospheric forcing. These variables are included in the list below:
```
   'Specific_humidity',
   '10m_u_component_of_wind',
   '10m_v_component_of_wind',
   '2m_temperature',
   '2m_dewpoint_temperature',
   'Mean_sea_level_pressure',
   'Total_cloud_cover',
   'Total_precipitation',
   'Mean_surface_net_short-wave_radiation_flux',
   'Mean_surface_net_long-wave_radiation_flux',
   'Mean_surface_downward_long-wave_radiation_flux',
   'Mean_surface_latent_heat_flux',
   'Mean_surface_sensible_heat_flux',
   'Evaporation',
   'Mean surface downward short-wave radiation flux'
```
Details of the ERA5 variables can be found [here](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview)
To see the details for how ROMS requires naming convention etc.
#### *Install API*
To start signup and get necessary credentials at the [*Climate Data Store*]. Store the credentials in a file called `.cdsapirc`in you root `$HOME` directory. It should look something like this:

url: https://cds.climate.copernicus.eu/api/v2
key: 28122:f85a4564-8895-498d-ad8a-gf274ba38d2r
ls -lrt
#### *Edit the toolbox settings*
Edit the file `ECMWF_query.py`to define the start and end period you want to download data. If you want you can edit the months, days, and time steps of the day data will be downloaded in the file `ECMWF_tools.py` but by default the program downloads data for all available reanalysis time steps of the day for all days for all months of the year. Each result file contains data for one variable for one year.


**Note**: If you are using Kate Hedstroms ROMS version with sea-ice you need to download 'mean_surface_downward_short_wave_radiation_flux' while the
regular Rutgers ROMS version uses 'mean_surface_net_short_wave_radiation_flux'. This can be defined in the option `self.ROMS_version = "Kate"`in `ECMWF_query.py`.

The request API can be tested here:
[ECMWF ERA5 API requests](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=form)
and the Python cdsapi is described [cdsapi](https://github.com/ecmwf/cdsapi).
Data availability from Copernicus available here [https://cp-availability.ceda.ac.uk/](https://cp-availability.ceda.ac.uk/).

The region for where you extract the data is defined by the variable `self.area = "80/0/50/25"`found in `ECMWF_query.py`. The area is constrained by `North/West/South/East`.

The time units in the  resulting ROMS files are converted from the ERA5 units (`1900-01-01`) to the standard ROMS reference time `1948-01-01`.
The toolbox uses the netCDF4 `date2num`and `num2date` functions for this conversion.

#### *Main query*
The main query for the call for data is found in ECMWF_tools.py
```Python
		def submit_request(self, parameter, year, out_filename):

		options = {
			'product_type': 'reanalysis',
			"year": year,
			"month": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
			'day': [
				'01', '02', '03',
				'04', '05', '06',
				'07', '08', '09',
				'10', '11', '12',
				'13', '14', '15',
				'16', '17', '18',
				'19', '20', '21',
				'22', '23', '24',
				'25', '26', '27',
				'28', '29', '30',
				'31',
			],
			'time': [
				'00:00', '01:00', '02:00',
				'03:00', '04:00', '05:00',
				'06:00', '07:00', '08:00',
				'09:00', '10:00', '11:00',
				'12:00', '13:00', '14:00',
				'15:00', '16:00', '17:00',
				'18:00', '19:00', '20:00',
				'21:00', '22:00', '23:00',
			],
			"variable": [parameter],
			'format': "netcdf",
			"area": self.config_ecmwf.area,
			"verbose": self.config_ecmwf.debug,
		}
		# Add more specific options for variables on pressure surfaces
		if parameter == "specific_humidity":
			self.config_ecmwf.reanalysis = "reanalysis-era5-pressure-levels"
			options["levtype"] = 'pl'
			options["pressure_level"] = '1000'
		else:
			self.config_ecmwf.reanalysis = 'reanalysis-era5-single-levels'

		try:
			# Do the request
			self.server.retrieve(self.config_ecmwf.reanalysis, options, out_filename)
		except Exception as e:
			print(e)
			print("[!] -------------------------- PROBLEMS WITH {0}".format(out_filename))

		metadata = self.config_ecmwf.get_parameter_metadata(parameter)
		converter = ECMWF_convert_to_ROMS.ECMWF_convert_to_ROMS()
		converter.convert_to_ROMS_units_standards(out_filename, metadata, parameter, self.config_ecmwf)


```

#### *Run the toolbox*
To run the toolbox after editing the settings simply run
`python ECMWF_tools.py`

### Global data
If your model domain covers the entire Arctic, or northern hemisphere and reaches from -180 to 180 you have to convert
the ERA5 data to be connected. This is done by introducing a fake point at 180 which is identical to point 0. This
makes the data across the meridian line con`sistent and ROMS won`t choke on it. This step requires CDO installed.

Run `make_files_fully_global-sh`:
```Bash
for filename in results/*.nc; do
		echo "Converting: " "$filename" " to" "halo/$(basename "$filename" .nc)_halo.nc"
    cdo sethalo,0,1 "$filename" "halo/$(basename "$filename" .nc)_halo.nc"
done
```

####*Unittest*
A few simple unittests are included in `test_ERA5.py`.

[1]: https://buildkite.com/rask-dev-llc/era5-toolbox
[image-1]:	https://badge.buildkite.com/9fe63ac4afc901fb503d10d67c26175d7071137729c00d1b17.svg
[image-2]:	https://codebeat.co/badges/402a5755-c757-4a8d-a9a5-f9349aed8462
[image-3]:	https://codecov.io/gh/trondkr/ERA5-ROMS/branch/master/graph/badge.svg
