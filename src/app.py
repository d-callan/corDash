import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import base64
from scipy.stats import pearsonr, spearmanr
import pandas as pd
import numpy as np
import networkx as nx
import logging
import io

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div(
    children=[
        html.Link(
            rel='stylesheet',
            href='https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css'  # Replace with the correct path to your Material UI stylesheet
        ),
        html.H3('Correlation Matrix as Network Visualization'),
        html.Div(
            children=[
                # Side panel content here
                html.Label('Upload Data Table', style={'fontWeight': 'bold', 'color': 'black', 'fontSize': '16px'}),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=False
                ),
                html.P(),
                html.Label('Upload Second Data Table (optional)', style={'fontWeight': 'bold', 'color': 'black', 'fontSize': '16px'}),
                dcc.Upload(
                    id='upload-data2',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=False
                )
            ],
            style={
                'width': '30%',  # adjust the width as needed
                'float': 'left',  # float the side panel to the left
                'padding': '20px'  # add padding for spacing
            }
        ),
        html.Div(
            children=[
                dcc.Tabs(
                    id='tabs',
                    children=[
                        dcc.Tab(label='Network', value='network'),
                        dcc.Tab(label='Table', value='table')
                    ],
                    value='network'
                ),
                html.Div(id='tab-content')
            ],
            style={
                'width': '70%',  # adjust the width as needed
                'float': 'right',  # float the main content to the right
                'padding': '20px'  # add padding for spacing
            }
        )
    ]
)

def load_data(contents, filename):
    """
    Load the uploaded data.

    Parameters:
    - contents (str): The contents of the uploaded file.
    - filename (str): The name of the uploaded file.

    Returns:
    - pandas.DataFrame: The loaded data.
    """
    content_type, content_string = contents.split(',')
    decoded_contents = base64.b64decode(content_string)
    return pd.read_table(io.StringIO(decoded_contents.decode('utf-8')))

def correlation_matrix(df, df2=None):
    """
    Calculate the correlation matrix.

    Parameters:
    - df (pandas.DataFrame): The DataFrame to calculate the correlation matrix from.

    Returns:
    - pandas.DataFrame: The correlation matrix.
    """
    if df2 is not None:
        df = pd.concat([df, df2])
    # Calculate the correlation matrix with pvalues
    p_values_matrix = df.apply(lambda col: df.apply(lambda col2: pearsonr(col, col2)[1]))
    correlation_matrix = df.apply(lambda col: df.apply(lambda col2: pearsonr(col, col2)[0]))
    # if df2 is none, find upper triangle of correlation matrix without diagonal
    if df2 is None:
        correlation_matrix = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(np.bool))
        p_values_matrix = p_values_matrix.where(np.triu(np.ones(p_values_matrix.shape), k=1).astype(np.bool))
    # if df2 is not none, find pairwise correlation between df and df2
    else:
        correlation_matrix = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(np.bool))
        p_values_matrix = p_values_matrix.where(np.triu(np.ones(p_values_matrix.shape), k=1).astype(np.bool))
        
    return correlation_matrix, p_values_matrix

def matrix_to_edgelist(correlation_matrix, p_values_matrix):
    """
    Convert the correlation matrix to an edgelist.

    Parameters:
    - correlation_matrix (pandas.DataFrame): The correlation matrix.

    Returns:
    - pandas.DataFrame: The edgelist.
    """
    edge_list = correlation_matrix.stack().reset_index()
    edge_list.columns = ['source', 'target', 'correlation']
    edge_list['p_value'] = p_values_matrix.stack().reset_index()['level_2']
    return edge_list

def generate_table(df):
    """
    Generate a table from a Pandas DataFrame.

    Parameters:
    - df (pandas.DataFrame): The DataFrame to generate the table from.

    Returns:
    - html.Table: The table.
    """
    return html.Table(
        children=[
            html.Thead(
                html.Tr(
                    children=[
                        html.Th(col) for col in df.columns
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        children=[
                            html.Td(df.iloc[i][col]) for col in df.columns
                        ]
                    ) for i in range(len(df))
                ]
            )
        ]
    )

def generate_network(edge_list):
    """
    Generate a network from a Pandas DataFrame.

    Parameters:
    - edge_list (pandas.DataFrame): The edge list containing columns 'source', 'target', 'correlation' and 'p_value'.

    Returns:
    - networkx.Graph: The network.
    """
    G = nx.from_pandas_edgelist(edge_list, source='source', target='target', edge_attr=['correlation', 'p_value'])
    # color edges by whether the correlation is positive or negative
    for edge in G.edges:
        if G[edge[0]][edge[1]]['correlation'] > 0:
            G[edge[0]][edge[1]]['color'] = 'green'
        else:
            G[edge[0]][edge[1]]['color'] = 'red'
    # set edge thickness based on absolute value of correlation
    for edge in G.edges:
        G[edge[0]][edge[1]]['width'] = abs(G[edge[0]][edge[1]]['correlation'])
    # add a label to each node
    for node in G.nodes:
        G.nodes[node]['label'] = node
    # add a legend to the network for color
    G.graph['legend'] = [
        {
            'color': 'green',
            'label': 'Positive Correlation'
        },
        {
            'color': 'red',
            'label': 'Negative Correlation'
        }
    ]

    return G


@app.callback(
    dash.dependencies.Output('tab-content', 'children'),
    [dash.dependencies.Input('upload-data', 'contents'), dash.dependencies.Input('tabs', 'value')],
    [dash.dependencies.State('upload-data', 'filename')]
)
def render_tab_content(contents, tab, filename):
    """
    Update the output based on the uploaded data.

    Parameters:
    - contents (str): The contents of the uploaded file.
    - tab (str): The selected tab.
    - filename (str): The name of the uploaded file.

    Returns:
    - children (html.Table): The table displaying the correlations.
    """
    # log params
    #logging.info(f'contents: {contents}')
    logging.info(f'tab: {tab}')
    logging.info(f'filename: {filename}')

    if contents is not None:
        # Read the contents of the uploaded file to a Pandas DataFrame
        content_type, content_string = contents.split(',')
        decoded_contents = base64.b64decode(content_string)
        df = pd.read_table(io.StringIO(decoded_contents.decode('utf-8')))
        logging.info(f'df: {df}')
    
        # Calculate the correlations
        correlations = df.corr()

        if tab == 'table':
            # Display the correlations in a table
            return html.Table([
                html.Thead(
                    html.Tr([html.Th(col) for col in correlations.columns])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(correlations.iloc[i][col]) for col in correlations.columns
                    ]) for i in range(len(correlations.columns))
                ])
            ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

