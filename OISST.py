import streamlit as st

from utils import getsstobs, plotmap, getsstclim

st.sidebar.header('NOAA Extended Reconstructed Sea Surface Temperature (SST) V5')

my_bar = st.sidebar.progress(0)

clim = st.sidebar.radio(
    'CLIMATOLOGY:',
    ('1989-2008', '1981-2010', '1991-2020'),
    index=1
)

# get obs e clim
anom_year = str(st.sidebar.selectbox('ANOM. YEAR:', range(2020, 2010, -1), index=0))
anom_mon = st.sidebar.selectbox('ANOM. MONTH:', list(range(1, 13)), index=0)
sst_obs, lat, lon = getsstobs(anom_year, anom_mon)
sst_clim, lat, lon = getsstclim(clim, anom_mon)

# compute anom
sst_anom = sst_obs - sst_clim

my_bar.progress(50)

# plot nom
fig_title = f'ANOM {anom_year}/{anom_mon:02d} ({clim})'
st.write(plotmap(sst_anom, lon, lat, fig_title, pal='anom'))

my_bar.progress(100)

#
