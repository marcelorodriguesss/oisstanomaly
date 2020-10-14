import xarray as xr
from numpy import squeeze
from cartopy.util import add_cyclic_point
import matplotlib as mpl
from matplotlib.colors import BoundaryNorm, ListedColormap
import cartopy as cart
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

def is_mon(month, n: int):
    """
    Se n = 1, seleciona somente os jan do período
    Se n = 2, seleciona somente os fev do período
    Se n = 12, seleciona somente os dez do período
    """
    return (month == n)


def fix_data(da: xr.DataArray, psst=False):

    # print(da)

    # lon 0:360 -> -180:180

    # https://stackoverflow.com/a/53471670

    da['_longitude'] = xr.where(da['longitude'] > 180,
                            da['longitude'] - 360,
                            da['longitude'])

    da = (
        da
        .swap_dims({'longitude': '_longitude'})
        .sel(**{'_longitude': sorted(da._longitude)})
        .drop('longitude')
    )

    da = da.rename({'_longitude': 'longitude'})

    if psst:
        da =  da.reindex(latitude=da.latitude[::-1])

    lat = da.coords['latitude'].values

    # add cyclic point lon

    lon = da.coords['longitude'].values

    lon_idx = da.dims.index('longitude')

    arr, lon = add_cyclic_point(
        da.values, coord=lon, axis=lon_idx
    )

    return arr, lat, lon


def getsstclim(clim, mon):

    # sst_file = 'SST.ER.LAND.50-81.and.OIV2.82-0820.T42.nc'

    sst_file = 'OBS-SST-1281-0920-T42.nc'

    with xr.open_dataset(sst_file) as dset:

        print('\n***** DSET CLIM *****')
        print(dset)
        print('')

        iyear = clim.split('-')[0]
        fyear = clim.split('-')[1]

        print(iyear)
        print(fyear)
        print(mon)

        sst_clim = dset.sst \
            .sel(time=is_mon(dset.sst['time.month'], mon)) \
            .sel(time=slice(iyear, fyear)).mean(dim='time')

        arr_clim, lat, lon = fix_data(sst_clim)

        return arr_clim, lat, lon


def getsstobs(year, mon):

    # sst_file = 'SST.ER.LAND.50-81.and.OIV2.82-0820.T42.nc'

    sst_file = 'OBS-SST-1281-0920-T42.nc'

    with xr.open_dataset(sst_file) as dset:

        print('\n***** DSET OBS *****')
        print(dset)
        print('')

        sst_obs = dset.sst.sel(time=f'{year}-{mon}')

        arr_obs, lat, lon = fix_data(sst_obs)

        return squeeze(arr_obs), lat, lon


def getpsst(ncfile, l=1):

    psst_file = f'./check/{ncfile}'

    with xr.open_dataset(psst_file) as dset:

        print('+++++++++')
        print(dset)

        psst = dset.sst.isel(time=l-1)

        arr, lat, lon = fix_data(psst, psst=True)

        return squeeze(arr) - 273.15, lat, lon


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
        clevs = [-0.1, -0.05, 0.05, 0.1]
        orient = 'horizontal'
        shrink=0.45
        aspect=9

    else:

        pal = ['#D204A9', '#B605C1', '#9406DF', '#7907F7', '#5A45F9', '#368FFB',
               '#18CDFD', '#00F8E1', '#00E696', '#00D13C', '#0CC600', '#4CD500',
               '#99E700', '#D8F600', '#FFE900', '#FFB400', '#FF7400', '#FF3F00']
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

    parallels = list(range(-180, 180, 20))
    meridians = list(range(-90, 91, 20))

    ax.set_xticks(parallels, crs=proj)
    ax.set_yticks(meridians, crs=proj)
    ax.set_xticklabels(parallels, rotation=0, fontsize=10, fontweight='bold')
    ax.set_yticklabels(meridians, rotation=0, fontsize=10, fontweight='bold')

    ax.add_feature(
        cart.feature.LAND,
        zorder=50,
        edgecolor='k',  # #808080
        facecolor='k'
    )

    ax.set_extent([-180, 180, -88, 88], proj)

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

    # 35

    ax.set_title(fig_title, fontsize=12, weight='bold', loc='center')

    return fig_map
