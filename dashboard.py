import dash
from dash import dcc, html, Input, Output, dash_table, callback, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from collections import Counter
import re
from urllib.parse import urlparse
import json

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

# AI-powered question analysis system
class AIQuestionAnalyzer:
    def __init__(self, df):
        self.df = df
        self.keywords = keyword_df['Keyword'].tolist()
        self.domains = df['Domain'].unique().tolist()
        
        # Create a comprehensive knowledge base from ALL article titles
        self.knowledge_base = self.build_comprehensive_knowledge_base()
    
    def build_comprehensive_knowledge_base(self):
        """Build a comprehensive knowledge base from ALL article titles"""
        knowledge = {
            'all_titles': [],
            'word_frequency': {},
            'topic_clusters': {},
            'semantic_patterns': {}
        }
        
        # Process all titles
        for _, article in self.df.iterrows():
            title = article['Title'].lower()
            knowledge['all_titles'].append({
                'title': article['Title'],
                'link': article['Link'],
                'domain': article['Domain'],
                'words': title.split()
            })
            
            # Extract all words for frequency analysis
            words = re.findall(r'\b\w{3,}\b', title)
            for word in words:
                knowledge['word_frequency'][word] = knowledge['word_frequency'].get(word, 0) + 1
        
        return knowledge
    
    def analyze_question(self, question):
        """Universal question analysis with relevance scoring - works for ANY question"""
        question_lower = question.lower()
        
        # Initialize response
        response = {
            'keywords': [],
            'domains': [],
            'title_length_filter': None,
            'response': "",
            'article_count': 0,
            'specific_articles': [],
            'intelligent_analysis': "",
            'related_topics': []
        }
        
        # Extract ALL words from the question
        import re
        question_words = re.findall(r'\b\w{3,}\b', question_lower)
        
        # Calculate relevance scores for all articles
        scored_articles = self.calculate_relevance_scores(question_words, question_lower)
        
        # Sort by relevance score (highest first)
        scored_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Get top relevant articles
        top_articles = scored_articles[:10]  # Top 10 most relevant
        
        # Extract keywords that actually contributed to matches
        contributing_keywords = []
        for article in top_articles:
            if 'matched_keywords' in article:
                contributing_keywords.extend(article['matched_keywords'])
        
        # Remove duplicates and keep order
        seen_keywords = set()
        unique_keywords = []
        for keyword in contributing_keywords:
            if keyword not in seen_keywords:
                unique_keywords.append(keyword)
                seen_keywords.add(keyword)
        
        response['specific_articles'] = top_articles
        response['keywords'] = unique_keywords
        response['article_count'] = len(scored_articles)
        
        # Generate intelligent analysis based on what was found
        response['intelligent_analysis'] = self.generate_universal_analysis(question, top_articles, unique_keywords)
        
        # Generate comprehensive response
        response['response'] = self.generate_comprehensive_response(question, response)
        
        return response
    
    def calculate_relevance_scores(self, question_words, question_lower):
        """Calculate relevance scores for all articles based on question"""
        scored_articles = []
        
        # Define scientific domain weights for better matching
        domain_weights = {
            'microgravity': 3.0,
            'spaceflight': 3.0,
            'space': 2.5,
            'bone': 2.5,
            'muscle': 2.5,
            'cell': 2.0,
            'radiation': 2.5,
            'heart': 2.0,
            'plant': 2.0,
            'drosophila': 2.0,
            'mouse': 2.0,
            'stem': 2.0,
            'gene': 2.0,
            'protein': 1.5,
            'dna': 1.5,
            'rna': 1.5,
            'expression': 1.5,
            'metabolism': 1.5,
            'oxidative': 1.5,
            'stress': 1.5
        }
        
        for _, article in self.df.iterrows():
            title = article['Title'].lower()
            relevance_score = 0
            matched_keywords = []
            
            # Calculate base score from word matches
            for word in question_words:
                if word in title:
                    # Base score for word match
                    word_score = 1.0
                    
                    # Apply domain weight if it's a scientific term
                    if word in domain_weights:
                        word_score *= domain_weights[word]
                    
                    # Bonus for exact phrase matches
                    if f" {word} " in f" {title} ":
                        word_score *= 1.2
                    
                    # Bonus for word appearing multiple times
                    word_count = title.count(word)
                    if word_count > 1:
                        word_score *= (1 + 0.1 * word_count)
                    
                    relevance_score += word_score
                    matched_keywords.append(word)
            
            # Calculate semantic similarity bonus
            semantic_bonus = self.calculate_semantic_similarity(question_lower, title)
            relevance_score += semantic_bonus
            
            # Calculate context relevance
            context_bonus = self.calculate_context_relevance(question_lower, title)
            relevance_score += context_bonus
            
            # Only include articles with some relevance
            if relevance_score > 0:
                scored_articles.append({
                    'title': article['Title'],
                    'link': article['Link'],
                    'domain': article['Domain'],
                    'relevance_score': relevance_score,
                    'matched_keywords': matched_keywords,
                    'semantic_bonus': semantic_bonus,
                    'context_bonus': context_bonus
                })
        
        return scored_articles
    
    def calculate_semantic_similarity(self, question, title):
        """Calculate semantic similarity between question and title"""
        bonus = 0
        
        # Define semantic groups for better matching
        semantic_groups = {
            'biological_processes': ['growth', 'development', 'differentiation', 'regeneration', 'metabolism'],
            'space_effects': ['microgravity', 'spaceflight', 'radiation', 'stress', 'adaptation'],
            'body_systems': ['bone', 'muscle', 'heart', 'brain', 'immune', 'cardiovascular'],
            'research_methods': ['study', 'analysis', 'experiment', 'investigation', 'research'],
            'organisms': ['mouse', 'rat', 'drosophila', 'plant', 'cell', 'tissue']
        }
        
        # Check for semantic group matches
        for group, terms in semantic_groups.items():
            question_has_group = any(term in question for term in terms)
            title_has_group = any(term in title for term in terms)
            
            if question_has_group and title_has_group:
                bonus += 0.5
        
        # Check for related terms
        related_terms = {
            'bone': ['skeletal', 'osteoporosis', 'calcium', 'mineral'],
            'muscle': ['atrophy', 'contraction', 'myofiber', 'skeletal'],
            'microgravity': ['weightlessness', 'zero-g', 'space', 'gravity'],
            'radiation': ['ionizing', 'cosmic', 'exposure', 'dose'],
            'cell': ['cellular', 'tissue', 'organ', 'molecular']
        }
        
        for main_term, related in related_terms.items():
            if main_term in question:
                for related_term in related:
                    if related_term in title:
                        bonus += 0.3
        
        return bonus
    
    def calculate_context_relevance(self, question, title):
        """Calculate context relevance based on question intent"""
        bonus = 0
        
        # Question intent patterns
        if any(word in question for word in ['effect', 'effects', 'impact', 'influence']):
            if any(word in title for word in ['effect', 'impact', 'influence', 'modulate', 'alter']):
                bonus += 0.4
        
        if any(word in question for word in ['study', 'research', 'investigation']):
            if any(word in title for word in ['study', 'research', 'investigation', 'analysis']):
                bonus += 0.3
        
        if any(word in question for word in ['mechanism', 'pathway', 'process']):
            if any(word in title for word in ['mechanism', 'pathway', 'process', 'regulation']):
                bonus += 0.4
        
        if any(word in question for word in ['treatment', 'therapy', 'intervention']):
            if any(word in title for word in ['treatment', 'therapy', 'intervention', 'prevention']):
                bonus += 0.4
        
        # Specificity bonus - longer, more specific titles get bonus
        if len(title.split()) > 8:  # More specific titles
            bonus += 0.2
        
        return bonus
        """Find ALL articles containing a specific word"""
        articles = []
        
        # Search for articles containing the word (case insensitive)
        mask = self.df['Title'].str.contains(word, case=False, na=False)
        matching_articles = self.df[mask]
        
        for _, article in matching_articles.iterrows():
            articles.append({
                'title': article['Title'],
                'link': article['Link'],
                'domain': article['Domain'],
                'matched_word': word
            })
        
        return articles
    
    def generate_universal_analysis(self, question, articles, keywords):
        """Generate intelligent analysis for ANY question with relevance information"""
        if not articles:
            return f"🤔 I couldn't find articles matching your question about '{question}'. Try rephrasing or asking about different aspects of space research."
        
        analysis = []
        
        # Analyze what was found with relevance info
        analysis.append(f"🔍 Found {len(articles)} highly relevant articles for your question.")
        
        # Show relevance scores for top articles
        if articles and 'relevance_score' in articles[0]:
            top_score = articles[0]['relevance_score']
            analysis.append(f"📊 Best match has relevance score: {top_score:.2f}")
        
        # Analyze the topics covered
        if keywords:
            analysis.append(f"📝 Your question involves: {', '.join(keywords)}")
        
        # Provide context based on what was found
        if len(articles) > 0:
            # Analyze the first few articles to provide context
            sample_titles = [article['title'] for article in articles[:3]]
            analysis.append("📚 Here are the most relevant articles:")
            
            # Provide intelligent summary based on actual article titles
            for i, title in enumerate(sample_titles, 1):
                analysis.append(f"• {title[:80]}{'...' if len(title) > 80 else ''}")
        
        return " ".join(analysis)
    
    def generate_comprehensive_response(self, question, response_data):
        """Generate a comprehensive response about the articles"""
        responses = []
        
        if response_data['intelligent_analysis']:
            responses.append(response_data['intelligent_analysis'])
        
        if response_data['article_count'] > 0:
            responses.append(f"📊 Found {response_data['article_count']} publications matching your query.")
        
        if response_data['specific_articles']:
            responses.append(f"📚 Here are {len(response_data['specific_articles'])} relevant articles from your dataset:")
        
        if not responses:
            responses.append("🤔 I can help you explore the research in your dataset. Try asking about any topic related to space research!")
        
        return " ".join(responses)
    
    def find_articles_by_category(self, category, keyword):
        """Find specific articles that match a category"""
        articles = []
        
        # Search for articles containing the keyword
        mask = self.df['Title'].str.contains(keyword, case=False, na=False)
        matching_articles = self.df[mask]
        
        for _, article in matching_articles.iterrows():
            articles.append({
                'title': article['Title'],
                'link': article['Link'],
                'domain': article['Domain']
            })
        
        return articles
    
    def find_articles_by_keyword(self, keyword):
        """Find articles containing a specific keyword"""
        articles = []
        
        # Search for articles containing the keyword (case insensitive)
        mask = self.df['Title'].str.contains(keyword, case=False, na=False)
        matching_articles = self.df[mask]
        
        for _, article in matching_articles.iterrows():
            articles.append({
                'title': article['Title'],
                'link': article['Link'],
                'domain': article['Domain']
            })
        
        return articles
    
    def find_long_title_articles(self):
        """Find articles with long titles"""
        title_lengths = self.df['Title'].str.len()
        long_threshold = title_lengths.quantile(0.8)  # Top 20% longest
        long_articles = self.df[title_lengths >= long_threshold]
        
        articles = []
        for _, article in long_articles.head(5).iterrows():
            articles.append({
                'title': article['Title'],
                'link': article['Link'],
                'domain': article['Domain'],
                'length': len(article['Title'])
            })
        
        return articles
    
    def find_short_title_articles(self):
        """Find articles with short titles"""
        title_lengths = self.df['Title'].str.len()
        short_threshold = title_lengths.quantile(0.2)  # Bottom 20% shortest
        short_articles = self.df[title_lengths <= short_threshold]
        
        articles = []
        for _, article in short_articles.head(5).iterrows():
            articles.append({
                'title': article['Title'],
                'link': article['Link'],
                'domain': article['Domain'],
                'length': len(article['Title'])
            })
        
        return articles
    
    def generate_intelligent_response(self, question, matched_categories, filters):
        """Generate intelligent response based on actual data analysis"""
        responses = []
        
        if filters['article_count'] > 0:
            responses.append(f"📊 Found {filters['article_count']} publications matching your query.")
        
        if matched_categories:
            category_descriptions = {
                'microgravity': "studies on microgravity effects",
                'bone': "bone health and skeletal research",
                'muscle': "muscle atrophy and muscular studies",
                'cell': "cellular and stem cell research",
                'radiation': "radiation effects and space radiation",
                'heart': "cardiac and cardiovascular research",
                'plant': "plant biology and gravitropism",
                'drosophila': "Drosophila and insect studies",
                'mouse': "mouse and rodent experiments"
            }
            
            for category in matched_categories:
                if category in category_descriptions:
                    responses.append(f"🔬 Focus: {category_descriptions[category]}")
        else:
            # If no predefined categories matched, mention the specific keywords found
            if filters['keywords']:
                responses.append(f"🔍 Searching for: {', '.join(filters['keywords'])}")
        
        if filters['specific_articles']:
            responses.append(f"📚 Here are {len(filters['specific_articles'])} relevant articles from your dataset:")
        
        if not responses:
            responses.append("🤔 I couldn't find specific matches in your dataset. Try asking about topics like 'microgravity', 'bone health', 'muscle atrophy', etc.")
        
        return " ".join(responses)
    
    def get_suggestions(self):
        """Get suggested questions based on actual data with relevance focus"""
        return [
            "What are the effects of microgravity on bone health?",
            "How does spaceflight affect muscle atrophy in mice?",
            "Show me research on radiation effects on cellular function",
            "What studies exist on stem cell differentiation in space?",
            "Find publications about heart function during spaceflight",
            "How do plants respond to microgravity conditions?",
            "What research exists on Drosophila behavior in space?",
            "Show me studies on oxidative stress in space",
            "Find publications about gene expression changes in microgravity",
            "What about protein metabolism in space environments?"
        ]

