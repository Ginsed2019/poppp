import dash
from dash import html, dcc, ctx
import dash_leaflet as dl
from dash.dependencies import Input, Output
import dash_daq as daq

from utils import get_config, get_rectangle_bounds, s1_2021, s2_2021, viirs_2021, census_1000_2021, census_500_2021, census_250_2021, census_100_2021, census_2021, gee_image_to_np_image, save_np, get_osm_image

CONFIG = get_config()
MAP_TILES = CONFIG['MAP_TILES']
ZOOM_LEVELS = CONFIG['ZOOM_LEVELS']
LOCATIONS = CONFIG['LOCATIONS']

gee_s1 = s1_2021()
gee_s2 = s2_2021()
gee_viirs = viirs_2021()
gee_census_1000 = census_1000_2021()
gee_census_500 = census_500_2021()
gee_census_250 = census_250_2021()
gee_census_100 = census_100_2021()
gee_census = census_2021()


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(id='map-selector', options=[{'label': name, 'value': url} for name, url in MAP_TILES.items()], value=None, clearable=False),
        dcc.Dropdown(id='sec-map-selector', options=[{'label': name, 'value': url} for name, url in MAP_TILES.items()], value=None, clearable=False),
        dcc.Dropdown(id='zoom-selector', options=[{'label': name, 'value': zoom} for name, zoom in ZOOM_LEVELS.items()], value=None, clearable=False),
        dcc.Dropdown(id='location-selector', options=[{'label': name, 'value': name} for name in LOCATIONS.keys()], value=None, clearable=False)
    ], style={'padding': '10px'}),
    html.Div([
        daq.Slider(id='show_secondary', min=0, max=1, value=0.5, step=0.01),
        html.Button("Download Configuration", id="btn-download", style={'margin': '10px 0'})
    ], style={'padding': '10px'}),
    dl.Map(
        id="map",
        center=list(LOCATIONS.values())[0],
        zoom=12,
        children=[
            dl.TileLayer(id="tile-layer", url=list(MAP_TILES.values())[0]),
            dl.TileLayer(id="second-tile-layer", url=list(MAP_TILES.values())[0], opacity=0.5),
            dl.ScaleControl(),
            dl.Rectangle(id="center-rectangle", bounds=get_rectangle_bounds(list(LOCATIONS.values())[0]), color="red", weight=2, fill=False)
        ],
        style={'width': '800px', 'height': '800px'},
        zoomControl=False,
        attributionControl=False
    )
])

@app.callback(
    Output("second-tile-layer", "opacity"),
    Input("show_secondary", "value"),
    prevent_initial_call=True
)
def update_secondary_opacity(value):
    return value

@app.callback(
    Output("second-tile-layer", "url"),
    Input("sec-map-selector", "value"),
    prevent_initial_call=True
)
def update_secondary(selected_tile):
    return selected_tile

@app.callback(
    Output("tile-layer", "url"),
    Input("map-selector", "value"),
    prevent_initial_call=True
)
def update_map(selected_tile):
    return selected_tile

@app.callback(
    Output("map", "zoom"),
    Input("zoom-selector", "value"),
    prevent_initial_call=True
)
def update_zoom(selected_zoom):
    return selected_zoom

@app.callback(
    Output("map", "center"),
    Input("location-selector", "value"),
    prevent_initial_call=True
)
def update_location(selected_city):
    coords = LOCATIONS[selected_city]
    return coords

@app.callback(
    Output("center-rectangle", "bounds"),
    Input("map", "center"),
    prevent_initial_call=True
)
def update_rectangle(center):
    return get_rectangle_bounds([center['lat'], center['lng']])

@app.callback(
    Input("btn-download", "n_clicks"),
    Input("map", "center"),
    prevent_initial_call=True
)
def download(n_clicks, center):
    if ctx.triggered_id == "btn-download" and n_clicks:
        prefix = ''
        print(center)
        lat = center[0]
        lon = center[1]
        #lat = center['lat']
        #lon = center['lng']
        save_np(get_osm_image(lat, lon), f"./downloads/{prefix}osm.npy")
        save_np(gee_image_to_np_image(gee_s1, lat, lon), f"./downloads/{prefix}s1.npy")
        save_np(gee_image_to_np_image(gee_s2, lat, lon, bands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6']), f"./downloads/{prefix}s2_a.npy")
        save_np(gee_image_to_np_image(gee_s2, lat, lon, bands=['B7', 'B8', 'B8A', 'B9', 'B11', 'B12']), f"./downloads/{prefix}s2_b.npy")
        save_np(gee_image_to_np_image(gee_viirs, lat, lon), f"./downloads/{prefix}viirs.npy")
        save_np(gee_image_to_np_image(gee_census_1000, lat, lon), f"./downloads/{prefix}census_1000.npy")
        save_np(gee_image_to_np_image(gee_census_500, lat, lon), f"./downloads/{prefix}census_500.npy")
        save_np(gee_image_to_np_image(gee_census_250, lat, lon), f"./downloads/{prefix}census_250.npy")
        save_np(gee_image_to_np_image(gee_census_100, lat, lon), f"./downloads/{prefix}census_100.npy")
        save_np(gee_image_to_np_image(gee_census, lat, lon), f"./downloads/{prefix}census.npy")
        print("DONE")

if __name__ == '__main__':
    app.run_server(debug=True)