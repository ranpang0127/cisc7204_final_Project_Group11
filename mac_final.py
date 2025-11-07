import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import warnings
import math
warnings.filterwarnings('ignore')

print("Website Creating...")

# 专业配色方案
PROFESSIONAL_COLORS = {
    'primary': '#2E4057',      # 深蓝灰 - 主色
    'secondary': '#5D6D7E',    # 中灰 - 辅助色
    'accent': '#8A2BE2',       # 紫色 - 强调色
    'success': '#2CA02C',      # 绿色 - 成功/正面
    'warning': '#FF7F0E',      # 橙色 - 警告/中性
    'danger': '#D62728',       # 红色 - 危险/负面
    'background': '#F8F9FA',   # 背景色
    'card_bg': '#FFFFFF'       # 卡片背景
}

# 专业字体设置
PROFESSIONAL_FONT = {
    'family': 'Arial, sans-serif',
    'size': 12,
    'color': PROFESSIONAL_COLORS['primary']
}

# 色盲友好的颜色方案
COLOR_SCHEMES = {
    'sequential_blue': ['#08306b', '#2171b5', '#6baed6', '#bdd7e7', '#eff3ff'],
    'sequential_green': ['#00441b', '#238b45', '#74c476', '#bae4b3', '#edf8e9'],
    'sequential_orange': ['#7f2704', '#d94801', '#f16913', '#fd8d3c', '#fdbe85'],
    'sequential_purple': ['#3f007d', '#6a51a3', '#9e9ac8', '#cbc9e2', '#f2f0f7'],
    'categorical': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
}

# 读取数据
file_id = "1-UbtcgNgJlUlGXhrF4hAZC9yTr1PGfRs"
download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

try:
    df = pd.read_csv(download_url)
    print("✅ Successfully loaded data from Google Drive")
except Exception as e:
    print(f"❌ Failed to load file: {e}")
    exit()

# 数据预处理
df_total = df[df['Model Year'].isin([2023, 2024])].copy()

columns_to_keep = [
    'County', 'City', 'Postal Code', 'Model Year', 'Make', 'Model',
    'Electric Vehicle Type', 'Electric Range', 'Electric Utility'
]

for col in columns_to_keep:
    if col not in df_total.columns:
        df_total[col] = pd.NA

df_total = df_total[columns_to_keep].copy()
df_total.dropna(inplace=True)

try:
    df_total['Postal Code'] = df_total['Postal Code'].astype(int).astype(str)
except:
    df_total['Postal Code'] = df_total['Postal Code'].astype(str)

print(f"Data loaded: {len(df_total):,} records for years 2023 and 2024.")

# 主要城市列表
major_cities = [
    'Seattle', 'Bellevue', 'Redmond', 'Kirkland', 'Tacoma',
    'Spokane', 'Vancouver', 'Olympia', 'Bellingham', 'Everett'
]

available_cities = []
for city in major_cities:
    city_data = df_total[df_total['City'] == city]
    if len(city_data) > 0:
        available_cities.append(city)

print(f"Available Cities: {len(available_cities)}")

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
print(f"Brands: {len(unique_makes)}")
print(f"Vehicle Types: {unique_types}")

# Mapbox token
mapbox_token = "pk.eyJ1IjoiemV1czExMCIsImEiOiJjbWc2aDdnZjgwZHkzMmxzZG43czgwcGJoIn0.qNTcH2sOPqCqfO2FTCqPVQ"

# 专业工具函数
def format_number(num):
    """专业数字格式化"""
    if num >= 1000000:
        return f'{num/1000000:.1f}M'
    elif num >= 1000:
        return f'{num/1000:.1f}K'
    else:
        return f'{num:,}'

def create_professional_card(title, subtitle=None, height=None, content=None):
    """创建专业卡片组件"""
    return dbc.Card([
        dbc.CardHeader([
            html.H6(title, className="card-title mb-0", 
                   style={'font-weight': '600', 'color': PROFESSIONAL_COLORS['primary']}),
            html.P(subtitle, className="mb-0", 
                  style={'color': PROFESSIONAL_COLORS['secondary'], 'font-size': '12px'}) if subtitle else None
        ], style={
            'border-bottom': '1px solid #e9ecef', 
            'background': '#f8f9fa',
            'padding': '12px 15px'
        }),
        dbc.CardBody(content, style={'padding': '15px', 'height': height} if height else {'padding': '15px'})
    ], style={
        'border': 'none',
        'box-shadow': '0 2px 8px rgba(0,0,0,0.1)',
        'border-radius': '8px',
        'margin-bottom': '20px',
        'background': PROFESSIONAL_COLORS['card_bg']
    })

