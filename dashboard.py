import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

df = pd.read_csv("spacex_launch_geo.csv")
max_payload = df["Payload Mass (kg)"].max()
min_payload = df["Payload Mass (kg)"].min()

app = dash.Dash(__name__)


app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Falcon 9 Launch Records Dashboard ",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        dcc.Dropdown(
            id="site-dropdown",
            options=[
                {"label": "All Sites", "value": "ALL"},
                {
                    "label": "Cape Canaveral Launch Complex 40 (CAFS LC-40)",
                    "value": "CCAFS LC-40",
                },
                {
                    "label": "Cape Canaveral Space Launch Complex 40 (CCAFS SLC-40)",
                    "value": "CCAFS SLC-40",
                },
                {
                    "label": "Kennedy Space Center Launch Complex 39A (KSC LC-39A)",
                    "value": "KSC LC-39A",
                },
                {
                    "label": "Vandenberg Air Force Base Space Launch Complex (VAFB SLC-4E)",
                    "value": "VAFB SLC-4E",
                },
            ],
            value="ALL",
            placeholder="Select a Launch Site:",
            searchable=True,
        ),
        html.Br(),
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={0: "0", 100: "100"},
            value=[min_payload, max_payload],
        ),
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    ft_df = df.groupby("Launch Site", as_index=False).agg({"class": "mean"})
    if entered_site == "ALL":
        return px.pie(
            ft_df,
            values="class",
            names="Launch Site",
            title="Launch Success Rate: All Sites",
        )
    # return the outcomes in pie chart for a selected site
    ft_df = df[df["Launch Site"] == entered_site]
    ft_df["outcome"] = ft_df["class"]
    ft_df["counts"] = 1
    return px.pie(
        ft_df,
        values="counts",
        names="outcome",
        title="Launch Success Rate: " + entered_site,
    )


@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_chart(entered_site, slider):
    ft_df = df[
        (slider[0] <= df["Payload Mass (kg)"]) & (df["Payload Mass (kg)"] <= slider[1])
    ]
    if entered_site == "ALL":
        return px.scatter(
            ft_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version",
            title="Launch Success Rate For All Sites",
        )

    ft_df = ft_df[ft_df["Launch Site"] == entered_site]
    ft_df["outcome"] = ft_df["class"].apply(
        lambda x: "Success" if (x == 1) else "Failure"
    )
    ft_df["counts"] = 1
    return px.scatter(
        ft_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version",
        title="Launch Success Rate For " + entered_site,
    )


if __name__ == "__main__":
    app.run_server()