# Initialize AI analyzer
ai_analyzer = AIQuestionAnalyzer(df)

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
                   className="text-center text-muted mb-4"),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("📊 Dashboard", href="/", active=True)),
                dbc.NavItem(dbc.NavLink("🌐 OSDR API Explorer", href="/osdr", external_link=True))
            ], className="justify-content-center mb-4")
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
    
    # AI Question Interface
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🤖 AI-Powered Question Interface"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Ask me anything about the publications:"),
                            dbc.InputGroup([
                                dbc.Input(
                                    id="ai-question-input",
                                    placeholder="e.g., Show me publications about microgravity effects on bone health",
                                    type="text"
                                ),
                                dbc.Button("Ask AI", id="ask-ai-button", color="primary", n_clicks=0)
                            ])
                        ], width=8),
                        dbc.Col([
                            dbc.Label("Suggested questions:"),
                            dcc.Dropdown(
                                id="suggestions-dropdown",
                                options=[{'label': q, 'value': q} for q in ai_analyzer.get_suggestions()],
                                placeholder="Select a suggestion...",
                                clearable=True
                            )
                        ], width=4)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Div(id="ai-response", className="mt-3"),
                            html.Div(id="specific-articles", className="mt-3")
                        ], width=12)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.H6("Recent Questions:", className="mt-3"),
                            html.Div(id="question-history", className="mb-2")
                        ], width=12)
                    ])
                ])
            ])
        ], width=12)
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

