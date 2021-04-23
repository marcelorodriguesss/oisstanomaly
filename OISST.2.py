import streamlit as st

from utils import getsstobs, plotmap, getsstclim

st.sidebar.header('NOAA Optimum Interpolation (OI) SST V2')

my_bar = st.sidebar.progress(0)

clim = st.sidebar.radio(
    'CLIMATOLOGY:',
    ('1982-2010', '1989-2008', '1991-2020'),
    index=0
)

# get obs e clim
<<<<<<< HEAD
anom_year = str(st.sidebar.selectbox('ANOM. YEAR:', range(2021, 2010, -1), index=0))
=======
anom_year = str(st.sidebar.selectbox('ANOM. YEAR:', range(2020, 1981, -1), index=0))

>>>>>>> d681e894f776ae5396e93592e12e767093c2184e
anom_mon = st.sidebar.selectbox('ANOM. MONTH:', list(range(1, 13)), index=0)

sst_obs, lat, lon = getsstobs(anom_year, anom_mon)
my_bar.progress(20)

sst_clim, lat, lon = getsstclim(clim, anom_mon)
my_bar.progress(40)

# compute anom
sst_anom = sst_obs - sst_clim
my_bar.progress(60)

# plot nom
fig_title = f'ANOM {anom_year}/{anom_mon:02d} - CLIMATOLOGY: {clim} - NOAA OISST V2'
st.write(plotmap(sst_anom, lon, lat, fig_title, pal='anom'))
my_bar.progress(80)

fig_title = f'OBS {anom_year}/{anom_mon:02d} - NOAA OISST V2'
st.write(plotmap(sst_obs, lon, lat, fig_title, pal='any'))

my_bar.progress(100)

#
