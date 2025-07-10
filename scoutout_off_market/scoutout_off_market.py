import reflex as rx
from rxconfig import config
import backend.check_validity as check_validity

class State(rx.State):
    
    address: str = ""

    def set_address(self, user_address: str):
        self.address = user_address

    def get_address(self):

        if check_validity.check_home_for_sale(self.address) is True:
            return rx.redirect("/value")
        else:
            return rx.redirect("/not-found")


def index() -> rx.Component:
    return rx.container(

        rx.color_mode.button(position="bottom-right"),

        rx.vstack(

            rx.heading(
                "Find Your Property Insights", 
                size="9", 
            ),

            rx.text(
                "Enter your address to get started with our predictive analysis tool.",
                size="5",
            ),


            rx.hstack(

                rx.input(
                    placeholder="Enter your property address here...",
                    default_value="",
                    on_blur=State.set_address,
                    border_width="1px",
                    padding="0.5em",
                    box_shadow="rgba(0, 0, 0, 0.15) 0px 2px 8px",
                    width="350px",
                ),
                
                rx.button(
                    "Find price!",
                    on_click=State.get_address,
                    background_color=rx.color("accent", 10),
                    box_shadow="rgba(0, 0, 0, 0.15) 0px 2px 8px",
                ),

                spacing="3",

            ),

            spacing="5",
            justify="center",
            align_items="center",
            min_height="85vh",
        ),
    )

def property_values():
    return rx.container(

        rx.color_mode.button(position="bottom-right"),

            rx.vstack(

                rx.heading(

                    "$1,003,234.45",
                    size="9"

                ),

                rx.text(

                    f"{State.address}",
                    size="5"

                ),

                 rx.button(

                    "Back to home", 
                    on_click=rx.redirect("/"),
                    color_scheme="grass"

                ),

                spacing="5",
                justify="center",
                align_items="center",
                min_height="85vh"

            )

        )
        
def not_found():
    return rx.container(

        rx.color_mode.button(position="bottom-right"),

        rx.vstack(

            rx.heading(
                
                "Sorry, we could not find that property",
                align="center",
                size = "9"
                    
            ),


            rx.button(

                "Back to home",
                on_click=rx.redirect("/"),
                border="2px",
                color_scheme="grass"

            ),

            spacing="5",
            align="center",
            justify="center",
            min_height="85vh"

        )

    )

app = rx.App()

app.add_page(index)

app.add_page(property_values, route="/value")
app.add_page(not_found, route="/not-found")