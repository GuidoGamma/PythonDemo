from flask import Flask
import urllib
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from classes import DeanOci
from bokeh.layouts import layout, widgetbox, column, row
from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d, LinearColorMapper, BasicTicker, PrintfTickFormatter, ColorBar, OpenURL, TapTool)
from bokeh.models.glyphs import VBar, HBar, Circle
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.palettes import Spectral6
from bokeh.transform import linear_cmap
from bokeh.models.widgets import CheckboxGroup

app = Flask(__name__)

def getallcustomtags():
    params = urllib.parse.quote_plus(os.environ.get('DeanOciDatabaseConnection'))
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    Session = sessionmaker(bind=engine)
    s = Session()

    dataCustomTags = s.query(DeanOci.CustomTag).join(DeanOci.DeviceType)\
        .order_by(DeanOci.DeviceType.Name, DeanOci.CustomTag.Name).all()

    return dataCustomTags

