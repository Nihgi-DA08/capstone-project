"""Dashboard Dash cho bài capstone Portugal Hotel Booking.

Tóm tắt: file này đọc dữ liệu đã làm sạch trong thư mục `data/`, tạo các biểu đồ
EDA một biến/đa biến, huấn luyện mô hình Linear Regression đơn giản để minh họa
dự báo Average Daily Rate, rồi gắn mọi phần vào layout Dash.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objs as go
import sklearn.model_selection as ms
from dash import Dash, html, dcc, callback, Output, Input
from pandas.api.types import CategoricalDtype
from sklearn.linear_model import LinearRegression

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DATA_VALID_PATH = DATA_DIR / 'data_valid.csv'
COUNTRY_CODES_PATH = DATA_DIR / 'country_codes_list.csv'

COL_NAME_HTL = 'Hotel'
COL_NAME_LEAD_TIME = 'Lead Time'
COL_NAME_ARR_DATE_D = 'Arrival Date Day'
COL_NAME_ARR_DATE_M = 'Arrival Date Month'
COL_NAME_ARR_DATE_Y = 'Arrival Date Year'
COL_NAME_ARR_DATE = 'Arrival Date'
COL_NAME_WKDAY = 'Weekday'
COL_NAME_ADT = 'Adults'
COL_NAME_CHLDN = 'Children'
COL_NAME_CNTRY = 'Country'
COL_NAME_MKT_SEG = 'Market Segment'
COL_NAME_AGT = 'Agent'
COL_NAME_CUST_TYPE = 'Customer Type'
COL_NAME_AVG_DLY_RATE = 'Average Daily Rate'
COL_NAME_CNTRY_NAME = 'Country Name'

month_ord = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
wkday_ord = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

htl_base_clr = ['#636EFA', '#EF553B']

# Đọc dữ liệu local để app chạy ổn trong cả Docker, local dev và nhánh GitHub hiện tại.
df = pd.read_csv(DATA_VALID_PATH)
cntry_codes_df = pd.read_csv(COUNTRY_CODES_PATH)
df[COL_NAME_ARR_DATE_Y] = df[COL_NAME_ARR_DATE_Y].astype(str)
df[COL_NAME_AGT] = df[COL_NAME_AGT].astype(str)
merged_df = pd.merge(df,
                     cntry_codes_df,
                     on=COL_NAME_CNTRY,
                     how='left')
merged_df[COL_NAME_ARR_DATE_Y] = merged_df[COL_NAME_ARR_DATE_Y].astype(str)

# Tạo danh sách lựa chọn cho Dropdown, luôn thêm "All" để reset bộ lọc.
def crt_ddl(col_name):
    options = sorted(df[col_name].dropna().unique().tolist())
    options.append('All')
    return options

# Lọc dữ liệu cho nhóm biểu đồ một biến theo các control trên dashboard.
def uv_mod_df(year, mkt_seg, cust_type):
    fltr_df = df if year == 'All' else df[df[COL_NAME_ARR_DATE_Y] == year]
    fltr_df = fltr_df if mkt_seg == 'All' else fltr_df[fltr_df[COL_NAME_MKT_SEG] == mkt_seg]
    return fltr_df if cust_type == 'All' else fltr_df[fltr_df[COL_NAME_CUST_TYPE] == cust_type]

# Biểu đồ một biến: cơ cấu booking theo loại khách sạn.
def uv_htl(year, mkt_seg, cust_type):
    cnts = uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_HTL].value_counts()
    return go.Pie(labels=cnts.index,
                  values=cnts.values,
                  hole=.5,
                  name='Hotel')

# Biểu đồ một biến: phân phối lead time.
def uv_lead_time(year, mkt_seg, cust_type):
    return go.Histogram(x=uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_LEAD_TIME],
                        nbinsx=30,
                        name='Day')

# Biểu đồ một biến: số booking theo ngày trong tháng.
def uv_arr_date_day(year, mkt_seg, cust_type):
    cnts = uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_ARR_DATE_D].value_counts().sort_index()
    return go.Bar(x=cnts.index,
                  y=cnts.values,
                  name='Day')

# Biểu đồ một biến: số booking theo thứ trong tuần, giữ đúng thứ tự calendar.
def uv_wkday(year, mkt_seg, cust_type):
    cnts = uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_WKDAY].astype(CategoricalDtype(categories=wkday_ord,
                                                                                       ordered=True)).value_counts().sort_index()
    return go.Bar(x=cnts.index.str[:3],
                  y=cnts.values,
                  hovertext=wkday_ord,
                  name='Weekday')

# Biểu đồ một biến: số booking theo tháng, giữ đúng thứ tự January -> December.
def uv_arr_date_month(year, mkt_seg, cust_type):
    cnts = uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_ARR_DATE_M].astype(CategoricalDtype(categories=month_ord,
                                                                                            ordered=True)).value_counts().sort_index()
    return go.Bar(x=cnts.index.str[:3],
                  y=cnts.values,
                  hovertext=month_ord,
                  name='Month')

# Biểu đồ một biến: cơ cấu booking theo năm.
def uv_arr_date_year(year, mkt_seg, cust_type):
    cnts = uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_ARR_DATE_Y].value_counts().sort_index()
    return go.Pie(labels=cnts.index,
                  values=cnts.values,
                  hole=.5,
                  name='Year')

# Biểu đồ một biến: phân bố booking theo quốc gia trên bản đồ.
def uv_cntry(year, mkt_seg, cust_type):
    new_df = pd.merge(cntry_codes_df,
                      uv_mod_df(year, mkt_seg, cust_type).groupby([COL_NAME_CNTRY]).size().reset_index(name='Count'),
                      how='inner')
    return go.Choropleth(locations=new_df[COL_NAME_CNTRY],
                         z=new_df['Count'],
                         hovertext=new_df[COL_NAME_CNTRY_NAME],
                         colorscale='reds',
                         showscale=False,
                         name='Country')

# Biểu đồ một biến: cơ cấu số người lớn.
def uv_adt(year, mkt_seg, cust_type):
    cnts = uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_ADT].value_counts().sort_index()
    return go.Pie(labels=cnts.index,
                  values=cnts.values,
                  hole=.5,
                  rotation=315,
                  name='N.O. Adults')

# Biểu đồ một biến: cơ cấu số trẻ em.
def uv_chldn(year, mkt_seg, cust_type):
    cnts = uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_CHLDN].value_counts().sort_index()
    return go.Pie(labels=cnts.index,
                  values=cnts.values,
                  hole=.5,
                  rotation=270,
                  name='N.O. Children')

# Biểu đồ một biến: cơ cấu booking theo market segment.
def uv_mrk_seg(year, mkt_seg, cust_type):
    cnts = uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_MKT_SEG].value_counts().sort_index()
    return go.Pie(labels=cnts.index,
                  values=cnts.values,
                  hole=.5,
                  rotation=315,
                  name='Name')

# Biểu đồ một biến: phân phối mã agent.
def uv_agt(year, mkt_seg, cust_type):
    return go.Histogram(x=uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_AGT],
                        name='ID')

# Biểu đồ một biến: cơ cấu customer type.
def uv_cust_type(year, mkt_seg, cust_type):
    cnts = uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_CUST_TYPE].value_counts().sort_index()
    return go.Pie(labels=cnts.index,
                  values=cnts.values,
                  hole=.5,
                  rotation=270,
                  name='Type')

# Biểu đồ một biến: phân phối Average Daily Rate.
def uv_avg_dly_rate(year, mkt_seg, cust_type):
    return go.Histogram(x=uv_mod_df(year, mkt_seg, cust_type)[COL_NAME_AVG_DLY_RATE],
                        nbinsx=50,
                        name='USD')

# Lọc dữ liệu cho nhóm biểu đồ đa biến; `.copy()` tránh SettingWithCopyWarning.
def mv_mod_df(year, expand=False):
    fltr_df = merged_df if expand else df
    fltr_df = fltr_df if year == 'All' else fltr_df[fltr_df[COL_NAME_ARR_DATE_Y] == year]
    return fltr_df.copy()

# Đa biến: xu hướng booking theo khách sạn và ngày trong tháng.
def mv_htl_arr_date_day(year):
    grped_df = mv_mod_df(year).groupby([COL_NAME_HTL, COL_NAME_ARR_DATE_D]).size().reset_index(name='Booking Count')
    fig = go.Figure()
    for htl in grped_df[COL_NAME_HTL].unique():
        htl_df = grped_df[grped_df[COL_NAME_HTL] == htl]
        fig.add_trace(go.Scatter(x=htl_df[COL_NAME_ARR_DATE_D],
                                 y=htl_df['Booking Count'],
                                 mode='lines',
                                 name=htl))
    return fig

# Đa biến: xu hướng booking theo khách sạn và thứ trong tuần.
def mv_htl_wkday(year):
    grped_df = mv_mod_df(year).groupby([COL_NAME_HTL, COL_NAME_WKDAY]).size().reset_index(name='Booking Count')
    grped_df[COL_NAME_WKDAY] = pd.Categorical(grped_df[COL_NAME_WKDAY],
                                              categories=wkday_ord,
                                              ordered=True)
    grped_df = grped_df.sort_values([COL_NAME_WKDAY])
    grped_df[COL_NAME_WKDAY] = grped_df[COL_NAME_WKDAY].apply(lambda x: x[:3])
    fig = go.Figure()
    for htl in grped_df[COL_NAME_HTL].unique():
        htl_df = grped_df[grped_df[COL_NAME_HTL] == htl]
        fig.add_trace(go.Scatter(x=htl_df[COL_NAME_WKDAY],
                                 y=htl_df['Booking Count'],
                                 hovertext=wkday_ord,
                                 mode='lines',
                                 name=htl))
    return fig

# Đa biến: xu hướng booking theo khách sạn và tháng.
def mv_htl_arr_date_month(year):
    grped_df = mv_mod_df(year).groupby([COL_NAME_HTL, COL_NAME_ARR_DATE_M]).size().reset_index(name='Booking Count')
    grped_df[COL_NAME_ARR_DATE_M] = pd.Categorical(grped_df[COL_NAME_ARR_DATE_M],
                                                   categories=month_ord,
                                                   ordered=True)
    grped_df = grped_df.sort_values([COL_NAME_ARR_DATE_M])
    grped_df[COL_NAME_ARR_DATE_M] = grped_df[COL_NAME_ARR_DATE_M].apply(lambda x: x[:3])
    fig = go.Figure()
    for htl in grped_df[COL_NAME_HTL].unique():
        htl_df = grped_df[grped_df[COL_NAME_HTL] == htl]
        fig.add_trace(go.Scatter(x=htl_df[COL_NAME_ARR_DATE_M],
                                 y=htl_df['Booking Count'],
                                 hovertext=month_ord,
                                 mode='lines',
                                 name=htl))
    return fig

# Đa biến: tỷ trọng người lớn/trẻ em theo loại khách sạn.
def mv_htl_guest(year):
    mod_df = mv_mod_df(year)
    chldn_df = mod_df.groupby([COL_NAME_HTL])[COL_NAME_CHLDN].sum().reset_index(name=f'Total Children')
    adt_df = mod_df.groupby([COL_NAME_HTL])[COL_NAME_ADT].sum().reset_index(name=f'Total Adults')
    fig = sp.make_subplots(1, 2,
                           specs=[[{'type': 'domain'}, {'type': 'domain'}]])
    fig.add_trace(go.Pie(values=chldn_df[f'Total Children'],
                         labels=chldn_df[COL_NAME_HTL],
                         name=COL_NAME_CHLDN,
                         hole=.4,
                         texttemplate='     %{percent:.1%}     ',
                         marker=dict(line=dict(color='#ffffff',
                                               width=1),
                                     colors=htl_base_clr)), 1, 1)
    fig.add_trace(go.Pie(values=adt_df[f'Total Adults'],
                         labels=adt_df[COL_NAME_HTL],
                         name=COL_NAME_ADT,
                         hole=.7,
                         texttemplate='%{percent:.1%}',
                         marker=dict(line=dict(color='#ffffff',
                                               width=1),
                                     colors=htl_base_clr)), 1, 1)
    return fig

# Đa biến: top quốc gia theo booking và loại khách sạn.
def mv_htl_cntry(year):
    mod_df = mv_mod_df(year, True)
    grped_df = mod_df.groupby([COL_NAME_HTL, COL_NAME_CNTRY_NAME]).size().reset_index(name='Booking Count')
    return px.bar(grped_df[grped_df[COL_NAME_CNTRY_NAME].isin(mod_df.groupby(COL_NAME_CNTRY_NAME).size().nlargest(5).index)],
                 x=COL_NAME_CNTRY_NAME,
                 y='Booking Count',
                 category_orders={COL_NAME_HTL: sorted(mod_df[COL_NAME_HTL].unique())},
                 color=COL_NAME_HTL)

# Đa biến: booking theo khách sạn và market segment.
def mv_htl_mkt_seg(year):
    mod_df = mv_mod_df(year)
    return px.bar(mod_df.groupby([COL_NAME_HTL, COL_NAME_MKT_SEG]).size().reset_index(name='Booking Count'),
                 x=COL_NAME_MKT_SEG,
                 y='Booking Count',
                 category_orders={COL_NAME_HTL: sorted(mod_df[COL_NAME_HTL].unique())},
                 color=COL_NAME_HTL)

# Đa biến: top agent theo booking và loại khách sạn.
def mv_htl_agt(year):
    mod_df = mv_mod_df(year)
    grped_df = mod_df.groupby([COL_NAME_HTL, COL_NAME_AGT]).size().reset_index(name='Booking Count')
    return px.bar(grped_df[grped_df[COL_NAME_AGT].isin(mod_df.groupby(COL_NAME_AGT).size().nlargest(5).index)],
                 x=COL_NAME_AGT,
                 y='Booking Count',
                 category_orders={COL_NAME_HTL: sorted(mod_df[COL_NAME_HTL].unique())},
                 color=COL_NAME_HTL)

# Đa biến: booking theo khách sạn và customer type.
def mv_htl_cust_type(year):
    mod_df = mv_mod_df(year)
    return px.bar(mod_df.groupby([COL_NAME_HTL, COL_NAME_CUST_TYPE]).size().reset_index(name='Booking Count'),
                 x=COL_NAME_CUST_TYPE,
                 y='Booking Count',
                 category_orders={COL_NAME_HTL: sorted(mod_df[COL_NAME_HTL].unique())},
                 color=COL_NAME_HTL)

# Đa biến: phân phối Average Daily Rate theo loại khách sạn.
def mv_htl_avg_dly_rate(year):
    mod_df = mv_mod_df(year)
    fig = sp.make_subplots(1, 1,
                           shared_yaxes=True)
    for htl in mod_df[COL_NAME_HTL].sort_index(ascending=False).unique():
        fig.add_trace(go.Violin(x=mod_df[COL_NAME_HTL][mod_df[COL_NAME_HTL] == htl],
                                y=mod_df[COL_NAME_AVG_DLY_RATE][mod_df[COL_NAME_HTL] == htl],
                                name=htl,
                                box_visible=True,
                                meanline_visible=True,
                                jitter=.05), 1, 1)
    return fig

# Đa biến: quan hệ Lead Time và Average Daily Rate theo loại khách sạn.
def mv_htl_lead_time_avg_dly_rate(year):
    reverse_clr = htl_base_clr[:][::-1]
    return px.scatter(mv_mod_df(year),
                     x=COL_NAME_LEAD_TIME,
                     y=COL_NAME_AVG_DLY_RATE,
                     opacity=.7,
                     color_discrete_sequence=reverse_clr,
                     color=COL_NAME_HTL)

# Chuẩn bị dữ liệu mô hình; `errors='ignore'` giúp chạy được cả khi CSV không còn cột index cũ.
predict_df = df.drop(columns=['Unnamed: 0'], errors='ignore')
new_df = pd.DataFrame({
    COL_NAME_LEAD_TIME : predict_df[COL_NAME_LEAD_TIME],
    COL_NAME_ADT: predict_df[COL_NAME_ADT],
    COL_NAME_ARR_DATE_D: predict_df[COL_NAME_ARR_DATE_D],
    COL_NAME_CHLDN: predict_df[COL_NAME_CHLDN],
    COL_NAME_AVG_DLY_RATE: predict_df[COL_NAME_AVG_DLY_RATE],
})

# Vẽ đường Actual/Predicted để kiểm tra nhanh chất lượng mô hình minh họa.
def predict_db(y_test, y_pred):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=y_test,
                             name='Actual'))
    fig.add_trace(go.Scatter(y=y_pred,
                             name='Predicted'))
    fig.update_layout(title='Predictive model',
                      xaxis_title='Booking Sample',
                      yaxis_title=COL_NAME_AVG_DLY_RATE)
    return fig

# Huấn luyện mô hình Linear Regression với one-hot encoding cho biến phân loại.
X = predict_df.drop(COL_NAME_AVG_DLY_RATE, axis=1)
X = pd.get_dummies(X, drop_first=True) # one-hot encoding
y = predict_df[COL_NAME_AVG_DLY_RATE]
X_train, X_test, y_train, y_test = ms.train_test_split(X, y, test_size=.3, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Khởi tạo app Dash và expose `server` cho Gunicorn/Procfile.
app = Dash(__name__)

server = app.server

# Layout chính gồm EDA dashboard và khu vực predictive analysis.
app.layout = html.Div([
    html.Div(children='EDA Analysis'),
    html.Hr(),
    html.Div(children=[
        html.Div(children=[
            html.Div(children=[
                html.Div(children=[
                    html.Label('Year'),
                    dcc.Dropdown(crt_ddl(COL_NAME_ARR_DATE_Y),
                                 value='All',
                                 id='controls-and-dropdown-y')
                ],
                style={'width': '30%', 'margin': '0 auto', 'text-align': 'center'}),
                html.Div(children=[
                    html.Label('Market Segment'),
                    dcc.Dropdown(crt_ddl(COL_NAME_MKT_SEG),
                                 value='All',
                                 id='controls-and-dropdown-ms')
                ],
                style={'width': '30%', 'margin': '0 auto', 'text-align': 'center'}),
                html.Div(children=[
                    html.Label('Customer Type'),
                    dcc.Dropdown(crt_ddl(COL_NAME_CUST_TYPE),
                                 value='All',
                                 id='controls-and-dropdown-ct')
                ],
                style={'width': '30%', 'margin': '0 auto', 'text-align': 'center'}),
            ], style={'display': 'flex', 'flex-direction': 'row'}),
            dcc.Graph(figure={},
                      id='controls-and-graph-uv')
        ],
        style={'width': '50%', 'display': 'inline-block'}),
        html.Div(children=[
            html.Div(children=[
                html.Div(children=[
                    html.Label('Year'),
                    dcc.Dropdown(crt_ddl(COL_NAME_ARR_DATE_Y),
                                 value='All',
                                 id='controls-and-dropdown-year')
                ],
                style={'width': '30%', 'margin': '0 auto', 'text-align': 'center'})
            ],
            style={'display': 'flex', 'flex-direction': 'row'}),
            dcc.Graph(figure={},
                      id='controls-and-graph-mv')
        ],
        style={'width': '50%', 'display': 'inline-block'})
    ]),
    html.Div(children='Predictive Analysis'),
    html.Hr(),
    dcc.Graph(
        figure=px.scatter_matrix(new_df, title="Scatter Matrix"),
        style={'height': '900px'}
    ),
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(figure=go.Figure(data=go.Heatmap(z=new_df.corr(),
                                                       x=new_df.columns,
                                                       y=new_df.columns,
                                                       colorscale='Viridis',
                                                       colorbar=dict(title="Correlation")),
                                       layout=go.Layout(title=dict(text="Correlation Heatmap"))))
        ],
        style={'width': '50%', 'display': 'inline-block'}),
        html.Div(children=[
            html.Div([
                dcc.Graph(figure=predict_db(y_test.values, y_pred))
            ])
        ],
        style={'width': '50%', 'display': 'inline-block'})
    ])
])

# Callback cập nhật biểu đồ một biến khi người dùng đổi bộ lọc.
@callback(
    Output(component_id='controls-and-graph-uv',
           component_property='figure'),
    Input(component_id='controls-and-dropdown-y',
          component_property='value'),
    Input(component_id='controls-and-dropdown-ms',
          component_property='value'),
    Input(component_id='controls-and-dropdown-ct',
          component_property='value')
)
# Dashboard một biến.
def uv_db(year='All', mkt_seg='All', cust_type='All'):
    figs = sp.make_subplots(7, 4,
                            specs=[[{'type': 'pie', 'rowspan': year == 'All' and 1 or 2, 'colspan': 1}, {'type': 'pie'}, {'type': 'pie'}, {}],
                                   [{'type': 'pie'}, {}, {}, {}],
                                   [{'rowspan': 1, 'colspan': mkt_seg == 'All'and 1 or 2}, {'type': 'pie'}, {'type': cust_type == 'All' and 'pie' or 'histogram', 'rowspan': 1, 'colspan': cust_type == 'All' and 1 or 2}, {}],
                                   [{'type': 'choropleth', 'rowspan': 4, 'colspan': 4}, None, None, None],
                                   [None, None, None, None],
                                   [None, None, None, None],
                                   [None, None, None, None]],
                            subplot_titles=[COL_NAME_HTL, COL_NAME_ADT, COL_NAME_CHLDN, COL_NAME_AVG_DLY_RATE,
                                            year == 'All' and COL_NAME_ARR_DATE_Y or '', COL_NAME_ARR_DATE_M, COL_NAME_WKDAY, COL_NAME_ARR_DATE_D,
                                            COL_NAME_LEAD_TIME, mkt_seg == 'All' and COL_NAME_MKT_SEG or '', cust_type == 'All' and COL_NAME_CUST_TYPE or COL_NAME_AGT, cust_type == 'All' and COL_NAME_AGT or '',
                                            COL_NAME_CNTRY])
    figs.add_trace(uv_htl(year, mkt_seg, cust_type), 1, 1)
    figs.add_trace(uv_adt(year, mkt_seg, cust_type), 1, 2)
    figs.add_trace(uv_chldn(year, mkt_seg, cust_type), 1, 3)
    figs.add_trace(uv_avg_dly_rate(year, mkt_seg, cust_type), 1, 4)
    if year == 'All':
        figs.add_trace(uv_arr_date_year(year, mkt_seg, cust_type), 2, 1)
    figs.add_trace(uv_arr_date_month(year, mkt_seg, cust_type), 2, 2)
    figs.add_trace(uv_wkday(year, mkt_seg, cust_type), 2, 3)
    figs.add_trace(uv_arr_date_day(year, mkt_seg, cust_type), 2, 4)
    figs.add_trace(uv_lead_time(year, mkt_seg, cust_type), 3, 1)
    if mkt_seg == 'All':
        figs.add_trace(uv_mrk_seg(year, mkt_seg, cust_type), 3, 2)
    if cust_type == 'All':
        figs.add_trace(uv_cust_type(year, mkt_seg, cust_type), 3, 3)
    figs.add_trace(uv_agt(year, mkt_seg, cust_type), 3, cust_type == 'All' and 4 or 3)
    figs.add_trace(uv_cntry(year, mkt_seg, cust_type), 4, 1)
    figs.update_layout(height=1000,
                       title_text='Univariate Analysis for Portugal Hotel Booking',
                       showlegend=False)
    return figs

# Callback cập nhật dashboard đa biến theo năm.
@callback(
    Output(component_id='controls-and-graph-mv',
           component_property='figure'),
    Input(component_id='controls-and-dropdown-year',
          component_property='value')
)
# Dashboard đa biến.
def mv_db(year='All'):
    figs = sp.make_subplots(5, 4,
                            specs=[[{'type': 'pie', 'rowspan': 2, 'colspan': 1}, {}, {'rowspan': 1, 'colspan': 2}, None],
                                   [None, {}, {'rowspan': 1, 'colspan': 2}, None], [{}, {}, {'rowspan': 1, 'colspan': 2}, None],
                                   [{'rowspan': 2, 'colspan': 2}, None, {'rowspan': 2, 'colspan': 2}, None],
                                   [None, None, None, None]],
                            subplot_titles=[f'{COL_NAME_ADT} & {COL_NAME_CHLDN}', COL_NAME_AGT, COL_NAME_ARR_DATE_M,
                                            COL_NAME_CUST_TYPE, COL_NAME_WKDAY,
                                            COL_NAME_CNTRY, COL_NAME_MKT_SEG, COL_NAME_ARR_DATE_D,
                                            f'{COL_NAME_LEAD_TIME}          ', f'{COL_NAME_AVG_DLY_RATE} & {COL_NAME_LEAD_TIME}'])
    for trace in mv_htl_guest(year).data:
        figs.add_trace(trace, 1, 1)
    for trace in mv_htl_agt(year).data:
        figs.add_trace(trace, 1, 2)
    for trace in mv_htl_arr_date_month(year).data:
        figs.add_trace(trace, 1, 3)
    for trace in mv_htl_cust_type(year).data:
        figs.add_trace(trace, 2, 2)
    for trace in mv_htl_wkday(year).data:
        figs.add_trace(trace, 2, 3)
    for trace in mv_htl_cntry(year).data:
        figs.add_trace(trace, 3, 1)
    for trace in mv_htl_mkt_seg(year).data:
        figs.add_trace(trace, 3, 2)
    for trace in mv_htl_arr_date_day(year).data:
        figs.add_trace(trace, 3, 3)
    for trace in mv_htl_avg_dly_rate(year).data:
        figs.add_trace(trace, 4, 1)
    for trace in mv_htl_lead_time_avg_dly_rate(year).data:
        figs.add_trace(trace, 4, 3)
    figs.update_layout(height=950,
                       title_text='Multivariate Analysis for Portugal Hotel Booking',
                       showlegend=False,
                       barmode='stack',
                       xaxis6=dict(tickangle=30),
                       colorway=htl_base_clr)
    return figs

# Chạy app khi mở file trực tiếp bằng Python.
if __name__ == '__main__':
    app.run(debug=True)
