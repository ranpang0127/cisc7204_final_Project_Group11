import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import warnings
warnings.filterwarnings('ignore')

print("Website Creating...")

# 读取数据 - 适应苹果电脑文件路径
# ✅ Google Drive 文件 ID
file_id = "1-UbtcgNgJlUlGXhrF4hAZC9yTr1PGfRs"
download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

try:
    df = pd.read_csv(download_url)
    print("✅ 成功从 Google Drive 读取数据")
except Exception as e:
    print(f"❌ 读取文件失败：{e}")
    print("请检查文件是否已共享为“任何人都可以查看”")
    exit()

# 筛选2023和2024年的数据
df_total = df[df['Model Year'].isin([2023, 2024])].copy()

# 数据清洗
columns_to_keep = [
    'County', 'City', 'Postal Code', 'Model Year', 'Make', 'Model',
    'Electric Vehicle Type', 'Electric Range', 'Electric Utility'
]

for col in columns_to_keep:
    if col not in df_total.columns:
        df_total[col] = pd.NA

df_total = df_total[columns_to_keep].copy()
df_total.dropna(inplace=True)

# 确保邮政编码是字符串类型
try:
    df_total['Postal Code'] = df_total['Postal Code'].astype(int).astype(str)
except:
    df_total['Postal Code'] = df_total['Postal Code'].astype(str)

print(f"Data loaded: {len(df_total):,} records for years 2023 and 2024.")

# 定义主要城市列表
major_cities = [
    'Seattle', 'Bellevue', 'Redmond', 'Kirkland', 'Tacoma',
    'Spokane', 'Vancouver', 'Olympia', 'Bellingham', 'Everett'
]

# 检查哪些城市在数据中存在
available_cities = []
for city in major_cities:
    city_data = df_total[df_total['City'] == city]
    if len(city_data) > 0:
        available_cities.append(city)

print(f"Available Cities: {len(available_cities)} 个")

# 县坐标数据
county_centroids = {
    'KING': [47.4902, -121.8344], 'PIERCE': [47.0244, -122.1034], 'SNOHOMISH': [48.0464, -121.6977],
    'SPOKANE': [47.6202, -117.4040], 'CLARK': [45.7793, -122.4824], 'THURSTON': [47.5047, -120.4857],
    'KITSAP': [47.6394, -122.6474], 'YAKIMA': [46.4571, -120.7383], 'WHATCOM': [48.8258, -121.7231],
    'FRANKLIN': [46.5348, -118.8989], 'BENTON': [46.2395, -119.5108], 'SKAGIT': [48.4790, -121.7309],
    'ISLAND': [48.1633, -122.5213], 'CLALLAM': [48.0496, -123.9271], 'LEWIS': [46.5776, -122.3929],
    'COWLITZ': [46.1935, -122.6812], 'GRANT': [47.2059, -119.4514], 'MASON': [47.3508, -123.1854],
    'GRAYS HARBOR': [47.1496, -123.7733], 'CHELAN': [47.8692, -120.6199], 'OKANOGAN': [48.5488, -119.7400],
    'STEVENS': [48.3991, -117.8551], 'JEFFERSON': [47.7495, -123.5927], 'WHITMAN': [46.9012, -117.5238],
    'DOUGLAS': [47.7362, -119.6919], 'KITTITAS': [47.1244, -120.6796], 'WALLA WALLA': [46.2298, -118.4784],
    'PACIFIC': [46.5556, -123.7008], 'SAN JUAN': [48.5780, -122.9671], 'LINCOLN': [47.5762, -118.4189],
    'ADAMS': [46.9832, -118.5606], 'FERRY': [48.4702, -118.5171], 'ASOTIN': [46.1911, -117.2035],
    'COLUMBIA': [46.2973, -117.9074], 'GARFIELD': [46.4315, -117.5454], 'KLICKITAT': [45.8737, -120.7883],
    'SKAMANIA': [46.0230, -121.9149], 'WAHKIAKUM': [46.2911, -123.4245], 'PEND OREILLE': [48.5323, -117.2743]
}