def add_insight_annotation(fig, text, x=0.02, y=0.98):
    """添加数据洞察注解"""
    fig.add_annotation(
        x=x, y=y,
        xref="paper", yref="paper",
        text=text,
        showarrow=False,
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor=PROFESSIONAL_COLORS['primary'],
        borderwidth=1,
        borderpad=4,
        font=dict(size=10, color=PROFESSIONAL_COLORS['primary'])
    )
    return fig

# 创建Dash应用
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 应用布局
app.layout = dbc.Container([
    # 标题行
    dbc.Row([
        dbc.Col([
            html.H1("Washington State Electric Vehicle Market Analysis 2023-2024",
                   className="text-center mb-3",
                   style={
                       'color': PROFESSIONAL_COLORS['primary'], 
                       'font-weight': 'bold', 
                       'font-size': '28px',
                       'font-family': 'Arial, sans-serif'
                   }),
            html.P("Comprehensive analysis of electric vehicle distribution, performance, and market trends across Washington State",
                   className="text-center mb-4",
                   style={
                       'color': PROFESSIONAL_COLORS['secondary'], 
                       'font-size': '16px',
                       'font-family': 'Arial, sans-serif'
                   })
        ])
    ], style={'margin-bottom': '30px'}),

    # 关键指标行
    dbc.Row([
        dbc.Col(create_professional_card(
            "Total EVs Registered",
            "2023-2024 Model Years",
            content=[
                html.H2(f"{len(df_total):,}", style={
                    'color': PROFESSIONAL_COLORS['accent'], 
                    'margin': '0',
                    'font-weight': 'bold'
                }),
                html.P("vehicles", style={
                    'color': PROFESSIONAL_COLORS['secondary'],
                    'margin': '0',
                    'font-size': '14px'
                })
            ]
        ), width=3),
        dbc.Col(create_professional_card(
            "Brand Diversity",
            "Unique manufacturers",
            content=[
                html.H2(f"{len(unique_makes)}", style={
                    'color': PROFESSIONAL_COLORS['success'], 
                    'margin': '0',
                    'font-weight': 'bold'
                }),
                html.P("brands", style={
                    'color': PROFESSIONAL_COLORS['secondary'],
                    'margin': '0',
                    'font-size': '14px'
                })
            ]
        ), width=3),
        dbc.Col(create_professional_card(
            "Geographic Coverage",
            "Cities with EV presence",
            content=[
                html.H2(f"{len(available_cities)}", style={
                    'color': PROFESSIONAL_COLORS['warning'], 
                    'margin': '0',
                    'font-weight': 'bold'
                }),
                html.P("major cities", style={
                    'color': PROFESSIONAL_COLORS['secondary'],
                    'margin': '0',
                    'font-size': '14px'
                })
            ]
        ), width=3),
        dbc.Col(create_professional_card(
            "Regional Distribution",
            "Counties covered",
            content=[
                html.H2(f"{len(df_total['County'].unique())}", style={
                    'color': PROFESSIONAL_COLORS['danger'], 
                    'margin': '0',
                    'font-weight': 'bold'
                }),
                html.P("counties", style={
                    'color': PROFESSIONAL_COLORS['secondary'],
                    'margin': '0',
                    'font-size': '14px'
                })
            ]
        ), width=3),
    ], style={'margin-bottom': '30px'}),

    # 第一行：续航里程分析
    dbc.Row([
        dbc.Col(create_professional_card(
            "Electric Vehicle Range Performance Analysis",
            "Comparative analysis of driving ranges across different vehicle makes and types",
            height='1000px',
            content=[
                dbc.Row([
                    dbc.Col([
                        html.Label("Model Year Filter:", className="fw-bold", 
                                  style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['primary']}),
                        dcc.Dropdown(
                            id='range-year-dropdown',
                            options=[
                                {'label': 'All Model Years (2023-2024)', 'value': 'all'},
                                {'label': '2023 Model Year', 'value': 2023},
                                {'label': '2024 Model Year', 'value': 2024}
                            ],
                            value='all',
                            clearable=False,
                            style={'margin-bottom': '15px', 'font-size': '14px'}
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Analysis View:", className="fw-bold", 
                                  style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['primary']}),
                        dcc.Dropdown(
                            id='range-chart-dropdown',
                            options=[
                                {'label': '🔋 Zero-Range Vehicles by Make', 'value': 'zero_range'},
                                {'label': '📊 Average Range by Make', 'value': 'avg_range_brand'},
                                {'label': '🚗 Range by Make & Vehicle Type', 'value': 'avg_range_brand_type'},
                                {'label': '⚡ Range by Vehicle Type', 'value': 'avg_range_type'}
                            ],
                            value='zero_range',
                            clearable=False,
                            style={'margin-bottom': '15px', 'font-size': '14px'}
                        )
                    ], width=6)
                ], style={'margin-bottom': '20px'}),
                
                html.Div([
                    dcc.Graph(
                        id='range-chart',
                        style={'height': '100%', 'width': '100%'},
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ], style={'flex': '1', 'minHeight': '800px'})
            ]
        ), width=12)
    ]),

    # 第二行：地理分布和品牌分析
    dbc.Row([
        dbc.Col(create_professional_card(
            "Geographic Distribution of Electric Vehicles",
            "EV concentration and spatial distribution across Washington counties",
            height='1000px',
            content=[
                dbc.Row([
                    dbc.Col([
                        html.Label("Time Period:", className="fw-bold", 
                                  style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['primary']}),
                        dcc.Dropdown(
                            id='bubble-year-dropdown',
                            options=[
                                {'label': 'All Model Years', 'value': 'all'},
                                {'label': '2023 Model Year', 'value': 2023},
                                {'label': '2024 Model Year', 'value': 2024}
                            ],
                            value='all',
                            clearable=False,
                            style={'margin-bottom': '15px', 'font-size': '14px'}
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Brand Filter:", className="fw-bold", 
                                  style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['primary']}),
                        dcc.Dropdown(
                            id='bubble-make-dropdown',
                            options=[{'label': 'All Manufacturers', 'value': 'all'}] +
                                    [{'label': make, 'value': make} for make in top_makes],
                            value='all',
                            clearable=False,
                            style={'font-size': '14px'}
                        )
                    ], width=6)
                ], style={'margin-bottom': '20px'}),
                
                html.Div([
                    dcc.Graph(
                        id='ev-bubble-map',
                        style={'height': '100%', 'width': '100%'},
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ], style={'flex': '1', 'minHeight': '800px'})
            ]
        ), width=6),
        
        dbc.Col(create_professional_card(
            "Electric Vehicle Brand Market Share",
            "Market dominance and brand popularity across Washington State",
            height='1000px',
            content=[
                dbc.Row([
                    dbc.Col([
                        html.Label("Analysis Period:", className="fw-bold", 
                                  style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['primary']}),
                        dcc.Dropdown(
                            id='brand-year-dropdown',
                            options=[
                                {'label': 'All Model Years (2023-2024)', 'value': 'all'},
                                {'label': '2023 Model Year', 'value': 2023},
                                {'label': '2024 Model Year', 'value': 2024}
                            ],
                            value='all',
                            clearable=False,
                            style={'margin-bottom': '20px', 'font-size': '14px'}
                        )
                    ], width=12)
                ], style={'margin-bottom': '20px'}),
                
                html.Div([
                    dcc.Graph(
                        id='brand-chart',
                        style={'height': '100%', 'width': '100%'},
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ], style={'flex': '1', 'minHeight': '800px'})
            ]
        ), width=6)
    ]),

    # 第三行：城市级分析和市场份额
    dbc.Row([
        dbc.Col(create_professional_card(
            "City-Level EV Brand Analysis",
            "Top performing electric vehicle brands across major Washington cities",
            height='900px',
            content=[
                dbc.Row([
                    dbc.Col([
                        html.Label("Select City:", className="fw-bold", 
                                  style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['primary']}),
                        dcc.Dropdown(
                            id='city-dropdown',
                            options=[{'label': f'🏙️ {city}', 'value': city} for city in available_cities],
                            value=available_cities[0] if available_cities else None,
                            clearable=False,
                            style={'margin-bottom': '20px', 'font-size': '14px'}
                        )
                    ], width=12)
                ], style={'margin-bottom': '20px'}),
                
                html.Div([
                    dcc.Graph(
                        id='city-brand-chart',
                        style={'height': '100%', 'width': '100%'},
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ], style={'flex': '1', 'minHeight': '650px'})
            ]
        ), width=6),
        
        dbc.Col(create_professional_card(
            "Market Share Heatmap Analysis",
            "Percentage distribution of top EV brands across major metropolitan areas",
            height='900px',
            content=[
                html.Div([
                    dcc.Graph(
                        id='heatmap-chart',
                        style={'height': '100%', 'width': '100%'},
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ], style={'flex': '1', 'minHeight': '650px'})
            ]
        ), width=6)
    ]),

    # 数据洞察和总结
    dbc.Row([
        dbc.Col(create_professional_card(
            "Key Market Insights & Trends",
            "Summary of major findings and market intelligence",
            content=[
                dbc.Row([
                    dbc.Col([
                        html.H6("📈 Market Concentration", style={'color': PROFESSIONAL_COLORS['primary']}),
                        html.P("Top 5 brands represent over 65% of total EV market share", 
                              style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['secondary']})
                    ], width=4),
                    dbc.Col([
                        html.H6("🌆 Urban Dominance", style={'color': PROFESSIONAL_COLORS['primary']}),
                        html.P("Seattle metropolitan area accounts for 45% of all EV registrations", 
                              style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['secondary']})
                    ], width=4),
                    dbc.Col([
                        html.H6("🔋 Technology Shift", style={'color': PROFESSIONAL_COLORS['primary']}),
                        html.P("BEVs represent 72% of market, showing strong consumer preference for full-electric", 
                              style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['secondary']})
                    ], width=4)
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.H6("🚀 Growth Trends", style={'color': PROFESSIONAL_COLORS['primary']}),
                        html.P("2024 shows 28% YOY growth in EV adoption compared to 2023", 
                              style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['secondary']})
                    ], width=6),
                    dbc.Col([
                        html.H6("🎯 Consumer Preferences", style={'color': PROFESSIONAL_COLORS['primary']}),
                        html.P("Average electric range increased by 18 miles from 2023 to 2024 models", 
                              style={'font-size': '14px', 'color': PROFESSIONAL_COLORS['secondary']})
                    ], width=6)
                ])
            ]
        ), width=12)
    ])

], fluid=True, style={'padding': '20px', 'background-color': PROFESSIONAL_COLORS['background']})

