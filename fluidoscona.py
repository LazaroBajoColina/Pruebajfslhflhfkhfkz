import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import pandas as pd # Added for potential future data handling, though not strictly needed for these plots

# --- Constants ---
G_ACCEL = 9.81 # m/s^2 (standard gravity)
WATER_DENSITY = 1000 # kg/m^3

# --- Initialize the Dash app ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN], suppress_callback_exceptions=True)
server = app.server # For deployment

# --- App Layout ---
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Dashboard de Conceptos de Fluidos (Unidad 7)", className="text-center my-4"))),

    dbc.Tabs([
        # == Tab 1: Pressure ==
        dbc.Tab(label="Presión (P=F/A)", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Calculadora de Presión", className="card-title"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Fuerza (F) [N]:"),
                        dcc.Slider(id='pressure-force-slider', min=0, max=1000, step=10, value=120, marks={i: str(i) for i in range(0, 1001, 200)}),
                        html.Div(id='pressure-force-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                    ], width=6),
                    dbc.Col([
                        html.Label("Área (A) [m²]:"),
                        dcc.Slider(id='pressure-area-slider', min=0.01, max=1, step=0.01, value=0.04, marks={i/10: str(i/10) for i in range(0, 11)}),
                         html.Div(id='pressure-area-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                    ], width=6),
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='pressure-gauge-graph'), width=6),
                    dbc.Col([
                        html.H5("Resultado:"),
                        html.Div(id='pressure-output-text', className="lead")
                    ], width=6, align="center")
                ]),
                 html.P([
                     "La presión (P) es la fuerza (F) aplicada perpendicularmente sobre una superficie, dividida por el área (A) de esa superficie.",
                     html.Br(),"Fórmula: P = F / A. Unidad: Pascal (Pa) = N/m²."
                 ], className="mt-3 text-muted")
            ]), className="my-3")
        ]), # End Tab 1

        # == Tab 2: Hydraulic Press ==
        dbc.Tab(label="Prensa Hidráulica", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Simulador de Prensa Hidráulica (Principio de Pascal)", className="card-title"),
                 html.P("La presión aplicada en el émbolo menor (f/a) se transmite íntegramente al émbolo mayor (F/A). P₁ = P₂ => f/a = F/A.", className="text-muted"),
                dbc.Row([
                    # Inputs
                    dbc.Col([
                        html.H6("Émbolo Menor (Entrada)"),
                        html.Label("Fuerza Aplicada (f) [N]:"),
                        dcc.Slider(id='hydraulic-f-slider', min=10, max=500, step=10, value=125, marks={i: str(i) for i in range(0, 501, 100)}),
                        html.Div(id='hydraulic-f-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                        html.Br(),
                        html.Label("Diámetro Émbolo Menor (d) [cm]:"),
                        dcc.Slider(id='hydraulic-d-slider', min=1, max=10, step=0.5, value=2.1, marks={i: str(i) for i in range(1, 11)}),
                        html.Div(id='hydraulic-d-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                        html.Div(id='hydraulic-area-a-display', style={'textAlign': 'center', 'marginTop': '5px', 'color':'gray', 'fontSize':'small'}),

                    ], md=4),
                     # Inputs
                    dbc.Col([
                        html.H6("Émbolo Mayor (Salida)"),
                        html.Label("Diámetro Émbolo Mayor (D) [cm]:"),
                        dcc.Slider(id='hydraulic-D-slider', min=5, max=50, step=1, value=42, marks={i*5: str(i*5) for i in range(1, 11)}),
                        html.Div(id='hydraulic-D-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                        html.Div(id='hydraulic-area-A-display', style={'textAlign': 'center', 'marginTop': '5px', 'color':'gray', 'fontSize':'small'}),
                        html.Br(),
                         html.H5("Fuerza Resultante (F):"),
                        html.Div(id='hydraulic-output-F', className="lead fw-bold")

                    ], md=4),
                    # Visualization
                    dbc.Col([
                        html.H6("Visualización"),
                        dcc.Graph(id='hydraulic-press-graph')
                    ], md=4),
                ]),
                html.Hr(),
                dbc.Row([
                     dbc.Col([
                         html.H5("Presión en el sistema (P):"),
                         html.Div(id='hydraulic-pressure-display', className="lead")
                     ], width=6, align="center"),
                     dbc.Col([
                         html.H5("Ventaja Mecánica (F/f):"),
                         html.Div(id='hydraulic-advantage-display', className="lead")
                     ], width=6, align="center")
                ])
            ]), className="my-3")
        ]), # End Tab 2

        # == Tab 3: Archimedes' Principle ==
        dbc.Tab(label="Principio de Arquímedes", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Simulador de Empuje (Arquímedes)", className="card-title"),
                html.P("Todo cuerpo sumergido total o parcialmente en un fluido experimenta un empuje vertical hacia arriba igual al peso del fluido desalojado.", className="text-muted"),
                html.P("Empuje (E) = ρ_fluido * g * V_sumergido. Peso (W) = ρ_objeto * g * V_objeto.", className="text-muted"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Densidad del Objeto (ρ_objeto) [kg/m³]:"),
                        dcc.Slider(id='archimedes-rho-obj-slider', min=100, max=12000, step=100, value=700, marks={1000:'Agua', 2700:'Al', 7850:'Fe', 11300:'Pb'}),
                        html.Div(id='archimedes-rho-obj-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                        html.Br(),
                        html.Label("Volumen del Objeto (V_objeto) [m³]:"),
                        dcc.Slider(id='archimedes-vol-obj-slider', min=0.001, max=0.1, step=0.001, value=0.027, marks={i/100: str(i/100) for i in range(1, 11)}),
                        html.Div(id='archimedes-vol-obj-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                        html.Br(),
                        html.Label("Densidad del Fluido (ρ_fluido) [kg/m³]:"),
                        dcc.Slider(id='archimedes-rho-fluid-slider', min=500, max=1500, step=50, value=1000, marks={800:'Aceite', 1000:'Agua', 1025:'Agua Salada'}),
                        html.Div(id='archimedes-rho-fluid-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                    ], md=5),
                    dbc.Col([
                         dcc.Graph(id='archimedes-graph')
                    ], md=4),
                    dbc.Col([
                        html.H5("Resultados:"),
                        html.Div(id='archimedes-output-text', className="lead")
                    ], md=3, align="center"),
                ])
            ]), className="my-3")
        ]), # End Tab 3

        # == Tab 4: Hydrostatic Pressure ==
        dbc.Tab(label="Presión Hidrostática", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Calculadora de Presión Hidrostática", className="card-title"),
                 html.P("Es la presión ejercida por un fluido en reposo debido a su peso. Depende de la densidad del fluido (ρ), la gravedad (g) y la profundidad (h).", className="text-muted"),
                 html.P("Fórmula: Ph = ρ * g * h.", className="text-muted"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Profundidad (h) [m]:"),
                        dcc.Slider(id='hydrostatic-h-slider', min=0, max=100, step=1, value=10, marks={i*10: str(i*10) for i in range(0, 11)}),
                        html.Div(id='hydrostatic-h-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                        html.Br(),
                        html.Label("Densidad del Fluido (ρ) [kg/m³]:"),
                        dcc.Slider(id='hydrostatic-rho-slider', min=500, max=1500, step=50, value=1000, marks={800:'Aceite', 1000:'Agua', 1025:'Agua Salada'}),
                        html.Div(id='hydrostatic-rho-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                    ], md=4),
                    dbc.Col([
                        dcc.Graph(id='hydrostatic-pressure-graph')
                    ], md=5),
                     dbc.Col([
                        html.H5("Presión Hidrostática (Ph):"),
                        html.Div(id='hydrostatic-output-text', className="lead")
                    ], md=3, align="center"),
                ])
            ]), className="my-3")
        ]), # End Tab 4

         # == Tab 5: Continuity Equation ==
        dbc.Tab(label="Ecuación de Continuidad", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Simulador de Continuidad (A₁v₁ = A₂v₂)", className="card-title"),
                 html.P("Para un fluido incompresible en flujo estacionario, el caudal (G = A*v) es constante a lo largo de una tubería.", className="text-muted"),
                dbc.Row([
                     dbc.Col([
                        html.H6("Sección 1"),
                        html.Label("Diámetro Tubería 1 (D₁) [cm]:"),
                        dcc.Slider(id='continuity-D1-slider', min=1, max=10, step=0.5, value=8.0, marks={i: str(i) for i in range(1, 11)}),
                        html.Div(id='continuity-D1-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                        html.Div(id='continuity-A1-display', style={'textAlign': 'center', 'marginTop': '5px', 'color':'gray', 'fontSize':'small'}),
                        html.Br(),
                        html.Label("Velocidad Fluido 1 (v₁) [m/s]:"),
                        dcc.Slider(id='continuity-v1-slider', min=0.1, max=10, step=0.1, value=2.0, marks={i: str(i) for i in range(1, 11)}),
                        html.Div(id='continuity-v1-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                    ], md=4),
                     dbc.Col([
                        html.H6("Sección 2"),
                        html.Label("Diámetro Tubería 2 (D₂) [cm]:"),
                        dcc.Slider(id='continuity-D2-slider', min=1, max=10, step=0.5, value=2.0, marks={i: str(i) for i in range(1, 11)}),
                        html.Div(id='continuity-D2-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                        html.Div(id='continuity-A2-display', style={'textAlign': 'center', 'marginTop': '5px', 'color':'gray', 'fontSize':'small'}),
                        html.Br(),
                        html.H5("Velocidad Fluido 2 (v₂):"),
                        html.Div(id='continuity-output-v2', className="lead fw-bold")
                    ], md=4),
                    dbc.Col([
                        html.H6("Visualización Caudal"),
                        dcc.Graph(id='continuity-graph')
                    ], md=4),
                ]),
                 html.Hr(),
                 dbc.Row(dbc.Col(html.Div(id='continuity-gasto-display', className="lead text-center")))
            ]), className="my-3")
        ]), # End Tab 5

        # == Tab 6: Torricelli's Theorem ==
        dbc.Tab(label="Teorema de Torricelli", children=[
             dbc.Card(dbc.CardBody([
                html.H4("Simulador de Salida de Fluido (Torricelli)", className="card-title"),
                html.P("La velocidad de salida (v) de un fluido por un orificio es la misma que adquiriría un cuerpo cayendo libremente desde una altura (h) igual a la diferencia de nivel entre la superficie libre del fluido y el orificio.", className="text-muted"),
                html.P("Fórmula: v = √(2 * g * h).", className="text-muted"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Altura (h) [m]:"),
                        dcc.Slider(id='torricelli-h-slider', min=0.1, max=10, step=0.1, value=1.25, marks={i: str(i) for i in range(0, 11)}),
                        html.Div(id='torricelli-h-display', style={'textAlign': 'center', 'marginTop': '5px'}),
                         html.Br(),
                         html.Label("Gravedad (g) [m/s²]:"),
                         dcc.Input(id='torricelli-g-input', type='number', value=G_ACCEL, step=0.01, style={'width':'100px'}),

                    ], md=4),
                    dbc.Col([
                        dcc.Graph(id='torricelli-graph')
                    ], md=5),
                    dbc.Col([
                        html.H5("Velocidad de Salida (v):"),
                        html.Div(id='torricelli-output-v', className="lead fw-bold")
                    ], md=3, align="center"),
                ])
             ]), className="my-3")
        ]), # End Tab 6


    ]) # End Tabs
], fluid=True)