# Store for question history
app.layout = html.Div([
    dcc.Store(id='question-history-store', data={'questions': []}),
    app.layout
])

# Callbacks for AI functionality
@app.callback(
    [Output('keyword-filter', 'value'),
     Output('domain-filter', 'value'),
     Output('ai-response', 'children'),
     Output('specific-articles', 'children'),
     Output('ai-question-input', 'value'),
     Output('question-history-store', 'data')],
    [Input('ask-ai-button', 'n_clicks'),
     Input('suggestions-dropdown', 'value')],
    [State('ai-question-input', 'value'),
     State('question-history-store', 'data')]
)
def process_ai_question(n_clicks, suggestion, question_input, history_data):
    """Process AI question and apply filters"""
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return [], [], "", "", "", history_data
    
    # Determine which input triggered the callback
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'suggestions-dropdown' and suggestion:
        question = suggestion
    elif trigger_id == 'ask-ai-button' and question_input:
        question = question_input
    else:
        return [], [], "", "", "", history_data
    
    # Add question to history
    if question and question not in history_data['questions']:
        history_data['questions'].insert(0, question)
        history_data['questions'] = history_data['questions'][:5]  # Keep only last 5
    
    # Analyze the question
    ai_response = ai_analyzer.analyze_question(question)
    
    # Create response component
    response_components = []
    
    # Add intelligent analysis
    if ai_response['intelligent_analysis']:
        response_components.append(
            dbc.Alert(
                ai_response['intelligent_analysis'],
                color="info",
                className="mb-2"
            )
        )
    
    # Add keywords found
    if ai_response['keywords']:
        response_components.append(
            dbc.Alert(
                f"🔍 Found keywords: {', '.join(ai_response['keywords'])}",
                color="success",
                className="mb-2"
            )
        )
    
    # Add main response
    if ai_response['response']:
        response_components.append(
            dbc.Alert(
                ai_response['response'],
                color="primary"
            )
        )
    
    # Create specific articles component
    articles_components = []
    if ai_response['specific_articles']:
        articles_components.append(html.H6("📚 Relevant Articles from Your Dataset:", className="mt-3"))
        
        for i, article in enumerate(ai_response['specific_articles'][:5]):  # Show top 5
            # Create relevance badge
            relevance_badge = ""
            if 'relevance_score' in article:
                score = article['relevance_score']
                if score > 5:
                    badge_color = "success"
                    badge_text = f"High Relevance ({score:.1f})"
                elif score > 2:
                    badge_color = "warning"
                    badge_text = f"Medium Relevance ({score:.1f})"
                else:
                    badge_color = "secondary"
                    badge_text = f"Low Relevance ({score:.1f})"
                
                relevance_badge = dbc.Badge(badge_text, color=badge_color, className="mb-2")
            
            # Show matched keywords
            keywords_info = ""
            if 'matched_keywords' in article and article['matched_keywords']:
                keywords_info = html.P(
                    f"Matched: {', '.join(article['matched_keywords'])}", 
                    className="card-text text-info small"
                )
            
            article_card = dbc.Card([
                dbc.CardBody([
                    relevance_badge,
                    html.H6(f"{i+1}. {article['title'][:100]}{'...' if len(article['title']) > 100 else ''}", 
                           className="card-title"),
                    html.P(f"Domain: {article['domain']}", className="card-text text-muted"),
                    keywords_info,
                    html.A("Read Article", href=article['link'], target="_blank", 
                          className="btn btn-sm btn-outline-primary")
                ])
            ], className="mb-2")
            articles_components.append(article_card)
    
    return ai_response['keywords'], ai_response['domains'], response_components, articles_components, "", history_data

# Callback to display question history
@app.callback(
    Output('question-history', 'children'),
    Input('question-history-store', 'data')
)
def display_question_history(history_data):
    """Display recent questions as clickable badges"""
    if not history_data or not history_data['questions']:
        return html.P("No recent questions", className="text-muted")
    
    badges = []
    for i, question in enumerate(history_data['questions']):
        badges.append(
            dbc.Badge(
                question,
                color="secondary",
                className="me-2 mb-1",
                style={"cursor": "pointer"},
                id=f"history-question-{i}"
            )
        )
    
    return badges

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
