import hydralit as hy
from example_balun_sizing import Balun
from example_space_mapping import SpaceMap

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

    app = hy.HydraApp(title="Simple Multi-Page App", allow_url_nav=True)

    @app.addapp(is_home=True)
    def my_home():
        hy.info("Welcome to the balun design demo.")

    # deactivated for now
    app.add_app("Space Mapping", app=SpaceMap())
    app.add_app("Balun", app=Balun())

    # Run the whole lot, we get navbar, state management and app isolation, all with this tiny amount of work.
    app.run()