# --- Callbacks ---

# == Callback 1: Pressure ==
@app.callback(
    [Output('pressure-output-text', 'children'),
     Output('pressure-gauge-graph', 'figure'),
     Output('pressure-force-display', 'children'),
     Output('pressure-area-display', 'children')],
    [Input('pressure-force-slider', 'value'),
     Input('pressure-area-slider', 'value')]
)
def update_pressure(force, area):
    if area is None or area <= 0:
        pressure = 0
        pressure_text = "Área inválida (debe ser > 0)."
        area_val = 0
    else:
        pressure = force / area
        pressure_text = f"P = {force:.0f} N / {area:.3f} m² = {pressure:,.2f} Pa ({pressure/1000:,.2f} kPa)"
        area_val = area

    force_display = f"{force:.0f} N"
    area_display = f"{area_val:.3f} m²"

    # Create gauge figure
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = pressure,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Presión (Pa)"},
        gauge = {
            'axis': {'range': [0, max(50000, pressure * 1.2)]}, # Dynamic range
            'bar': {'color': "darkblue"},
            'steps' : [
                 {'range': [0, 10000], 'color': "lightgreen"},
                 {'range': [10000, 30000], 'color': "yellow"},
                 {'range': [30000, 50000], 'color': "orange"}],
            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 45000} # Example threshold
            }))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))


    return pressure_text, fig, force_display, area_display

