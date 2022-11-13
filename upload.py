import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
from plotly import tools
import plotly.offline as py

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import PyPDF2

