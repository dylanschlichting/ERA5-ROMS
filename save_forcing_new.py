#Script to modify ERA5 files obtained from ERA5-ROMS repository.
#This is to produce a forcing file compatible with COAWST v3.8
#when using BULK_FLUXES
import xarray as xr
import warnings
warnings.filterwarnings("ignore") #turns off annoying warnings

ds = xr.open_mfdataset('/global/cfs/cdirs/m4304/txla_mod/hindcast/inputs/frc/era5/2000/*.nc')
#Remove rendundant indices
ds = ds.drop_indexes(['lon', 'lat', 'pair_time', 
                     'qair_time', 'Tair_time', 'wind_time', 
                     'cloud_time', 'rain_time', 'swrad_time', 
                     'lwrad_time', 'sen_time'])

ds['Pair'] = ds['Pair']/100 #Convert to mb
ds['Qair'] = ds['Qair']*1000 #Convert to g/kg
ds['time'] = ds.pair_time.values #Replace time values

#Drop variables not needed by ROMS
ds = ds.drop_vars(['latent', 'sensible', 'lwrad','evaporation']) 

#Prescribe attributes
#Air pressure
ds.Pair.attrs = {'long_name': 'surface pressure', 
                 'units': 'millibar', 
                 'coordinates':'lon lat',
                 'time': 'time'}
#Specific humidity
ds.Qair.attrs = {'long_name': 'specific humidity', 
                 'units': 'g kg-1',
                 'coordinates':'lon lat',
                 'time': 'time'}
# ds['Qair'].encoding.popitem()
#Air temperature
ds['Tair'] = ds['Tair'].rename({'Tair_time':'tair_time'}) #fix typo 
ds.Tair.attrs = {'long_name': '2 metre temperature', 
                 'units': 'Celsius',
                 'coordinates':'lon lat',
                 'time': 'time'}
ds['Tair'].encoding.popitem()
#Uwind 
ds.Uwind.attrs = {'long_name': '10 metre u-wind component', 
                 'units': 'm s-1',
                 'coordinates':'lon lat',
                 'time': 'time'}
ds['Uwind'].encoding.popitem()
#Vwind
ds.Vwind.attrs = {'long_name': '10 metre v-wind component', 
                 'units': 'm s-1',
                 'coordinates':'lon lat',
                 'time': 'time'}
ds['Vwind'].encoding.popitem()
#Rain
ds.rain.attrs = {'long_name': 'rain',
                 'units': 'kg m-2 s-1',
                 'coordinates':'lon lat',
                 'time': 'time'}
ds['rain'].encoding.popitem()

#Net shortwave
ds['swrad'] = ds['swrad'].rename({'swrad_time':'srf_time'})
ds.swrad.attrs = {'long_name': 'Mean surface net short-wave radiation flux',
                  'units': 'watt meter-2',
                  'coordinates':'lon lat',
                  'time': 'time'}
ds['swrad'].encoding.popitem()
# Downward longwave
ds['lwrad_down'] = ds['lwrad_down'].rename({'lwrad_time':'lrf_time'})
ds.lwrad_down.attrs = {'long_name': 'Mean surface downward long-wave radiation flux',
                       'units': 'watt meter-2',
                       'coordinates':'lon lat',
                       'time': 'time'}
ds['lwrad_down'].encoding.popitem()

#Save to netcdf 
ds.to_netcdf('/global/cfs/cdirs/m4304/txla_mod/hindcast/inputs/frc/era5/2000/txla_bulk_ERA5_2000_r1.nc', 
              format='NETCDF4', engine='netcdf4')