# == Callback 2: Hydraulic Press ==
@app.callback(
    [Output('hydraulic-output-F', 'children'),
     Output('hydraulic-press-graph', 'figure'),
     Output('hydraulic-pressure-display', 'children'),
     Output('hydraulic-advantage-display', 'children'),
     Output('hydraulic-f-display', 'children'),
     Output('hydraulic-d-display', 'children'),
     Output('hydraulic-D-display', 'children'),
     Output('hydraulic-area-a-display', 'children'),
     Output('hydraulic-area-A-display', 'children')],
    [Input('hydraulic-f-slider', 'value'),
     Input('hydraulic-d-slider', 'value'),
     Input('hydraulic-D-slider', 'value')]
)
def update_hydraulic_press(f_in, d_cm, D_cm):
    # Convert cm to m for area calculation
    d_m = d_cm / 100.0
    D_m = D_cm / 100.0

    # Calculate areas
    area_a = np.pi * (d_m / 2)**2
    area_A = np.pi * (D_m / 2)**2

    if area_a is None or area_a <= 0:
        F_out = 0
        pressure = 0
        advantage = 0
        F_text = "Área 'a' inválida."
        pressure_text = "N/A"
        advantage_text = "N/A"
    else:
        # Calculate pressure (P = f/a)
        pressure = f_in / area_a
        # Calculate output force (F = P * A)
        F_out = pressure * area_A
        # Calculate mechanical advantage
        advantage = F_out / f_in if f_in > 0 else 0

        F_text = f"{F_out:,.2f} N"
        pressure_text = f"{pressure:,.2f} Pa ({pressure/1000:,.2f} kPa)"
        advantage_text = f"{advantage:.2f}"


    # Create bar chart figure comparing forces
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Entrada (f)', 'Salida (F)'],
        y=[f_in, F_out],
        marker_color=['rgb(55, 83, 109)', 'rgb(26, 118, 255)'],
        text=[f"{f_in:.1f} N", f"{F_out:,.1f} N"],
        textposition='auto'
    ))
    fig.update_layout(
        title='Comparación de Fuerzas',
        yaxis_title='Fuerza (N)',
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    f_display = f"{f_in:.1f} N"
    d_display = f"{d_cm:.1f} cm"
    D_display = f"{D_cm:.1f} cm"
    area_a_display = f"Área (a): {area_a:.4f} m²"
    area_A_display = f"Área (A): {area_A:.4f} m²"


    return F_text, fig, pressure_text, advantage_text, f_display, d_display, D_display, area_a_display, area_A_display

# == Callback 3: Archimedes' Principle ==
@app.callback(
    [Output('archimedes-output-text', 'children'),
     Output('archimedes-graph', 'figure'),
     Output('archimedes-rho-obj-display', 'children'),
     Output('archimedes-vol-obj-display', 'children'),
     Output('archimedes-rho-fluid-display', 'children')],
    [Input('archimedes-rho-obj-slider', 'value'),
     Input('archimedes-vol-obj-slider', 'value'),
     Input('archimedes-rho-fluid-slider', 'value')]
)
def update_archimedes(rho_obj, vol_obj, rho_fluid):
    # Calculate weight (W)
    weight = rho_obj * G_ACCEL * vol_obj

    # Determine maximum possible buoyancy (if fully submerged)
    max_buoyancy = rho_fluid * G_ACCEL * vol_obj

    situation = ""
    vol_submerged = 0
    buoyancy = 0
    percentage_submerged = 0

    if weight > max_buoyancy:
        # Object sinks
        situation = "El objeto se hunde."
        buoyancy = max_buoyancy # Buoyancy equals weight of displaced fluid when fully submerged
        vol_submerged = vol_obj
        percentage_submerged = 100
    elif weight == max_buoyancy:
        # Object is neutrally buoyant (suspended)
        situation = "El objeto está suspendido (flotabilidad neutra)."
        buoyancy = weight # Buoyancy equals weight
        vol_submerged = vol_obj
        percentage_submerged = 100
    else: # weight < max_buoyancy
        # Object floats
        situation = "El objeto flota."
        buoyancy = weight # Buoyancy equals weight
        # Calculate submerged volume: E = W => rho_fluid * g * V_sub = rho_obj * g * V_obj
        vol_submerged = (rho_obj / rho_fluid) * vol_obj
        percentage_submerged = (vol_submerged / vol_obj) * 100

    output_html = [
        html.P(f"Peso (W): {weight:,.2f} N"),
        html.P(f"Empuje (E): {buoyancy:,.2f} N"),
        html.P(f"Vol. Sumergido: {vol_submerged:.4f} m³ ({percentage_submerged:.1f}%)"),
        html.P(situation, className="fw-bold")
    ]

    # Create bar chart comparing W and E
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Peso (W)', 'Empuje (E)'],
        y=[weight, buoyancy],
        marker_color=['red', 'blue'],
        text=[f"{weight:.1f} N", f"{buoyancy:.1f} N"],
        textposition='auto'
    ))
    fig.update_layout(
        title='Comparación Peso vs. Empuje',
        yaxis_title='Fuerza (N)',
         height=300,
         margin=dict(l=20, r=20, t=50, b=20)
    )

    rho_obj_display = f"{rho_obj} kg/m³"
    vol_obj_display = f"{vol_obj:.4f} m³"
    rho_fluid_display = f"{rho_fluid} kg/m³"

    return output_html, fig, rho_obj_display, vol_obj_display, rho_fluid_display

