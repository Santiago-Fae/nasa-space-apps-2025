# NASA OSDR API Explorer

## Overview
The NASA OSDR API Explorer is a web application that provides an interactive interface to explore NASA's Open Science Data Repository (OSDR) biological data API. This tool allows users to query and visualize biological data from NASA's GeneLab and ALSDA programs.

## Features

### 🌐 API Explorer
- **Interactive API Testing**: Test different OSDR API endpoints directly from the web interface
- **Parameter Configuration**: Easily configure query parameters and filters
- **Real-time Results**: See API responses immediately with formatted output
- **URL Generation**: Generate and copy API URLs for external use

### 📊 Data Visualization
- **Automatic Charts**: Generate visualizations based on API response data
- **Multiple Formats**: Support for JSON, CSV, TSV, and HTML responses
- **Interactive Tables**: Browse data in interactive, sortable tables

### 🔍 Sample Queries
Pre-configured sample queries for common use cases:
- **All Datasets**: List all available datasets
- **Mouse Spaceflight Studies**: Find studies involving mice in spaceflight
- **RNA-Seq Data**: Access RNA sequencing data
- **Plant Studies**: Find studies involving plants

### 📚 API Documentation
Built-in documentation covering:
- **Endpoint Descriptions**: Detailed information about each API endpoint
- **Query Syntax**: Complete guide to query parameters and filters
- **Output Formats**: Available response formats and their uses
- **Examples**: Real-world usage examples

## Available Endpoints

### REST Interface
- **`/datasets/`** - List all datasets
- **`/dataset/{accession}/`** - Get dataset metadata
- **`/dataset/{accession}/assays/`** - List dataset assays
- **`/dataset/{accession}/assay/{assay}/sample/{sample}/`** - Get sample metadata

### Query Interface
- **`/query/metadata/`** - Query sample-level metadata
- **`/query/data/`** - Query and retrieve data files

## Query Syntax

### Basic Filtering
- `field=value` - Filter by exact value
- `field!=value` - Exclude exact value
- `field=value1|value2` - Multiple values (OR operation)

### Advanced Filtering
- `field=/regex/` - Regular expression matching
- `=field` - Include field if not null
- `field.*` - Include all subfields

### Examples
```
# Find mouse studies
study.characteristics.organism=/Mus musculus/

# Exclude control samples
study.factor value.spaceflight!=basal control

# Multiple datasets
id.accession=OSD-48|OSD-49

# RNA-Seq data only
file.data type=unnormalized counts
```

## Output Formats

- **JSON** - Structured data format
- **CSV** - Comma-separated values
- **TSV** - Tab-separated values
- **HTML** - Interactive browser format
- **Raw** - Original file format

## Usage

### 1. Select Endpoint
Choose from available API endpoints in the dropdown menu.

### 2. Configure Parameters
- Enter accession numbers for dataset-specific queries
- Add query parameters in key=value format
- Use multiple parameters separated by newlines

### 3. Execute Query
Click "Execute API Call" to run the query and view results.

### 4. View Results
- **Response Data**: Formatted display of API response
- **Metadata**: Information about the response (size, format, etc.)
- **Visualization**: Automatic charts based on data content

### 5. Use Sample Queries
Click on sample queries to quickly test common use cases.

## Technical Details

### Base URL
```
https://osdr.nasa.gov/osdr/api/v2
```

### Authentication
The OSDR API is publicly accessible and does not require authentication for most endpoints.

### Rate Limiting
Be mindful of API rate limits when making multiple requests.

### Data Types
The API supports various biological data types:
- **Unnormalized counts** - Raw RNA-Seq data
- **Differential expression** - Processed expression data
- **MultiQC reports** - Quality control reports
- **Metadata** - Sample and study information

## Examples

### Get All Datasets
```
GET /v2/datasets/
```

### Find Mouse Spaceflight Studies
```
GET /v2/query/metadata/
?study.characteristics.organism=/Mus musculus/
&study.factor value.spaceflight!=basal control
&format=csv
```

### Get RNA-Seq Data
```
GET /v2/query/data/
?id.accession=OSD-48|OSD-49
&file.data type=unnormalized counts
&format=csv
```

## Troubleshooting

### Common Issues
1. **Network Errors**: Check internet connection and API availability
2. **Invalid Parameters**: Verify parameter syntax and values
3. **Empty Results**: Try broader search criteria
4. **Timeout Errors**: Reduce query complexity or try smaller datasets

### Error Codes
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (invalid endpoint or data)
- **500**: Server Error (API issue)

## Resources

- [NASA OSDR Official Website](https://osdr.nasa.gov/)
- [GeneLab Data Portal](https://genelab.nasa.gov/)
- [NASA Space Biology Program](https://www.nasa.gov/space-biology-program)

## Support

For technical support or questions about the OSDR API:
- Visit the [NASA GeneLab Support](https://genelab.nasa.gov/support)
- Check the [OSDR Documentation](https://osdr.nasa.gov/osdr/api/v2/)

---

**Note**: This tool is designed for educational and research purposes. Always verify data accuracy and follow NASA's data usage guidelines.
