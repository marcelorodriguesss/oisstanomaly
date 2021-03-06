import xarray as xr
import matplotlib as mpl
import cartopy as cart
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from numpy import squeeze
from cartopy.util import add_cyclic_point
from matplotlib.colors import BoundaryNorm, ListedColormap

def is_mon(month, n: int):
    """
    Se n = 1, seleciona somente os jan do período
    Se n = 2, seleciona somente os fev do período
    Se n = 12, seleciona somente os dez do período
    """
    return (month == n)


def fix_data(da: xr.DataArray, psst=False):

    # lon 0:360 -> -180:180

    # https://stackoverflow.com/a/53471670

    da['_lon'] = xr.where(da['lon'] > 180,
                                da['lon'] - 360,
                                da['lon'])

    da = (
        da
        .swap_dims({'lon': '_lon'})
        .sel(**{'_lon': sorted(da._lon)})
        .drop('lon')
    )

    da = da.rename({'_lon': 'lon'})

    da =  da.reindex(lat=da.lat[::-1])

    lat = da.coords['lat'].values

    # add cyclic point lon

    lon = da.coords['lon'].values

    lon_idx = da.dims.index('lon')

    arr, lon = add_cyclic_point(
        da.values, coord=lon, axis=lon_idx
    )

    return arr, lat, lon


def getsstclim(clim, mon):

    sst_file = 'https://psl.noaa.gov/thredds/dodsC/Datasets' \
        '/noaa.oisst.v2/sst.mnmean.nc'

    # sst_file = 'https://psl.noaa.gov/thredds/dodsC/Datasets' \
        # '/noaa.ersst.v5/sst.mnmean.nc'

    with xr.open_dataset(sst_file) as dset:

        print(dset)

        iyear = clim.split('-')[0]
        fyear = clim.split('-')[1]

        sst_clim = dset.sst \
            .sel(time=is_mon(dset.sst['time.month'], mon)) \
            .sel(time=slice(iyear, fyear)).mean(dim='time')

        arr_clim, lat, lon = fix_data(sst_clim)

        return arr_clim, lat, lon


def getsstobs(year, mon):

    sst_file = 'https://psl.noaa.gov/thredds/dodsC/Datasets' \
        '/noaa.oisst.v2/sst.mnmean.nc'

    # sst_file = 'https://psl.noaa.gov/thredds/dodsC/Datasets' \
        # '/noaa.ersst.v5/sst.mnmean.nc'

    with xr.open_dataset(sst_file) as dset:

        sst_obs = dset.sst.sel(time=f'{year}-{mon}')

        arr_obs, lat, lon = fix_data(sst_obs)

        return squeeze(arr_obs), lat, lon


def plotmap(arr, lon, lat, fig_title, pal='anom'):

    fig_map = plt.figure(figsize=(10, 7))

    proj = cart.crs.PlateCarree(central_longitude=0)  # -156

    ax = plt.axes(projection=proj)

    if pal == 'anom':

        pal = ['#000044', '#0033FF', '#007FFF', '#0099FF', '#00B2FF',
               '#00CCFF', '#FFFFFF', '#FFCC00', '#FF9900', '#FF7F00',
               '#FF3300', '#A50000', '#B48C82']
        clevs = [-3., -2.5, -2., -1.5, -1., -0.5, 0.5, 1., 1.5, 2., 2.5, 3.]
        orient = 'horizontal'
        shrink=1.
        aspect=35

    elif pal == 'diff':

        pal = ('#0033FF', '#0099FF', '#FFFFFF', '#FFCC00', '#FF3300')
        clevs = [-1., -0.05, 0.05, 1.]
        orient = 'horizontal'
        shrink=0.45
        aspect=9

    else:

        pal = ['#D204A9', '#B605C1', '#9406DF', '#7907F7', '#5A45F9',
               '#368FFB', '#18CDFD', '#00F8E1', '#00E696', '#00D13C',
               '#0CC600', '#4CD500', '#99E700', '#D8F600', '#FFE900',
               '#FFB400', '#FF7400', '#FF3F00']
        clevs = list(range(-2, 31, 2))
        orient = 'horizontal'
        shrink=1.
        aspect=35

    ccols = ListedColormap(pal[1:-1])
    ccols.set_under(pal[0])
    ccols.set_over(pal[-1])

    norm = BoundaryNorm(clevs, ncolors=ccols.N, clip=False)

    img = ax.contourf(
        lon,
        lat,
        arr,
        cmap=ccols,
        levels=clevs,
        extend='both',
        norm=norm,
        transform=proj
    )

    ax.gridlines(crs=proj, linewidth=1.5, color='black', alpha=0.5,
                 linestyle='--', draw_labels=False)

    parallels = list(range(-180, 181, 40))
    meridians = list(range(-90, 91, 20))

    ax.set_xticks(parallels, crs=proj)
    ax.set_yticks(meridians, crs=proj)
    ax.set_xticklabels(parallels, rotation=0, fontsize=10, fontweight='bold')
    ax.set_yticklabels(meridians, rotation=0, fontsize=10, fontweight='bold')

    ax.add_feature(
        cart.feature.LAND,
        zorder=50,
        edgecolor='k',  #808080
        facecolor='k'
    )

    ax.set_extent([-180, 180, -80, 80], proj)

    bar = fig_map.colorbar(
                img,
                pad=0.08,
                spacing='uniform',
                orientation=orient,
                extend='both',
                ax=ax,
                extendfrac='auto',
                ticks=clevs,
                shrink=shrink,
                aspect=aspect
            )


    bar.ax.tick_params(labelsize=11)

    # fig_map.canvas.flush_events()

    # ref: https://matplotlib.org/3.1.1/gallery/ticks_and_spines/colorbar_tick_labelling_demo.html
    # bar.ax.set_yticklabels(
    #     labels=bar.ax.get_yticklabels(),
    #     fontsize=50, weight='bold'
    # )

    bar.set_label(label="(degC)", size=11, weight='bold')

    ax.set_title(fig_title, fontsize=12, weight='bold', loc='center')

    return fig_map

#