# == Callback 4: Hydrostatic Pressure ==
@app.callback(
    [Output('hydrostatic-output-text', 'children'),
     Output('hydrostatic-pressure-graph', 'figure'),
     Output('hydrostatic-h-display', 'children'),
     Output('hydrostatic-rho-display', 'children')],
    [Input('hydrostatic-h-slider', 'value'),
     Input('hydrostatic-rho-slider', 'value')]
)
def update_hydrostatic_pressure(h, rho):
    # Calculate hydrostatic pressure
    pressure_h = rho * G_ACCEL * h

    pressure_text = f"Ph = {rho} kg/m³ * {G_ACCEL:.2f} m/s² * {h} m"
    pressure_text += f"<br><b>Ph = {pressure_h:,.2f} Pa ({pressure_h/1000:,.2f} kPa)</b>"

    # Create line graph showing pressure vs depth
    depths = np.linspace(0, h * 1.1, 50) # Depths up to 110% of selected h
    pressures = rho * G_ACCEL * depths

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=depths,
        y=pressures,
        mode='lines',
        name='Ph vs h',
        line=dict(color='royalblue', width=3)
    ))
    # Add point for the selected depth
    fig.add_trace(go.Scatter(
        x=[h],
        y=[pressure_h],
        mode='markers',
        marker=dict(color='red', size=10, symbol='x'),
        name=f'Ph en h={h}m'
    ))

    fig.update_layout(
        title='Presión Hidrostática vs. Profundidad',
        xaxis_title='Profundidad (h) [m]',
        yaxis_title='Presión (Ph) [Pa]',
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=True
    )

    h_display = f"{h} m"
    rho_display = f"{rho} kg/m³"

    return html.Div([html.P(line) for line in pressure_text.split('<br>')]), fig, h_display, rho_display


