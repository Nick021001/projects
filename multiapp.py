import streamlit as st
from MAPP import MultiApp
from apps import index, home, General_Information # import your app modules here

app = MultiApp()

app.add_app('Home', home.app)
app.add_app('General Informations', General_Information.app)
app.add_app('Excel Creation', index.app)


#the main app

app.run()