# 获取唯一值
unique_years = sorted(df_total['Model Year'].unique())
unique_makes = sorted(df_total['Make'].unique())
unique_types = sorted(df_total['Electric Vehicle Type'].unique())
top_makes = df_total['Make'].value_counts().head(15).index.tolist()

print(f"Model Year: {unique_years}")
print(f"Brands: {len(unique_makes)} 个")
print(f"Vehicle Types: {unique_types}")

# 色盲友好的离散颜色方案
colorblind_discrete_colors = [
    '#1f77b4',  # 蓝色
    '#ff7f0e',  # 橙色
    '#2ca02c',  # 绿色
    '#d62728',  # 红色
    '#9467bd',  # 紫色
    '#8c564b',  # 棕色
    '#e377c2',  # 粉色
    '#7f7f7f',  # 灰色
    '#bcbd22',  # 黄绿色
    '#17becf'   # 青色
]

# 色盲友好的单色方案
colorblind_single_colors = {
    'blue': ['#08306b', '#2171b5', '#6baed6', '#bdd7e7', '#eff3ff'],
    'green': ['#00441b', '#238b45', '#74c476', '#bae4b3', '#edf8e9'],
    'orange': ['#7f2704', '#d94801', '#f16913', '#fd8d3c', '#fdbe85'],
    'purple': ['#3f007d', '#6a51a3', '#9e9ac8', '#cbc9e2', '#f2f0f7']
}

# Mapbox token
mapbox_token = "pk.eyJ1IjoiemV1czExMCIsImEiOiJjbWc2aDdnZjgwZHkzMmxzZG43czgwcGJoIn0.qNTcH2sOPqCqfO2FTCqPVQ"