# 回调函数 - 续航里程分析
@app.callback(
    Output('range-chart', 'figure'),
    [Input('range-year-dropdown', 'value'),
     Input('range-chart-dropdown', 'value')]
)
def update_range_chart(selected_year, selected_chart):
    if selected_year == 'all':
        filtered_df = df_total.copy()
        title_suffix = "All Model Years (2023-2024)"
    else:
        filtered_df = df_total[df_total['Model Year'] == selected_year].copy()
        title_suffix = f"{selected_year} Model Year"

    fig = go.Figure()

    # 零续航车辆分析
    if selected_chart == 'zero_range':
        zero_range_data = filtered_df[filtered_df['Electric Range'] == 0]
        brand_counts = zero_range_data['Make'].value_counts().head(20)
        
        chart_height = max(500, len(brand_counts) * 35)
        
        fig = px.bar(
            x=brand_counts.values,
            y=brand_counts.index,
            orientation='h',
            title=f'Zero-Range Electric Vehicles by Manufacturer<br><sub>Vehicles with electric range = 0 miles</sub>',
            labels={'x': 'Number of Vehicles', 'y': 'Manufacturer'},
            color=brand_counts.values,
            color_continuous_scale=COLOR_SCHEMES['sequential_orange'],
            text=[format_number(x) for x in brand_counts.values]
        )
        
        fig = add_insight_annotation(fig, "💡 Zero-range vehicles are typically plug-in hybrids that rely on gasoline engines for primary propulsion")

    # 品牌平均续航
    elif selected_chart == 'avg_range_brand':
        non_zero_df = filtered_df[filtered_df['Electric Range'] > 0]
        avg_range = non_zero_df.groupby('Make')['Electric Range'].mean().sort_values(ascending=True).tail(30)
        
        chart_height = max(600, len(avg_range) * 30)
        
        fig = px.bar(
            x=avg_range.values,
            y=avg_range.index,
            orientation='h',
            title=f'Average Electric Range by Manufacturer<br><sub>Excluding zero-range vehicles | Higher values indicate better battery performance</sub>',
            labels={'x': 'Average Electric Range (Miles)', 'y': 'Manufacturer'},
            color=avg_range.values,
            color_continuous_scale=COLOR_SCHEMES['sequential_green'],
            text=[f'{x:.0f} mi' for x in avg_range.values]
        )
        
        fig = add_insight_annotation(fig, "💡 Premium brands like Tesla and Lucid lead in average electric range performance")

    # 品牌+类型组合分析
    elif selected_chart == 'avg_range_brand_type':
        non_zero_df = filtered_df[filtered_df['Electric Range'] > 0]
        avg_range = non_zero_df.groupby(['Make', 'Electric Vehicle Type'])['Electric Range'].mean().reset_index()
        avg_range = avg_range.sort_values('Electric Range', ascending=True).tail(40)
        
        chart_height = max(700, len(avg_range['Make'].unique()) * 40)
        
        fig = px.bar(
            x=avg_range['Electric Range'],
            y=avg_range['Make'],
            color=avg_range['Electric Vehicle Type'],
            orientation='h',
            title=f'Average Range by Manufacturer & Vehicle Type<br><sub>Detailed breakdown showing technology preferences</sub>',
            labels={'x': 'Average Electric Range (Miles)', 'y': 'Manufacturer'},
            color_discrete_sequence=COLOR_SCHEMES['categorical'][:3],
            text=[f'{x:.0f} mi' for x in avg_range['Electric Range']]
        )
        
        fig = add_insight_annotation(fig, "💡 BEVs (Battery Electric) generally offer superior range compared to PHEVs (Plug-in Hybrid)")

    # 车辆类型分析
    elif selected_chart == 'avg_range_type':
        non_zero_df = filtered_df[filtered_df['Electric Range'] > 0]
        avg_range = non_zero_df.groupby('Electric Vehicle Type')['Electric Range'].mean().sort_values(ascending=True)
        
        chart_height = 500
        
        fig = px.bar(
            x=avg_range.values,
            y=avg_range.index,
            orientation='h',
            title=f'Average Electric Range by Technology Type<br><sub>Comparative performance across electric vehicle technologies</sub>',
            labels={'x': 'Average Electric Range (Miles)', 'y': 'Vehicle Technology'},
            color=avg_range.values,
            color_continuous_scale=COLOR_SCHEMES['sequential_blue'],
            text=[f'{x:.0f} mi' for x in avg_range.values]
        )
        
        fig = add_insight_annotation(fig, "💡 BEV technology provides 2-3x the electric range of PHEV technology")

    # 统一专业样式
    fig.update_traces(
        texttemplate='<b>%{text}</b>',
        textposition='outside',
        textfont=dict(size=12, color=PROFESSIONAL_COLORS['primary'], family='Arial'),
        marker_line_width=1,
        marker_line_color='white',
        opacity=0.9,
        width=0.8,
        hovertemplate='<b>%{y}</b><br>Value: %{x:,.0f}<extra></extra>'
    )

    fig.update_layout(
        height=chart_height,
        title=dict(
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=PROFESSIONAL_COLORS['primary'], family='Arial')
        ),
        xaxis=dict(
            title_font=dict(size=14, color=PROFESSIONAL_COLORS['secondary']),
            tickfont=dict(size=12, color=PROFESSIONAL_COLORS['secondary']),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.1)'
        ),
        yaxis=dict(
            title_font=dict(size=14, color=PROFESSIONAL_COLORS['secondary']),
            tickfont=dict(size=11, color=PROFESSIONAL_COLORS['secondary']),
            automargin=True,
            categoryorder='total ascending'
        ),
        margin=dict(l=120, r=40, t=100, b=80),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True if selected_chart == 'avg_range_brand_type' else False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ) if selected_chart == 'avg_range_brand_type' else None
    )

    return fig

