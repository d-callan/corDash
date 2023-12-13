import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import base64

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
                html.Label('Upload Data Table', style={'font-weight': 'bold', 'color': 'black', 'font-size': '16px'}),
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
                html.Label('Upload Second Data Table (optional)', style={'font-weight': 'bold', 'color': 'black', 'font-size': '16px'}),
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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