# 创建Dash应用
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 应用布局
# 应用布局 - 改为4行1列结构
app.layout = dbc.Container([
    # 标题行
    dbc.Row([
        dbc.Col([
            html.H1("Electric Vehicle Analysis in WA (Model Year 2023&2024)",
                   className="text-center mb-3",
                   style={'color': '#2E4057', 'font-weight': 'bold', 'font-size': '26px'}),
            html.P("Explore the distribution, brands, and electric range of electric vehicles in WA in Model Year 2023&2024.",
                   className="text-center mb-4",
                   style={'color': '#5D6D7E', 'font-size': '16px'})
        ])
    ], style={'margin-bottom': '20px'}),

# 第一行：续航里程分析（高度 ×2，图表自适应）
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader([
                html.H5(
                    "Washington State Electric Vehicle Range Analysis",
                    className="card-title mb-0",
                    style={'font-size': '16px'}
                ),
                html.P(
                    "Explore the driving range of different brands and types of electric vehicles",
                    style={'color': '#5D6D7E', 'font-size': '12px', 'margin': '0'}
                )
            ], style={
                'padding': '12px',
                'border-bottom': '1px solid rgba(0,0,0,0.05)'
            }),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Model Year:", className="fw-bold", style={'font-size': '14px'}),
                        dcc.Dropdown(
                            id='range-year-dropdown',
                            options=[
                                {'label': 'Model Year (2023–2024)', 'value': 'all'},
                                {'label': 'Model Year 2023', 'value': 2023},
                                {'label': 'Model Year 2024', 'value': 2024}
                            ],
                            value='all',
                            clearable=False,
                            style={'margin-bottom': '10px', 'font-size': '14px'}
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Visualizations:", className="fw-bold", style={'font-size': '14px'}),
                        dcc.Dropdown(
                            id='range-chart-dropdown',
                            options=[
                                {'label': 'Electric Range = 0 Records', 'value': 'zero_range'},
                                {'label': 'Car Make (All Brands, Excluding 0 Range)', 'value': 'avg_range_brand'},
                                {'label': 'Make and Electric Vehicle Type (Excluding 0 Range)', 'value': 'avg_range_brand_type'},
                                {'label': 'Electric Vehicle Type (Excluding 0 Range)', 'value': 'avg_range_type'}
                            ],
                            value='zero_range',
                            clearable=False,
                            style={'margin-bottom': '10px', 'font-size': '14px'}
                        )
                    ], width=6)
                ], style={'margin-bottom': '15px'}),

                # 图表部分 - 高度自适应父容器
                html.Div([
                    dcc.Graph(
                        id='range-chart',
                        style={
                            'height': '100%',     # 图表自适应卡片高度
                            'width': '100%',
                            'minHeight': '800px'  # 增加最小高度防止内容被压缩
                        },
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ], style={
                    'flex': '1',
                    'display': 'flex',
                    'align-items': 'center',
                    'justify-content': 'center'
                })
            ], style={
                'padding': '15px',
                'height': 'calc(100% - 70px)',
                'display': 'flex',
                'flexDirection': 'column'
            })
        ], style={
            'height': '1000px',  # 卡片高度 ×2
            'margin-bottom': '20px',
            'border': 'none',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.05)',
            'border-radius': '8px',
            'maxWidth': '1600px',
            'margin': '0 auto'
        })
    ])
]),

    # 第二行：EV 地图（高度 ×2）
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("EV Population by County in Washington State Map", className="card-title mb-0", style={'font-size': '16px'}),
                    html.P("EV Population by County", style={'color': '#5D6D7E', 'font-size': '12px', 'margin': '0'})
                ], style={'padding': '12px', 'border-bottom': '1px solid rgba(0,0,0,0.05)'}),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Model Year:", className="fw-bold", style={'font-size': '14px'}),
                            dcc.Dropdown(
                                id='bubble-year-dropdown',
                                options=[
                                    {'label': 'Model Year (2023-2024)', 'value': 'all'},
                                    {'label': 'Model Year 2023', 'value': 2023},
                                    {'label': 'Model Year 2024', 'value': 2024}
                                ],
                                value='all',
                                clearable=False,
                                style={'margin-bottom': '10px', 'font-size': '14px'}
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Brands:", className="fw-bold", style={'font-size': '14px'}),
                            dcc.Dropdown(
                                id='bubble-make-dropdown',
                                options=[{'label': 'All Brands', 'value': 'all'}] +
                                        [{'label': make, 'value': make} for make in top_makes],
                                value='all',
                                clearable=False,
                                style={'font-size': '14px'}
                            )
                        ], width=6)
                    ], style={'margin-bottom': '15px'}),
                    dcc.Graph(
                        id='ev-bubble-map',
                        style={'height': '100%', 'min-height': '800px'},  # 高度 ×2
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ], style={'padding': '15px', 'height': 'calc(100% - 70px)'})
            ], style={
                'height': '1000px',  # 整体卡片高度 ×2
                'margin-bottom': '20px',
                'border': 'none',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.05)',
                'border-radius': '8px',
                'maxWidth': '1600px',
                'margin': '0 auto'
            })
        ])
    ]),

dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader([
                html.H5("Washington State Electric Vehicle Brand Analysis", className="card-title mb-0", style={'font-size': '16px'}),
                html.P("Explore the ranking of different EV brands", style={'color': '#5D6D7E', 'font-size': '12px', 'margin': '0'})
            ], style={'padding': '12px', 'border-bottom': '1px solid rgba(0,0,0,0.05)'}),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Model Year:", className="fw-bold", style={'font-size': '14px'}),
                        dcc.Dropdown(
                            id='brand-year-dropdown',
                            options=[
                                {'label': 'Model Year (2023-2024)', 'value': 'all'},
                                {'label': 'Model Year 2023', 'value': 2023},
                                {'label': 'Model Year 2024', 'value': 2024}
                            ],
                            value='all',
                            clearable=False,
                            style={'margin-bottom': '15px', 'font-size': '14px'}
                        )
                    ], width=12)
                ], style={'margin-bottom': '15px'}),
                html.Div([
                    dcc.Graph(
                        id='brand-chart',
                        style={'height': '100%', 'width': '100%'},  
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ], style={'flex': '1', 'minHeight': '700px'})  # 设置最小高度保证图表充满
            ], style={
                'padding': '15px', 
                'height': 'calc(100% - 70px)',
                'display': 'flex',
                'flexDirection': 'column'
            })
        ], style={
            'height': '1400px',  # 卡片高度 ×2
            'margin-bottom': '20px',
            'border': 'none',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.05)',
            'border-radius': '8px',
            'maxWidth': '1600px',
            'margin': '0 auto'
        })
    ])
]),


