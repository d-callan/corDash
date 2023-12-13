import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import base64

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
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
    html.Div(id='output-data')
])

# Callback to display the contents of the uploaded file
@app.callback(Output('output-data', 'children'),
              [Input('upload-data', 'contents')])
def update_output(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
        return html.Div([
            html.H5('Uploaded File Content:'),
            html.Pre(decoded)
        ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

