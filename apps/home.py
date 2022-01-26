import hydralit as hy
from example_substrate import Substrate
from example_balun_sizing import Balun

if __name__ == "__main__":
    hy.set_page_config(
        page_title="Balun Sizer",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://passiveautodesign.netlify.app/",
            "Report a bug": "https://github.com/Patarimi/PassiveAutoDesign/issues",
        },
    )

    app = hy.HydraApp(title="Simple Multi-Page App")

    @app.addapp(is_home=True)
    def my_home():
        hy.info("Hello from app1")

    app.add_app("Substrate", app=Substrate())
    app.add_app("Balun", app=Balun())

    # Run the whole lot, we get navbar, state management and app isolation, all with this tiny amount of work.
    app.run()