# 第四行：城市品牌分析（全宽）
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader([
                html.H5("EV Number Analysis by Make in Main Cities in WA", className="card-title mb-0", style={'font-size': '16px'}),
                html.P("Explore Top 8 EV Brands among Cities", style={'color': '#5D6D7E', 'font-size': '12px', 'margin': '0'})
            ], style={'padding': '12px', 'border-bottom': '1px solid rgba(0,0,0,0.05)'}),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("City:", className="fw-bold", style={'font-size': '14px'}),
                        dcc.Dropdown(
                            id='city-dropdown',
                            options=[{'label': f'{city}', 'value': city} for city in available_cities],
                            value=available_cities[0] if available_cities else None,
                            clearable=False,
                            style={'margin-bottom': '20px', 'font-size': '14px'}
                        )
                    ], width=12)
                ], style={'margin-bottom': '20px'}),
                dcc.Graph(
                    id='city-brand-chart',
                    style={'height': '100%', 'min-height': '650px'},  # 增加图表最小高度
                    config={'displayModeBar': True, 'displaylogo': False}
                )
            ], style={'padding': '20px', 'height': 'calc(100% - 70px)'})  # 增加内边距
        ], style={
            'height': '900px',  
            'border': 'none',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.05)',
            'border-radius': '8px'
        })
    ])
]),
    
# 第五行：城市品牌市场份额热力图
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5(
                        "Market Share of Top 5 EV Brands Across Major WA Cities",
                        className="card-title mb-0",
                        style={'font-size': '16px'}
                    ),
                    html.P(
                        "Explore the percentage market share of top brands across main cities",
                        style={'color': '#5D6D7E', 'font-size': '12px', 'margin': '0'}
                    )
                ], style={'padding': '12px', 'border-bottom': '1px solid rgba(0,0,0,0.05)'}),
                dbc.CardBody([
                    dcc.Graph(
                        id='heatmap-chart',
                        style={'height': '600px', 'width': '100%'},
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ], style={'padding': '15px'})
            ], style={
                'margin-bottom': '20px',
                'border': 'none',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.05)',
                'border-radius': '8px',
                'maxWidth': '1600px',
                'margin': '0 auto'
            })
        ])
    ]),

                
    # 数据统计信息
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Data Analysis Overview", className="card-title", style={'font-size': '16px'}),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H4(f"{len(df_total):,}", style={'color': '#1f77b4', 'margin': '0', 'font-size': '24px'}),
                                html.P("Total", style={'margin': '0', 'color': '#5D6D7E', 'font-size': '14px'})
                            ], className="text-center")
                        ], width=3),
                        dbc.Col([
                            html.Div([
                                html.H4(f"{len(unique_makes)}", style={'color': '#ff7f0e', 'margin': '0', 'font-size': '24px'}),
                                html.P("Make", style={'margin': '0', 'color': '#5D6D7E', 'font-size': '14px'})
                            ], className="text-center")
                        ], width=3),
                        dbc.Col([
                            html.Div([
                                html.H4(f"{len(available_cities)}", style={'color': '#2ca02c', 'margin': '0', 'font-size': '24px'}),
                                html.P("City", style={'margin': '0', 'color': '#5D6D7E', 'font-size': '14px'})
                            ], className="text-center")
                        ], width=3),
                        dbc.Col([
                            html.Div([
                                html.H4(f"{len(df_total['County'].unique())}", style={'color': '#d62728', 'margin': '0', 'font-size': '24px'}),
                                html.P("County", style={'margin': '0', 'color': '#5D6D7E', 'font-size': '14px'})
                            ], className="text-center")
                        ], width=3)
                    ])
                ], style={'padding': '20px'})
            ], style={
                'margin-top': '20px',
                'border': 'none',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.05)',
                'border-radius': '8px'
            })
        ])
    ])
], fluid=True, style={'padding': '15px', 'background-color': '#F8F9FA'})

