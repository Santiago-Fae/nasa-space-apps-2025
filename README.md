# 🚀 NASA Space Apps Dashboard - PMC Publications

This is a dynamic and interactive dashboard created in Python using Dash for analyzing PMC (PubMed Central) scientific publications.

## 📋 Features

- **Interactive Visualization**: Dynamic charts with Plotly
- **Advanced Filters**: Filter by keywords and domains
- **Keyword Analysis**: Automatic identification of most frequent words
- **Paginated Table**: Complete data visualization with pagination
- **Responsive Design**: Interface adaptable for different devices
- **Real-time Statistics**: Cards with important metrics

## 🛠️ Installation

1. **Clone the repository** (if applicable) or download the files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 How to Run

1. **Make sure the CSV file is in the same directory**:
   - `SB_publication_PMC.csv`

2. **Run the application**:
   ```bash
   python dashboard.py
   ```

3. **Access the dashboard**:
   - Open your browser and go to: `http://localhost:8050`

## 📊 Dashboard Features

### Statistics Cards
- Total publications
- Number of unique domains
- Keywords analyzed
- Average title length

### Interactive Charts
1. **Top 15 Keywords**: Horizontal bar chart showing the most frequent words
2. **Distribution by Domain**: Pie chart with domain distribution
3. **Title Length Distribution**: Histogram showing title size distribution

### Dynamic Filters
- **Keyword Filter**: Select one or more words to filter the data
- **Domain Filter**: Filter by specific domains

### Data Table
- Complete data visualization
- Automatic pagination (10 items per page)
- Sorting by any column
- Native filters
- Clickable links to publications

## 🔧 Technologies Used

- **Dash**: Web framework for analytical applications
- **Plotly**: Interactive charts
- **Pandas**: Data manipulation
- **Bootstrap**: Responsive design
- **Python**: Main language

## 📁 File Structure

```
├── dashboard.py              # Main application
├── requirements.txt          # Python dependencies
├── SB_publication_PMC.csv    # Publication data
└── README.md                 # This file
```

## 🎨 Customization

The dashboard can be easily customized:

- **Colors**: Modify Bootstrap themes in `dbc.themes.BOOTSTRAP`
- **Charts**: Add new charts using Plotly
- **Filters**: Implement new filters as needed
- **Layout**: Adjust layout using Bootstrap components

## 🌐 Remote Access

To access the dashboard from other devices on the same network:

1. Run with: `python dashboard.py`
2. Access: `http://[YOUR_IP]:8050`

## 📈 Available Analyses

- **Frequency Analysis**: Identification of the most important keywords
- **Domain Analysis**: Distribution of publication sources
- **Size Analysis**: Patterns in title lengths
- **Dynamic Filters**: Segmented data analysis

## 🔍 How to Use

1. **Explore the charts**: Click and drag to zoom, hover for details
2. **Use filters**: Select keywords or domains for specific analysis
3. **Navigate the table**: Use pagination and sorting to find specific data
4. **Click links**: Access original publications directly

## 🐛 Troubleshooting

- **Import error**: Check if all dependencies are installed
- **File not found**: Make sure the CSV is in the correct directory
- **Port occupied**: Change the port in the code if 8050 is in use

## 📝 License

This project is part of the NASA Space Apps Challenge 2025.
