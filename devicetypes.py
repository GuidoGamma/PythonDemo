from flask import Flask, flash
import urllib
import os
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from classes import DeanOci
from bokeh.layouts import layout, widgetbox, column, row
from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d, LinearColorMapper, BasicTicker, FixedTicker, ColorBar, OpenURL, TapTool)
from bokeh.models.glyphs import VBar, HBar, Circle
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tickers import CategoricalTicker
from bokeh.palettes import Spectral6, Category20c
from bokeh.transform import linear_cmap, cumsum
from bokeh.models.widgets import CheckboxGroup
from math import pi

import pandas as pd

app = Flask(__name__)

def getalldevicetypes():
    params = urllib.parse.quote_plus(os.environ.get('DeanOciDatabaseConnection'))
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    Session = sessionmaker(bind=engine)
    s = Session()

    dataDeviceTypes = s.query(DeanOci.DeviceType).order_by(DeanOci.DeviceType.Name).all()
    return dataDeviceTypes

def getdevicetype(devicetype_uid):
    params = urllib.parse.quote_plus(os.environ.get('DeanOciDatabaseConnection'))
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    Session = sessionmaker(bind=engine)
    s = Session()

    query = s.query(DeanOci.DeviceType).filter(DeanOci.DeviceType.Uid.in_([devicetype_uid]))
    dataDeviceType = query.first()

    if dataDeviceType:
        return dataDeviceType
    else:
        flash('Invalid objectreference')

def getmostusedtagschart(devicetype_uid):
    params = urllib.parse.quote_plus(os.environ.get('DeanOciDatabaseConnection'))
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    data = {
        "CustomTagName": [],
        "NrOfTimesUsed": []
    }

    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(DeanOci.DeviceType).filter(DeanOci.DeviceType.Uid.in_([devicetype_uid]))
    dataDeviceType = query.first()

    with engine.connect() as con:
        rs = con.execute(os.environ.get('DeviceTypeCustomTagUsageQuery').replace('{0}', devicetype_uid))

        for row in rs:
            data["CustomTagName"].append(row.Name)
            data["NrOfTimesUsed"].append(row.Aantal)


    plot = create_horizontal_bar_chart(data, "Custom Tags " + dataDeviceType.Name,
                                       "NrOfTimesUsed", "CustomTagName",  "", "")

    return plot

def create_horizontal_bar_chart(data, title, x_name, y_name, x_axis_label, y_axis_label, width=1200,
                                height=300):
    arraycounts = data["NrOfTimesUsed"]

    colors = ["red", "orange", "green"]
    mapper = LinearColorMapper(palette=colors, low=0, high=max(arraycounts))

    source = ColumnDataSource(data)
    ydr = FactorRange(factors=data[y_name])
    xdr = Range1d(start=0, end=max(data[x_name]) * 1.5)

    hover = HoverTool()
    hover.tooltips = """
        <div>Aantal: <strong>@NrOfTimesUsed</strong></div>
    """


    plot = figure(title=title, x_range=xdr, y_range=ydr, plot_width=width,
                  plot_height=height,
                  min_border=0, toolbar_location="above",
                  outline_line_color="#666666")

    plot.hbar(y=y_name, right=x_name, left=0, height=0.5,
              fill_color={'field': "NrOfTimesUsed", 'transform': mapper}, source=source)

    xaxis = LinearAxis(ticker=BasicTicker(mantissas=[1], num_minor_ticks=3))
    yaxis = LinearAxis()

    plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))
    plot.add_tools(hover)

    plot.toolbar.logo = None
    plot.min_border_top = 0
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = "#999999"
    plot.yaxis.axis_label = y_axis_label
    plot.ygrid.grid_line_alpha = 0.1
    plot.xaxis.axis_label = x_axis_label

    plot.xaxis.major_label_orientation = 'horizontal'
    return plot

def getpiechart():

    params = urllib.parse.quote_plus(os.environ.get('DeanOciDatabaseConnection'))
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    Session = sessionmaker(bind=engine)
    s = Session()

    dictdata = {}
    dataDeviceTypes = s.query(DeanOci.DeviceType).all()
    dataDeviceTemplates = s.query(DeanOci.Template).all()

    for devicetype in dataDeviceTypes:
        nrOfTemplates = sum(template.DeviceTypeUid == devicetype.Uid for template in dataDeviceTemplates)
        dictdata[devicetype.Name] = nrOfTemplates

    chart_colors = ['#44e5e2', '#e29e44', '#e244db',
                    '#d8e244', '#eeeeee', '#56e244', '#007bff', 'black']

    data = pd.Series(dictdata).reset_index(name='NrOfTemplates').rename(columns={'index': 'DeviceType'})
    data['angle'] = data['NrOfTemplates'] / data['NrOfTemplates'].sum() * 2 * pi
    data['color'] = chart_colors[:len(dictdata)]

    plot = figure(plot_height=350, title="Verdeling templates", toolbar_location=None,
               tools="hover", tooltips="@DeviceType: @NrOfTemplates", x_range=(-0.5, 1.0))

    plot.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='DeviceType', source=data)

    plot.axis.axis_label = None
    plot.axis.visible = False
    plot.grid.grid_line_color = None

    return plot