# 回调函数 - 续航里程分析（自适应尺寸 + 柱子加粗 + 数字放大）
@app.callback(
    Output('range-chart', 'figure'),
    [Input('range-year-dropdown', 'value'),
     Input('range-chart-dropdown', 'value')]
)
def update_range_chart(selected_year, selected_chart):
    if selected_year == 'all':
        filtered_df = df_total.copy()
        title_suffix = "Model Year (2023–2024)"
    else:
        filtered_df = df_total[df_total['Model Year'] == selected_year].copy()
        title_suffix = f"Model Year {selected_year}"

    # 初始化空图表
    fig = go.Figure()

    # ——————————————
    # ① 电池续航为0的车辆
    # ——————————————
    if selected_chart == 'zero_range':
        zero_range_data = filtered_df[filtered_df['Electric Range'] == 0]
        brand_counts = zero_range_data['Make'].value_counts()

    # ✅ 自动调整高度，确保所有品牌标签显示
        chart_height = max(500, len(brand_counts) * 35)
        scaled_height = chart_height * 0.7  
        fig = px.bar(
            x=brand_counts.values,
            y=brand_counts.index,
            orientation='h',
            title=f'Count of Car Makes with Electric Range = 0',
            labels={'x': 'Count', 'y': 'Make'},
            color=brand_counts.values,
            color_continuous_scale=colorblind_single_colors['orange'],
            text=brand_counts.values
    )

        fig.update_traces(
            textposition='auto',
            marker_line_width=0.5
        )

    # 缩小整体效果
        fig.update_layout(
            height=scaled_height,
            font=dict(size=12*0.75),     # 字体缩小0.85倍
            margin=dict(l=80, r=40, t=60, b=40),  # 保持边距比例
            bargap=0.25  # 柱子宽度稍微细一点
        )


    # ——————————————
    # ② 品牌平均续航
    # ——————————————
    elif selected_chart == 'avg_range_brand':
        non_zero_df = filtered_df[filtered_df['Electric Range'] > 0]
        avg_range = non_zero_df.groupby('Make')['Electric Range'].mean().sort_values(ascending=True)

        chart_height = max(500, len(avg_range) * 35)

        fig = px.bar(
            x=avg_range.values,
            y=avg_range.index,
            orientation='h',
            title=f'Average Electric Range by Make (Excluding 0 Range) — {title_suffix}',
            labels={'x': 'Average Range (Miles)', 'y': 'Make'},
            color=avg_range.values,
            color_continuous_scale=colorblind_single_colors['green'],
            text=[f'{x:.1f}' for x in avg_range.values]
        )

        fig.update_layout(height=chart_height)

    # ——————————————
    # ③ 品牌+类型组合平均续航
    # ——————————————
    elif selected_chart == 'avg_range_brand_type':
        non_zero_df = filtered_df[filtered_df['Electric Range'] > 0]
        avg_range = non_zero_df.groupby(['Make', 'Electric Vehicle Type'])['Electric Range'].mean().reset_index()
        avg_range = avg_range.sort_values('Electric Range', ascending=True)

        chart_height = max(600, len(avg_range['Make'].unique()) * 35)

        fig = px.bar(
            x=avg_range['Electric Range'],
            y=avg_range['Make'],
            color=avg_range['Electric Vehicle Type'],
            orientation='h',
            title=f'Average Electric Range by Make & Type — {title_suffix}',
            labels={'x': 'Average Range (Miles)', 'y': 'Make'},
            color_discrete_sequence=colorblind_discrete_colors,
            text=[f'{x:.1f}' for x in avg_range['Electric Range']]
        )

        fig.update_layout(height=chart_height)

    # ——————————————
    # ④ 车辆类型平均续航
    # ——————————————
    elif selected_chart == 'avg_range_type':
        non_zero_df = filtered_df[filtered_df['Electric Range'] > 0]
        avg_range = non_zero_df.groupby('Electric Vehicle Type')['Electric Range'].mean().sort_values(ascending=True)

        fig = px.bar(
            x=avg_range.values,
            y=avg_range.index,
            orientation='h',
            title=f'Average Electric Range by Vehicle Type — {title_suffix}',
            labels={'x': 'Average Range (Miles)', 'y': 'Vehicle Type'},
            color=avg_range.values,
            color_continuous_scale=colorblind_single_colors['blue'],
            text=[f'{x:.1f}' for x in avg_range.values]
        )

    # ——————————————
    # 统一视觉样式调整（加粗柱子 + 放大文字 + 自适应高度）
    # ——————————————
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        textfont=dict(size=14, color='black', family='Arial Black'),
        marker_line_width=1.2,       # 柱子边框略加粗
        marker_line_color='white',
        opacity=0.95,
        width=0.9,                   # 柱子加粗
        hovertemplate='<b>%{y}</b><br>Value: %{x}<extra></extra>'
    )

    fig.update_layout(
        autosize=True,
        title=dict(
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#2E4057', family='Arial Black')
        ),
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            automargin=True,          # ✅ 防止品牌名称被截断
            categoryorder='total ascending'
        ),
        margin=dict(l=180, r=40, t=60, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False
    )

    return fig