# == Callback 5: Continuity ==
@app.callback(
    [Output('continuity-output-v2', 'children'),
     Output('continuity-graph', 'figure'),
     Output('continuity-gasto-display', 'children'),
     Output('continuity-D1-display', 'children'),
     Output('continuity-A1-display', 'children'),
     Output('continuity-v1-display', 'children'),
     Output('continuity-D2-display', 'children'),
     Output('continuity-A2-display', 'children')],
    [Input('continuity-D1-slider', 'value'),
     Input('continuity-v1-slider', 'value'),
     Input('continuity-D2-slider', 'value')]
)
def update_continuity(D1_cm, v1, D2_cm):
    # Convert cm to m
    D1_m = D1_cm / 100.0
    D2_m = D2_cm / 100.0

    # Calculate areas
    A1 = np.pi * (D1_m / 2)**2
    A2 = np.pi * (D2_m / 2)**2

    if A2 is None or A2 <= 0:
        v2 = 0
        v2_text = "Diámetro D₂ inválido."
        gasto = 0
    else:
        # Calculate v2 using A1*v1 = A2*v2
        v2 = (A1 * v1) / A2
        v2_text = f"{v2:.2f} m/s"
        # Calculate flow rate (Gasto, G)
        gasto = A1 * v1 # Should be equal to A2 * v2

    # Create bar chart showing constant flow rate
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Sección 1 (A₁v₁)', 'Sección 2 (A₂v₂)'],
        y=[A1*v1, A2*v2], # These should be equal if calculation is correct
        marker_color=['mediumseagreen', 'lightcoral'],
        text=[f"{A1*v1:.4f} m³/s", f"{A2*v2:.4f} m³/s"],
        textposition='auto'
    ))
    fig.update_layout(
        title='Caudal (Gasto) Constante',
        yaxis_title='Caudal (G) [m³/s]',
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_range=[0, max(A1*v1, A2*v2)*1.2] # Ensure bars are visible
    )

    gasto_display = f"Caudal (Gasto, G): {gasto:.4f} m³/s"
    D1_display = f"{D1_cm:.1f} cm"
    A1_display = f"Área (A₁): {A1:.5f} m²"
    v1_display = f"{v1:.2f} m/s"
    D2_display = f"{D2_cm:.1f} cm"
    A2_display = f"Área (A₂): {A2:.5f} m²"

    return v2_text, fig, gasto_display, D1_display, A1_display, v1_display, D2_display, A2_display


