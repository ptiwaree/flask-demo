from __future__ import print_function
from flask import Flask, render_template, request, redirect
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
import numpy as np 
import pandas as pd
import bokeh
import requests
bv = bokeh.__version__

app = Flask(__name__)

app.vars={}
cols = ['date', 'open', 'close', 'adj_open', 'adj_close']

colors = {
	'Black': '#000000',
	'Red':   '#FF0000',
	'Green': '#00FF00',
	'Blue':  '#0000FF',
}

@app.route('/')
def main():
	return redirect('/index')

@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/graph',methods=['POST'])
def graph():
	app.vars['ticker'] = request.form['ticker']
	app.vars['select'] = [cols[i] for i in xrange(1,5) if cols[i] in request.form.values()]
	return redirect('/graph')

@app.route('/graph',methods=['GET'])
def graph2():
	df = quandl_request()
	return plot_w_bokeh(df)
	#return render_template('graph.html', ticker=app.vars['ticker'])

def quandl_request():
	# Request data from Quandl and get into pandas
	cols_2_request = ",".join(cols)
	req = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?'
	req = '%sticker=%s&date.gte=20170101&api_key=785i2wEnCjp2sAKg_Cy9&qopts.columns=%s' \
	 % (req, app.vars['ticker'], cols_2_request)
	r = requests.get(req)
	#cols = ['date', 'open', 'close', 'adj_open', 'adj_close']
	df = pd.DataFrame(np.array(r.json()['datatable']['data']), columns=cols)
	df.date = pd.to_datetime(df.date)
	df[['open', 'close', 'adj_open', 'adj_close']] = \
	df[['open', 'close', 'adj_open', 'adj_close']].astype(float)
	return df

def plot_w_bokeh(df):
	# Make Bokeh plot and insert using components
	p = figure(plot_width=450, plot_height=450, title=app.vars['ticker'], x_axis_type="datetime")
	if 'open' in app.vars['select']:
		p.line(df.date, df.open, line_width=2,legend='Opening price', line_color=colors['Green'])
	if 'close' in app.vars['select']:
		p.line(df.date, df.close, line_width=2, line_color=colors['Black'],legend='Closing price')
	if 'adj_close' in app.vars['select']:
		p.scatter(df.date, df.adj_close, fill_color=colors['Red'],legend='Adj Closing price')
	if 'adj_open' in app.vars['select']:
		p.scatter(df.date, df.adj_open, fill_color=colors['Blue'],legend='Adj Opening price')
	p.legend.location = "top_left"
		
	# axis labels
	p.xaxis.axis_label = "Date"
	p.xaxis.axis_label_text_font_style = 'bold'
	p.xaxis.axis_label_text_font_size = '16pt'
	p.xaxis.major_label_orientation = np.pi/4
	p.xaxis.major_label_text_font_size = '14pt'
	p.xaxis.bounds = (df.date.iloc[-1],df.date.iloc[0])
	p.yaxis.axis_label = "Price ($)"
	p.yaxis.axis_label_text_font_style = 'bold'
	p.yaxis.axis_label_text_font_size = '16pt'
	p.yaxis.major_label_text_font_size = '12pt'
	
	#js_resources = INLINE.render_js()
	#css_resources = INLINE.render_css()

	# render graph template
	script, div = components(p)
	html = render_template(
		'graph.html',
		plot_script=script,
		plot_div=div,
		bv=bv,
		ticker=app.vars['ticker'],
		selected_cols=app.vars['select']
	)
	return encode_utf8(html)

if __name__ == '__main__':
	app.run(port=33507, debug=True)
