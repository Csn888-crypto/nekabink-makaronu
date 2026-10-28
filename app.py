import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import os

st.set_page_config(page_title="Nekabink makaronų | Scam Shield", page_icon="🛡️", layout="centered")

st.title("🛡️ Nekabink makaronų!")
st.write("Įkelkite įtartiną žinutę, nuorodą arba ekrano nuotrauką (SMS, skelbimą, e-parduotuvę), ir Gemini padės įvertinti riziką.")

# Paimamas raktas iš Streamlit Secrets arba įvedamas rankiniu būdu
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Įveskite savo Gemini API raktą:", type="password")

if not api_key:
    st.info("Norėdami pradėti, šoniniame meniu įveskite Gemini API raktą.")
    st.stop()

client = genai.Client(api_key=api_key)

# Įvesties pasirinkimas
tab1, tab2 = st.tabs(["📝 Tekstas ar nuoroda", "📸 Ekrano nuotrauka (Screenshot)"])

user_text = ""
uploaded_image = None

with tab1:
    user_text = st.text_area("Įklijuokite įtartinos žinutės tekstą arba svetainės adresą:", height=120)

with tab2:
    uploaded_file = st.file_uploader("Įkelkite paveikslėlį / screenshot:", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption="Įkelta peržiūrai", use_container_width=True)

if st.button("🔍 Tikrinti saugumą", type="primary"):
    if not user_text and not uploaded_image:
        st.warning("Pirmiausia įveskite tekstą arba įkelkite nuotrauką!")
    else:
        with st.spinner("Tikrinama... AI analizuoja galimus sukčiavimo požymius..."):
            system_prompt = (
                "Tu esi saugumo ekspertas asistentas 'Nekabink makaronų'. "
                "Tavo tikslas – įvertinti, ar vartotojo pateikta informacija (tekstas arba ekrano nuotrauka) yra sukčiavimas, "
                "apgaulė, netikra e-parduotuvė, manipuliacija ar saugus turinys.\n\n"
                "Atsakymo struktūra:\n"
                "1. VERDIKTAS (vienas iš šių: 🔴 Didelė rizika! / 🟡 Būkite atsargūs / 🟢 Saugu)\n"
                "2. KAS KELIA ĮTARIAMŲ (aiškūs, trumpi punktai apie domenų klaidas, dirbtinį skubėjimą, neįtikėtinas nuolaidas, neaiškius mokėjimus)\n"
                "3. KĄ DARYTI DABAR (1–2 konkretūs, paprasti patarimai, pvz., 'Nieko nespauskite', 'Blokuokite siuntėją').\n"
                "Toną išlaikyk ramų, aiškų, be sudėtingo žargono. Atsakyk lietuviškai."
            )
            
            contents = [system_prompt]
            if user_text:
                contents.append(f"Vartotojo pateiktas tekstas: {user_text}")
            if uploaded_image:
                contents.append(uploaded_image)

            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents
                )
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Įvyko klaida atliekant analizę: {e}")
