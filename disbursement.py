import streamlit as st


def render_disbursement_tab():
    initial_assets = st.session_state.get("fire_objective", 0)
    st.header(f"How to manage your {initial_assets:,.0f}$ assets once FIREd")

    # TODO: indiquer le montant payé en taxe à chaque année
    # TODO: Page de simulation de decaissement -> Monte carlo? Calculer impots et rente
    # disbursment_df = monte_carlo_disbursment(initial_assets)