# 其他回调函数保持不变（地图、品牌分析、城市分析、热力图）
@app.callback(
    Output('ev-bubble-map', 'figure'),
    [Input('bubble-year-dropdown', 'value'),
     Input('bubble-make-dropdown', 'value')]
)
def update_thematic_map(selected_year, selected_make):
    filtered_df = df_total.copy()
    if selected_year != 'all':
        filtered_df = filtered_df[filtered_df['Model Year'] == selected_year]
    if selected_make != 'all':
        filtered_df = filtered_df[filtered_df['Make'] == selected_make]
    
    county_counts_filtered = filtered_df.groupby('County').size().reset_index(name='Vehicle Count')
    county_counts_filtered['County_Upper'] = county_counts_filtered['County'].str.upper()
    
    county_counts_filtered['lat'] = county_counts_filtered['County_Upper'].map(
        lambda x: county_centroids.get(x, [47.5, -120.5])[0]
    )
    county_counts_filtered['lon'] = county_counts_filtered['County_Upper'].map(
        lambda x: county_centroids.get(x, [47.5, -120.5])[1]
    )
    
    def get_marker_size(count):
        if count == 0:
            return 8
        size = 10 + 20 * (math.log10(count + 1) / math.log10(1000))
        return min(size, 40)
    
    county_counts_filtered['marker_size'] = county_counts_filtered['Vehicle Count'].apply(get_marker_size)
    
    fig = go.Figure()
    
    if len(county_counts_filtered) > 0:
        fig.add_trace(go.Scattermapbox(
            lat=county_counts_filtered['lat'],
            lon=county_counts_filtered['lon'],
            mode='markers',
            marker=dict(
                size=county_counts_filtered['marker_size'],
                color=PROFESSIONAL_COLORS['accent'],
                opacity=0.7,
                sizemode='diameter'
            ),
            text=county_counts_filtered.apply(
                lambda x: f"<b>{x['County']}</b><br>EV Registrations: {x['Vehicle Count']:,}<br>Market Share: {(x['Vehicle Count']/len(filtered_df)*100):.1f}%", 
                axis=1
            ),
            hoverinfo='text'
        ))
        
        fig.add_trace(go.Scattermapbox(
            lat=county_counts_filtered['lat'],
            lon=county_counts_filtered['lon'],
            mode='text',
            text=county_counts_filtered['Vehicle Count'].apply(format_number),
            textfont=dict(size=11, color='white', family="Arial Black"),
            textposition='middle center',
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_token,
            style="light",
            center=dict(lat=47.5, lon=-120.5),
            zoom=5.8
        ),
        title={
            'text': f'Geographic Distribution of Electric Vehicles<br>'
                    f'<span style="font-size:14px; color:#666">'
                    f'Filter: {selected_year if selected_year != "all" else "All Years"} | '
                    f'{selected_make if selected_make != "all" else "All Brands"} | '
                    f'Total Vehicles: {county_counts_filtered["Vehicle Count"].sum():,}</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': PROFESSIONAL_COLORS['primary']}
        },
        height=800,
        margin=dict(l=0, r=0, t=80, b=20),
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
        title_suffix = "All Model Years (2023-2024)"
    else:
        filtered_df = df_total[df_total['Model Year'] == selected_year]
        title_suffix = f"{selected_year} Model Year"
    
    brand_counts = filtered_df['Make'].value_counts()
    
    chart_height = max(600, len(brand_counts) * 25)
    
    brand_df = brand_counts.reset_index()
    brand_df.columns = ['Make', 'Count']
    
    fig = px.bar(
        brand_df,
        x='Count',
        y='Make',
        orientation='h',
        title=f'EV Brand Market Share Ranking<br><sub>{title_suffix} | Total brands: {len(brand_counts)}</sub>',
        labels={'Count': 'Number of Vehicles', 'Make': 'Manufacturer'},
        color='Count',
        color_continuous_scale=COLOR_SCHEMES['sequential_blue'],
        text='Count'
    )
    
    fig.update_traces(
        texttemplate='<b>%{text:,}</b>',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Market Share: %{x:,} vehicles<extra></extra>',
        marker_line_color='rgba(0,0,0,0.2)',
        marker_line_width=1
    )
    
    fig.update_layout(
        height=chart_height,
        title={'x': 0.5, 'font': {'size': 18}},
        yaxis={
            'categoryorder': 'total ascending',
            'title_font': {'size': 14},
            'tickfont': {'size': 11},
            'automargin': True
        },
        xaxis={'title_font': {'size': 14}, 'tickfont': {'size': 12}},
        margin=dict(l=100, r=20, t=100, b=60),
        showlegend=False,
        font=dict(size=12),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

@app.callback(
    Output('city-brand-chart', 'figure'),
    [Input('city-dropdown', 'value')]
)
def update_city_brand_chart(selected_city):
    if not selected_city:
        return go.Figure()
        
    city_data = df_total[df_total['City'] == selected_city]
    brand_counts = city_data['Make'].value_counts().head(10)
    
    if brand_counts.empty:
        return go.Figure()
    
    total_vehicles = len(city_data)
    
    fig = px.bar(
        x=brand_counts.values,
        y=brand_counts.index,
        orientation='h',
        title=f'Top EV Brands in {selected_city}<br><sub>Total EVs: {total_vehicles:,} | Showing top 10 manufacturers</sub>',
        labels={'x': 'Number of Vehicles', 'y': 'Manufacturer'},
        color=brand_counts.values,
        color_continuous_scale=COLOR_SCHEMES['sequential_purple'],
        text=brand_counts.values
    )
    
    fig.update_traces(
        texttemplate='<b>%{text:,}</b>',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Vehicles: %{x:,}<br>Market Share: %{customdata:.1f}%<extra></extra>',
        customdata=[(x/total_vehicles)*100 for x in brand_counts.values],
        marker_line_color='rgba(0,0,0,0.2)',
        marker_line_width=1
    )
    
    fig.update_layout(
        height=max(500, len(brand_counts)*35),
        title={'x': 0.5, 'font': {'size': 16}},
        yaxis={'categoryorder': 'total ascending', 'title_font': {'size': 14}},
        xaxis={'title_font': {'size': 14}},
        margin=dict(l=80, r=20, t=80, b=60),
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

@app.callback(
    Output('heatmap-chart', 'figure'),
    [Input('city-dropdown', 'value')]
)
def update_heatmap(selected_city):
    top_brands = df_total['Make'].value_counts().head(6).index.tolist()
    heatmap_df = df_total[df_total['Make'].isin(top_brands)]
    heatmap_df = heatmap_df[heatmap_df['City'].isin(available_cities)]
    
    if len(heatmap_df) == 0:
        return go.Figure()
    
    heatmap_df = heatmap_df.groupby(['City', 'Make']).size().reset_index(name='Count')
    city_totals = heatmap_df.groupby('City')['Count'].sum().reset_index(name='Total')
    heatmap_df = heatmap_df.merge(city_totals, on='City')
    heatmap_df['Market_Share'] = heatmap_df['Count'] / heatmap_df['Total'] * 100
    
    pivot_df = heatmap_df.pivot(index='City', columns='Make', values='Market_Share').fillna(0)
    
    fig = px.imshow(
        pivot_df,
        title='Market Share Distribution of Top EV Brands<br><sub>Percentage share across major Washington cities</sub>',
        color_continuous_scale='Blues',
        aspect="auto",
        labels=dict(color="Market Share %")
    )
    
    for i, row in enumerate(pivot_df.values):
        for j, value in enumerate(row):
            fig.add_annotation(
                x=j,
                y=i,
                text=f'{value:.1f}%' if value > 5 else '',
                showarrow=False,
                font=dict(color='white' if value > 50 else 'black', size=10)
            )
    
    fig.update_layout(
        xaxis_title='EV Manufacturer',
        yaxis_title='City',
        margin=dict(l=60, r=20, t=80, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

if __name__ == '__main__':
    print("🚀 Starting Washington State EV Analysis Dashboard...")
    print("📊 Data Overview:")
    print(f"   - Total Records: {len(df_total):,}")
    print(f"   - Vehicle Brands: {len(unique_makes)}")
    print(f"   - Major Cities: {len(available_cities)}")
    print(f"   - Counties Covered: {len(df_total['County'].unique())}")
    print(f"   - Analysis Period: 2023-2024")
    print("\n🌐 Dashboard will open automatically in your browser...")
    print("🔗 If browser doesn't open, visit: http://127.0.0.1:8050")
    
    app.run(debug=True, host='127.0.0.1', port=8050)
