import os
import logging


class ECMWF_query:

    def __init__(self):
        self.setup_logging()

        self.use_era5 = True
        self.start_year = 2000
        self.end_year = 2001
        self.project = "ROHO800"
        self.area = self.get_area_for_project(self.project)
        self.skip_existing_files=True
        self.resultsdir = f"../oceanography/ERA5/{self.project}/"
        self.debug = False

        self.extract_data_every_N_hours = False
        self.time_units = "days since 1948-01-01 00:00:00"
        self.optionals = True  # optional variables to extract depending on ROMS version (Rutgers or Kate)
        self.ROMS_version = "Rutgers"  # "Rutgers" or "Kate" - the sea-ice component of Kates ROMS version uses downward
        # shortwave and not net shortwave to account for albedo of ice.

        if not os.path.exists(self.resultsdir):
            os.makedirs(self.resultsdir)
        if self.use_era5:
            self.dataset = 'era5'
            self.dataset_class = 'ea'
            self.grid = '0.25/0.25'
        else:
            self.dataset = 'interim'
            self.dataset_class = 'ei'
            self.grid = '0.75/0.75'

        self.reanalysis = 'reanalysis-era5-single-levels'  # 'reanalysis-era5-complete'

        # https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview
        self.parameters = ['10m_u_component_of_wind',
                           '10m_v_component_of_wind',
                           '2m_temperature',
                           'mean_sea_level_pressure',
                           'mean_surface_downward_long_wave_radiation_flux',
                           'total_cloud_cover',
                           'total_precipitation',
                           'specific_humidity']
        
        if self.ROMS_version == "Kate":
            self.parameters.append('mean_surface_downward_short_wave_radiation_flux')
        elif self.ROMS_version == "Rutgers":
            self.parameters.append('mean_surface_net_short_wave_radiation_flux')
        else:
            raise Exception("[ECMWF_query] You have to specify ROMS version (Kate or Rutgers)")

        # Additional variables that can be downloaded if needed
        if self.optionals:
            self.parameters.extend([#'evaporation',
                                    #'mean_surface_sensible_heat_flux',
                                    #'mean_surface_latent_heat_flux',
                                    'mean_surface_net_long_wave_radiation_flux'])
        if not os.path.exists(self.resultsdir):
            os.makedirs(self.resultsdir, exist_ok=True)

    def get_area_for_project(self, project):
        # Setup project dependent area to extract
        # North/West/South/East
        return {'ROHO800': '62/1/56/10',
                'A20': '90/-180/40/180'}[project]

    def setup_logging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

    def info(self):
        logging.info("[ECMWF_query] ERA5: \n Reanalysis: 0.25°x0.25° (atmosphere), 0.5°x0.5° (ocean waves) \n \
            Period: 1979 - present \n \
            More info on ERA5 can be found here:\n \
            https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels-monthly-means?tab=overview")

    # List of parameters to download:
    # https://apps.ecmwf.int/codes/grib/param-db
    # https: // apps.ecmwf.int / data - catalogues / era5 / batch / 3647799 /

    def get_parameter_metadata(self, parameter):
        return {'2m_temperature': {'parameter_id': '167.128',
                                   'short_name': 't2m',
                                   'roms_name': 'Tair',
                                   'name': '2 metre temperature',
                                   'units': 'K',
                                   'time_name': 'Tair_time'},
                '2m_dewpoint_temperature': {'parameter_id': '168.128',
                                            'short_name': 'd2m',
                                            'roms_name': 'Qair',
                                            'name': '2 metre dewpoint temperature',
                                            'units': 'K',
                                            'time_name': 'tdew_time'},
                'specific_humidity': {'parameter_id': '133.128',
                                      'short_name': 'q',
                                      'roms_name': 'Qair',
                                      'name': 'specific humidity',
                                      'units': 'kg kg-1',
                                      'time_name': 'qair_time'},
                '10m_v_component_of_wind': {'parameter_id': '166.128',
                                            'short_name': 'v10',
                                            'roms_name': 'Vwind',
                                            'name': '10 metre v-wind component',
                                            'units': 'm s-1',
                                            'time_name': 'wind_time'},
                '10m_u_component_of_wind': {'parameter_id': '165.128',
                                            'short_name': 'u10',
                                            'roms_name': 'Uwind',
                                            'name': '10 metre u-wind component',
                                            'units': 'm s-1',
                                            'time_name': 'wind_time'},
                'mean_sea_level_pressure': {'parameter_id': '151.128',
                                            'short_name': 'msl',
                                            'roms_name': 'Pair',
                                            'name': 'Mean sea level pressure',
                                            'units': 'Pa',
                                            'time_name': 'pair_time'},
                'total_cloud_cover': {'parameter_id': '164.128',
                                      'short_name': 'tcc',
                                      'roms_name': 'cloud',
                                      'name': 'Total cloud cover',
                                      'units': '(0-1)',
                                      'time_name': 'cloud_time'},
                'total_precipitation': {'parameter_id': '228.128',
                                        'short_name': 'tp',
                                        'roms_name': 'rain',
                                        'name': 'Total precipitation',
                                        'units': 'm',
                                        'time_name': 'rain_time'},
                'mean_surface_net_short_wave_radiation_flux': {'parameter_id': '37.235',
                                                               'short_name': 'msnswrf',
                                                               'roms_name': 'swrad',
                                                               'name': 'Mean surface net short-wave radiation flux',
                                                               'units': 'W m-2',
                                                               'time_name': 'swrad_time'},
                'mean_surface_net_long_wave_radiation_flux': {'parameter_id': '38.235',
                                                              'short_name': 'msnlwrf',
                                                              'roms_name': 'lwrad',
                                                              'name': 'Mean surface net long-wave radiation flux',
                                                              'units': 'W m-2',
                                                              'time_name': 'swrad_time'},
                'mean_surface_downward_long_wave_radiation_flux': {'parameter_id': '36.235',
                                                                   'short_name': 'msdwlwrf',
                                                                   'roms_name': 'lwrad_down',
                                                                   'name': 'Mean surface downward long-wave radiation flux',
                                                                   'units': 'W m-2',
                                                                   'time_name': 'lwrad_time'},
                'mean_surface_latent_heat_flux': {'parameter_id': '34.235',
                                                  'short_name': 'mslhf',
                                                  'roms_name': 'latent',
                                                  'name': 'Surface latent heat flux',
                                                  'units': 'W m-2',
                                                  'time_name': 'swrad_time'},
                'mean_surface_sensible_heat_flux': {'parameter_id': '33.235',
                                                    'short_name': 'msshf',
                                                    'roms_name': 'sensible',
                                                    'name': 'Surface sensible heat flux', 'units': 'W m-2',
                                                    'time_name': 'sen_time'},
                'evaporation': {'parameter_id': '182.128',
                                'short_name': 'e',
                                'roms_name': 'evaporation',
                                'name': 'Evaporation',
                                'units': 'm of water equivalent',
                                'time_name': 'rain_time'},
                'mean_surface_downward_short_wave_radiation_flux': {'parameter_id': 'None',
                                                                    'short_name': 'msdwswrf',
                                                                    'roms_name': 'swrad',
                                                                    'name': 'Mean surface downward short-wave radiation flux',
                                                                    'units': 'W m-2',
                                                                    'time_name': 'swrad_time'}}[parameter]
