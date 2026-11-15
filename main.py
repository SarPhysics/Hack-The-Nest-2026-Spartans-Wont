from datetime import datetime, timedelta, timezone
from locale import setlocale, LC_TIME

from requests import get
import streamlit as st

API_KEY = st.secrets["api_key"]

def fetch_object_list(now):
	yesterday = now - timedelta(days=1)
	tomorrow = now + timedelta(days=1)
	params = {
		"api_key": API_KEY,
		"start_date": yesterday.strftime("%Y-%m-%d"),
		"end_date": tomorrow.strftime("%Y-%m-%d")
	}
	
	r = get("https://api.nasa.gov/neo/rest/v1/feed", params)
	
	if r.status_code != 200:
		return None
	else:
		j = r.json()
		objects = []
		for v in j['near_earth_objects'].values():
			objects += v
		return objects

st.title("Near-Earth Asteroids")

now = datetime.now(timezone.utc)
objects = fetch_object_list(now)
tz = timezone(-timedelta(minutes=st.context.timezone_offset))

setlocale(LC_TIME, st.context.locale.replace("-", "_"))

for o in objects:
	# note that the epoch_date_close_approach value is in milliseconds, so we divide by 1000
	approach_datetime = datetime.fromtimestamp(o['close_approach_data'][0]['epoch_date_close_approach'] / 1000, tz=timezone.utc)
	
	st.markdown(f'''### {':gray-badge[Provisional]' if o['name'][0] == '(' else ''}{o['name']}
**Estimated diameter:** {o['estimated_diameter']['meters']['estimated_diameter_min']:.2f} to {o['estimated_diameter']['meters']['estimated_diameter_max']:.2f} m

**Closest approach time:** {approach_datetime.astimezone(tz).strftime('%c')}

**Velocity relative to Earth:** {float(o['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']):,.1f} km/h ({float(o['close_approach_data'][0]['relative_velocity']['miles_per_hour']):,.1f} mph)''')
	
	if approach_datetime < now:
		st.markdown(f"**Missed Earth by:** {int(o['close_approach_data'][0]['miss_distance']['kilometers'].partition('.')[0]):,} km ({int(o['close_approach_data'][0]['miss_distance']['miles'].partition('.')[0]):,} mi)")
	else:
		st.markdown(f"**Will miss Earth by:** {int(o['close_approach_data'][0]['miss_distance']['kilometers'].partition('.')[0]):,} km ({int(o['close_approach_data'][0]['miss_distance']['miles'].partition('.')[0]):,} mi)")
	
	st.markdown(f"[More info]({o['nasa_jpl_url']})")

st.markdown(":small[:gray[Made possible by NASA's NeoWs API. Supported by the Michigan Space Grant Consortium, NASA grant 80NSSC20M0124. This project is not affiliated with or endorsed by NASA.]]")
