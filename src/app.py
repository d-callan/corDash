import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import base64
import pandas as pd
from scipy.stats import pearsonr, spearmanr
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

