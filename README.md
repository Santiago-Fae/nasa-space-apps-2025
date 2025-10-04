# 🚀 Dashboard NASA Space Apps - Publicações PMC

Este é um dashboard dinâmico e interativo criado em Python usando Dash para análise de publicações científicas do PMC (PubMed Central).

## 📋 Funcionalidades

- **Visualização Interativa**: Gráficos dinâmicos com Plotly
- **Filtros Avançados**: Filtre por palavras-chave e domínios
- **Análise de Palavras-chave**: Identificação automática das palavras mais frequentes
- **Tabela Paginada**: Visualização completa dos dados com paginação
- **Design Responsivo**: Interface adaptável para diferentes dispositivos
- **Estatísticas em Tempo Real**: Cards com métricas importantes

## 🛠️ Instalação

1. **Clone o repositório** (se aplicável) ou baixe os arquivos
2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Como Executar

1. **Certifique-se de que o arquivo CSV está no mesmo diretório**:
   - `SB_publication_PMC.csv`

2. **Execute a aplicação**:
   ```bash
   python dashboard.py
   ```

3. **Acesse o dashboard**:
   - Abra seu navegador e vá para: `http://localhost:8050`

## 📊 Recursos do Dashboard

### Cards de Estatísticas
- Total de publicações
- Número de domínios únicos
- Palavras-chave analisadas
- Tamanho médio dos títulos

### Gráficos Interativos
1. **Top 15 Palavras-chave**: Gráfico de barras horizontal mostrando as palavras mais frequentes
2. **Distribuição por Domínio**: Gráfico de pizza com a distribuição dos domínios
3. **Distribuição do Tamanho dos Títulos**: Histograma mostrando a distribuição dos tamanhos

### Filtros Dinâmicos
- **Filtro por Palavra-chave**: Selecione uma ou mais palavras para filtrar os dados
- **Filtro por Domínio**: Filtre por domínios específicos

### Tabela de Dados
- Visualização completa dos dados
- Paginação automática (10 itens por página)
- Ordenação por qualquer coluna
- Filtros nativos
- Links clicáveis para as publicações

## 🔧 Tecnologias Utilizadas

- **Dash**: Framework web para aplicações analíticas
- **Plotly**: Gráficos interativos
- **Pandas**: Manipulação de dados
- **Bootstrap**: Design responsivo
- **Python**: Linguagem principal

## 📁 Estrutura dos Arquivos

```
├── dashboard.py              # Aplicação principal
├── requirements.txt          # Dependências Python
├── SB_publication_PMC.csv    # Dados das publicações
└── README.md                 # Este arquivo
```

## 🎨 Personalização

O dashboard pode ser facilmente personalizado:

- **Cores**: Modifique os temas Bootstrap em `dbc.themes.BOOTSTRAP`
- **Gráficos**: Adicione novos gráficos usando Plotly
- **Filtros**: Implemente novos filtros conforme necessário
- **Layout**: Ajuste o layout usando componentes Bootstrap

## 🌐 Acesso Remoto

Para acessar o dashboard de outros dispositivos na mesma rede:

1. Execute com: `python dashboard.py`
2. Acesse: `http://[SEU_IP]:8050`

## 📈 Análises Disponíveis

- **Análise de Frequência**: Identificação das palavras-chave mais importantes
- **Análise de Domínios**: Distribuição das fontes das publicações
- **Análise de Tamanho**: Padrões no tamanho dos títulos
- **Filtros Dinâmicos**: Análise segmentada dos dados

## 🔍 Como Usar

1. **Explore os gráficos**: Clique e arraste para zoom, hover para detalhes
2. **Use os filtros**: Selecione palavras-chave ou domínios para análise específica
3. **Navegue pela tabela**: Use paginação e ordenação para encontrar dados específicos
4. **Clique nos links**: Acesse diretamente as publicações originais

## 🐛 Solução de Problemas

- **Erro de importação**: Verifique se todas as dependências estão instaladas
- **Arquivo não encontrado**: Certifique-se de que o CSV está no diretório correto
- **Porta ocupada**: Mude a porta no código se 8050 estiver em uso

## 📝 Licença

Este projeto é parte do NASA Space Apps Challenge 2025.