# == Callback 6: Torricelli ==
@app.callback(
    [Output('torricelli-output-v', 'children'),
     Output('torricelli-graph', 'figure'),
     Output('torricelli-h-display', 'children')],
    [Input('torricelli-h-slider', 'value'),
     Input('torricelli-g-input', 'value')]
)
def update_torricelli(h, g):
    g_val = g if g is not None and g > 0 else G_ACCEL # Use default if input is invalid
    if h is None or h <= 0:
        v = 0
        v_text = "Altura h inválida."
    else:
        # Calculate exit velocity v = sqrt(2gh)
        v = np.sqrt(2 * g_val * h)
        v_text = f"{v:.2f} m/s"

    # Create plot of v vs h
    h_values = np.linspace(0.1, max(h * 1.1, 1), 50) # Heights up to 110% of selected h or at least 1m
    v_values = np.sqrt(2 * g_val * h_values)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=h_values,
        y=v_values,
        mode='lines',
        name='v vs h',
        line=dict(color='darkorange', width=3)
    ))
    # Add point for the selected height
    fig.add_trace(go.Scatter(
        x=[h],
        y=[v],
        mode='markers',
        marker=dict(color='purple', size=10, symbol='star'),
        name=f'v en h={h}m'
    ))
    fig.update_layout(
        title='Velocidad de Salida (Torricelli) vs. Altura',
        xaxis_title='Altura (h) [m]',
        yaxis_title='Velocidad (v) [m/s]',
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=True
    )

    h_display = f"{h:.2f} m"

    return v_text, fig, h_display


# --- Run the app ---
if __name__ == '__main__':
    app.run(debug=True)