
from typing import List
from shiny import ui, render, App, reactive
from shiny.types import NavSetArg
from Utilitaire import *


# NAVBAR
def nav_controls(prefix: str) -> List[NavSetArg]:
    return [
        
        ui.nav_spacer(),
        ui.nav_menu(
            "Participants",
            ui.nav_control(ui.a("NGOUMLA DENILSON DUPLEX",)),
            "----",
            ui.nav_control(ui.a("KENGNE FOKAM IDRISS LEONEL",)),
            "----",
            ui.nav_control(ui.a("DONGMO KENFACK LESLY",)),
            "----",
            "NGANKEM FOGANG IVAN STYVE",
            align="right",
        ),
    ]


# FRONT END
app_ui = ui.page_fluid(
    ui.tags.style("""body {background-color : black;font-family: Times;} """),
        ui.div(
            {"style": "padding-bottom: 20px;"},
        ui.page_navbar(*nav_controls("page_navbar"),title="PLATEFORME DE DIAGNOSTIQUE MEDICAL",id="navbar_id",position="'fixed-bottom'")),
        ui.panel_absolute(ui.card(ui.layout_sidebar(
                ui.sidebar(ui.div(
                {"style": "margin-bottom :10px;"},
                 "Vos recherches apparaissent ici"),  
                 ui.div(
                {"style": "color : white;padding-left:5px;border-radius: 5px;background-color : black;"},
                            ui.output_text("result")) ,
                            id="sidebar_closed", open="desktop"),
                            ui.output_data_frame("table"),
                             border_color="black",border_radius=False)),left="10%",right="10%",),

        ui.panel_absolute(
            ui.div(
                {"style": "text-align :right;background-color : black;"},
            ui.panel_well(
                ui.input_action_button("btn", "Générer", class_="btn btn-dark"),
                ui.input_text_area("x2", "", placeholder="Parlez nous de vos symptomes ..."))),
            bottom="0",
            left="8%",
            right="8%",
            fixed=True,)
            
    )

# BACK END - SERVER
def server(input, output, session):
    
    @output
    @render.text
    def result():
        return f"{input.x2()}"
    
    @output   
    @render.data_frame
    @reactive.event(input.btn, ignore_none=False)
    def table():
        return Resultats(df, input.x2())
    
    
app = App(app_ui, server)
