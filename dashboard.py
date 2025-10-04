import dash
from dash import dcc, html, Input, Output, dash_table, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from collections import Counter
import re
from urllib.parse import urlparse

# Carregar os dados
df = pd.read_csv('SB_publication_PMC.csv')

# Processar os dados para análise
def extract_keywords(text):
    """Extrai palavras-chave relevantes dos títulos"""
    # Remover caracteres especiais e converter para minúsculas
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    # Dividir em palavras e filtrar palavras muito curtas
    words = [word for word in text.split() if len(word) > 3]
    return words

# Extrair palavras-chave de todos os títulos
all_keywords = []
for title in df['Title']:
    keywords = extract_keywords(title)
    all_keywords.extend(keywords)

# Contar frequência das palavras-chave
keyword_counts = Counter(all_keywords)

# Criar DataFrame para análise de palavras-chave
keyword_df = pd.DataFrame(list(keyword_counts.items()), columns=['Keyword', 'Frequency'])
keyword_df = keyword_df.sort_values('Frequency', ascending=False).head(20)

# Extrair domínios dos links para análise
df['Domain'] = df['Link'].apply(lambda x: urlparse(x).netloc)

# Criar aplicação Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "NASA Space Apps Dashboard - PMC Publications"

# Layout da aplicação
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🚀 NASA Space Apps Dashboard", 
                   className="text-center text-primary mb-4"),
            html.P("Dynamic Analysis of PMC Scientific Publications", 
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    # Statistics Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{len(df)}", className="card-title text-primary"),
                    html.P("Total Publications", className="card-text")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{len(df['Domain'].unique())}", className="card-title text-success"),
                    html.P("Unique Domains", className="card-text")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{len(keyword_df)}", className="card-title text-warning"),
                    html.P("Keywords Analyzed", className="card-text")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{df['Title'].str.len().mean():.0f}", className="card-title text-info"),
                    html.P("Average Title Length", className="card-text")
                ])
            ], className="text-center")
        ], width=3)
    ], className="mb-4"),
    
    # Filters
    dbc.Row([
        dbc.Col([
            dbc.Label("Filter by keyword:"),
            dcc.Dropdown(
                id='keyword-filter',
                options=[{'label': word, 'value': word} for word in keyword_df['Keyword'].head(10)],
                multi=True,
                placeholder="Select keywords..."
            )
        ], width=6),
        dbc.Col([
            dbc.Label("Filter by domain:"),
            dcc.Dropdown(
                id='domain-filter',
                options=[{'label': domain, 'value': domain} for domain in df['Domain'].unique()],
                multi=True,
                placeholder="Select domains..."
            )
        ], width=6)
    ], className="mb-4"),
    
    # Charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📊 Top 15 Most Frequent Keywords"),
                dbc.CardBody([
                    dcc.Graph(id='keyword-chart')
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🌐 Distribution by Domain"),
                dbc.CardBody([
                    dcc.Graph(id='domain-chart')
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Title length distribution chart
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📏 Title Length Distribution"),
                dbc.CardBody([
                    dcc.Graph(id='title-length-chart')
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Data table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📋 Publication Data"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='data-table',
                        columns=[
                            {"name": "Title", "id": "Title", "type": "text"},
                            {"name": "Link", "id": "Link", "type": "text", "presentation": "markdown"},
                            {"name": "Domain", "id": "Domain", "type": "text"},
                            {"name": "Title Length", "id": "Title_Length", "type": "numeric"}
                        ],
                        data=[],
                        page_size=10,
                        sort_action="native",
                        filter_action="native",
                        style_cell={'textAlign': 'left', 'fontSize': 12},
                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }
                        ]
                    )
                ])
            ])
        ], width=12)
    ])
], fluid=True)

# Callbacks for interactivity
@app.callback(
    [Output('keyword-chart', 'figure'),
     Output('domain-chart', 'figure'),
     Output('title-length-chart', 'figure'),
     Output('data-table', 'data')],
    [Input('keyword-filter', 'value'),
     Input('domain-filter', 'value')]
)
def update_charts(selected_keywords, selected_domains):
    # Filter data based on filters
    filtered_df = df.copy()
    
    if selected_keywords:
        mask = filtered_df['Title'].str.contains('|'.join(selected_keywords), case=False, na=False)
        filtered_df = filtered_df[mask]
    
    if selected_domains:
        filtered_df = filtered_df[filtered_df['Domain'].isin(selected_domains)]
    
    # Prepare data for table
    table_data = filtered_df.copy()
    table_data['Title_Length'] = table_data['Title'].str.len()
    table_data['Link'] = table_data['Link'].apply(lambda x: f"[Access]({x})")
    
    # Keyword chart
    keyword_fig = px.bar(
        keyword_df.head(15),
        x='Frequency',
        y='Keyword',
        orientation='h',
        title="Top 15 Keywords",
        color='Frequency',
        color_continuous_scale='viridis'
    )
    keyword_fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=400
    )
    
    # Domain chart
    domain_counts = filtered_df['Domain'].value_counts().head(10)
    domain_fig = px.pie(
        values=domain_counts.values,
        names=domain_counts.index,
        title="Distribution by Domain"
    )
    domain_fig.update_layout(height=400)
    
    # Title length distribution chart
    title_length_fig = px.histogram(
        filtered_df,
        x=filtered_df['Title'].str.len(),
        nbins=20,
        title="Title Length Distribution",
        labels={'x': 'Title Length (characters)', 'y': 'Frequency'}
    )
    title_length_fig.update_layout(height=300)
    
    return keyword_fig, domain_fig, title_length_fig, table_data.to_dict('records')

# Custom CSS styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #f8f9fa;
            }
            .card {
                box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
                border: 1px solid rgba(0, 0, 0, 0.125);
            }
            .card:hover {
                box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
                transition: box-shadow 0.15s ease-in-out;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