def format_number(num): 
    if num >= 1000: 
        return f"{num/1000:.1f}k".replace('.0k', 'k') 
    else: 
        return str(num)
    
# 回调函数 - 专题地图（自适应页面大小 + 气泡尺寸整体缩小一倍）
@app.callback(
    Output('ev-bubble-map', 'figure'),
    [Input('bubble-year-dropdown', 'value'),
     Input('bubble-make-dropdown', 'value')]
)
def update_thematic_map(selected_year, selected_make):
    # 数据过滤
    filtered_df = df_total.copy()
    if selected_year != 'all':
        filtered_df = filtered_df[filtered_df['Model Year'] == selected_year]
    if selected_make != 'all':
        filtered_df = filtered_df[filtered_df['Make'] == selected_make]
    
    # 按县统计数量
    county_counts_filtered = filtered_df.groupby('County').size().reset_index(name='Vehicle Count')
    county_counts_filtered['County_Upper'] = county_counts_filtered['County'].str.upper()
    
    # 匹配经纬度
    county_counts_filtered['lat'] = county_counts_filtered['County_Upper'].map(
        lambda x: county_centroids.get(x, [47.5, -120.5])[0]
    )
    county_counts_filtered['lon'] = county_counts_filtered['County_Upper'].map(
        lambda x: county_centroids.get(x, [47.5, -120.5])[1]
    )
    
    # 调整气泡尺寸公式（整体缩小一倍 + 优化对数变化）
    import math
    def get_marker_size(count):
        if count == 0:
            return 8  # 更小的基础气泡
        # 对数缩放，使数量差异更平滑
        size = 10 + 20 * (math.log10(count + 1) / math.log10(1000))  # 原来是 20 + 40
        return min(size, 40)  # 最大尺寸由 80 缩小到 40
    
    county_counts_filtered['marker_size'] = county_counts_filtered['Vehicle Count'].apply(get_marker_size)
    
    # 创建地图
    fig = go.Figure()
    
    if len(county_counts_filtered) > 0:
        # 添加紫色气泡
        fig.add_trace(go.Scattermapbox(
            lat=county_counts_filtered['lat'],
            lon=county_counts_filtered['lon'],
            mode='markers',
            marker=dict(
                size=county_counts_filtered['marker_size'],
                color='#8A2BE2',
                opacity=0.85,
                sizemode='diameter'
            ),
            text=county_counts_filtered.apply(
                lambda x: f"{x['County']}<br>EV Number: {x['Vehicle Count']:,}", 
                axis=1
            ),
            hoverinfo='text'
        ))
        
        # 添加白色数字标注
        fig.add_trace(go.Scattermapbox(
            lat=county_counts_filtered['lat'],
            lon=county_counts_filtered['lon'],
            mode='text',
            text=county_counts_filtered['Vehicle Count'].apply(format_number),
            textfont=dict(
                size=13,
                color='white',
                family="Arial Black"
            ),
            textposition='middle center',
            hoverinfo='skip'
        ))
    
    # 自适应布局
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_token,
            style="light",
            center=dict(lat=47.5, lon=-120.5),
            zoom=5.8
        ),
        title={
            'text': f'EV Distribution Map around WA <br>'
                    f'<span style="font-size:14px; color:#666">'
                    f'Filter: {selected_year if selected_year != "all" else "Model Year"} | '
                    f'{selected_make if selected_make != "all" else "Make"} | '
                    f'Total: {county_counts_filtered["Vehicle Count"].sum():,}</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2E4057'}
        },
        height=None,  # 图表高度自适应
        margin=dict(l=0, r=0, t=60, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig



@app.callback(
    Output('brand-chart', 'figure'),
    [Input('brand-year-dropdown', 'value')]
)
def update_brand_chart(selected_year):
    if selected_year == 'all':
        filtered_df = df_total.copy()
        title_suffix = "Model Year (2023-2024)"
    else:
        filtered_df = df_total[df_total['Model Year'] == selected_year]
        title_suffix = f"{selected_year} Model Year"
    
    brand_counts = filtered_df['Make'].value_counts()
    
    # Dynamic height
    per_brand_height = 40
    chart_height = max(500, len(brand_counts) * per_brand_height)
    
    scale = 0.7
    scaled_height = chart_height * scale
    font_scale = 14 * scale
    title_scale = 18 * scale

    # Create DataFrame
    brand_df = brand_counts.reset_index()
    brand_df.columns = ['Make', 'Count']
    
    fig = px.bar(
        brand_df,
        x='Count',
        y='Make',
        orientation='h',
        title=f'EV Brands Count Ranking in WA - {title_suffix}',
        labels={'Count': 'Count', 'Make': 'Make'},
        color='Count',
        color_continuous_scale=colorblind_single_colors['blue'],
        text='Count'
    )
    
    fig.update_traces(
        texttemplate='<b>%{text:,}</b>',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Vehicles: %{x:,}<extra></extra>',
        marker_line_color='rgba(0,0,0,0.3)',
        marker_line_width=1.5
    )
    
    fig.update_layout(
        height=scaled_height,
        title={'x': 0.5, 'font': {'size': title_scale}},
        yaxis={
            'categoryorder': 'total ascending',
            'title_font': {'size': font_scale},
            'automargin': True
        },
        xaxis={'title_font': {'size': font_scale}},
        margin=dict(l=80*scale, r=20*scale, t=60*scale, b=40*scale),
        showlegend=False,
        font=dict(size=font_scale),
        bargap=0.2
    )
    
    return fig


@app.callback(
    Output('city-brand-chart', 'figure'),
    [Input('city-dropdown', 'value')]
)
def update_city_brand_chart(selected_city):
    if not selected_city:
        fig = go.Figure()
        fig.update_layout(title="Select City", height=400)
        return fig

    city_data = df_total[df_total['City'] == selected_city]
    if city_data.empty:
        fig = go.Figure()
        fig.update_layout(title=f"{selected_city} - No Data", height=400)
        return fig

    brand_counts = city_data['Make'].value_counts().head(8)
    if brand_counts.empty:
        fig = go.Figure()
        fig.update_layout(title=f"{selected_city} - No Data", height=400)
        return fig

    scale = 0.8

    fig = px.bar(
        x=brand_counts.values,
        y=brand_counts.index,
        orientation='h',
        title=f'{selected_city} - Top 8 EV Brands',
        labels={'x': 'Count', 'y': 'Make'},
        color=brand_counts.values,
        color_continuous_scale=colorblind_single_colors['purple'],
        text=brand_counts.values
    )

    fig.update_traces(
        texttemplate='<b>%{text:,}</b>',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Count: %{x:,}<extra></extra>',
        marker_line_color='rgba(0,0,0,0.3)',
        marker_line_width=1.5,
        width=0.8 * scale
    )

    fig.update_layout(
        autosize=True,
        height=max(400, len(brand_counts)*40*scale),
        title={'x': 0.5, 'font': {'size': 18 * scale}},
        yaxis={'categoryorder': 'total ascending', 'title_font': {'size': 14 * scale}},
        xaxis={'title_font': {'size': 14 * scale}},
        margin=dict(l=70*scale, r=20*scale, t=60*scale, b=40*scale),
        showlegend=False,
        font=dict(size=14 * scale)
    )

    return fig



@app.callback(
    Output('heatmap-chart', 'figure'),
    [Input('city-dropdown', 'value')]  # 可以用城市下拉过滤，或者用全局数据
)
def update_heatmap(selected_city):
    # 取城市和品牌前5
    top_brands = df_total['Make'].value_counts().head(5).index.tolist()
    heatmap_df = df_total[df_total['Make'].isin(top_brands)]
    
    # 过滤主要城市
    heatmap_df = heatmap_df[heatmap_df['City'].isin(available_cities)]
    
    if len(heatmap_df) == 0:
        return go.Figure()  # 空图表
    
    # 计算市场份额 %
    heatmap_df = heatmap_df.groupby(['City', 'Make']).size().reset_index(name='Count')
    city_totals = heatmap_df.groupby('City')['Count'].sum().reset_index(name='Total')
    heatmap_df = heatmap_df.merge(city_totals, on='City')
    heatmap_df['Market_Share'] = heatmap_df['Count'] / heatmap_df['Total'] * 100
    
    # 生成透视表
    pivot_df = heatmap_df.pivot(index='City', columns='Make', values='Market_Share').fillna(0)
    
    fig = px.imshow(
        pivot_df,
        title='Market Share of Top 5 EV Brands Across Major WA Cities (%)',
        color_continuous_scale='Blues',
        aspect="auto"
    )
    
    # 添加百分比标注
    for i, row in enumerate(pivot_df.values):
        for j, value in enumerate(row):
            fig.add_annotation(
                x=j,
                y=i,
                text=f'{value:.1f}%',
                showarrow=False,
                font=dict(color='white' if value > 50 else 'black', size=10)
            )
    
    fig.update_layout(
        xaxis_title='EV Brand',
        yaxis_title='City',
        margin=dict(l=60, r=20, t=40, b=25),
        bargap=0
    )
    
    return fig


if __name__ == '__main__':
    print("🌐 启动华盛顿州电动汽车综合分析统一网站...")
    print("📊 数据统计:")
    print(f"   - 总记录数: {len(df_total):,}")
    print(f"   - 汽车品牌: {len(unique_makes)}")
    print(f"   - 主要城市: {len(available_cities)}")
    print(f"   - 涉及县数: {len(df_total['County'].unique())}")
    print(f"   - 年份范围: 2023-2024")
    print("\n🌐 网站将在浏览器中自动打开...")
    print("🔗 如果浏览器没有自动打开，请访问: http://127.0.0.1:8050")
    
    app.run(debug=True, host='127.0.0.1', port=8050)




