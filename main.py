import json
import os

import streamlit as st

# Data
races_list = [
    "Midlander", "Highlander", "Wildwood", "Duskwight", "Seeker", "Keeper",
    "Seawolf", "Hellsguard", "Plainsfolk", "Dunesfolk", "Raen", "Xaela", "Hellions", "Lost",
    "Rava", "Veena"
]

part_types = ["Face", "Body", "Eyes", "Brow/Lash"]
body_types_female = ["Vanilla", "Bibo+", "Gen 3"]
body_types_male = ["Vanilla", "TBSE", "Vanilla (with TBSE installed)"]
body_type_mapping = {
    "Vanilla (with TBSE installed)": "VanillaTBSE"
}
texture_types = ["Diffuse/Base", "Normal", "Mask"]


# Load JSON data
@st.cache_resource
def load_all_data():
    data = {}
    for gender in ['male', 'female']:
        data[gender] = {
            'body': json.load(open(f'json/{gender}_body.json')),
            'face': json.load(open(f'json/{gender}_face.json')),
            'eye': json.load(open(f'json/{gender}_eye.json')),
            'etc': json.load(open(f'json/{gender}_etc.json'))
        }
    return data


ALL_DATA = load_all_data()


@st.dialog("Help")
def show_dialog():
    st.write(
        "If there is an issue with the paths, or you need some help with them, you can ask me in my Discord Server: "
        "https://discord.gg/lunartear")


def get_texture_path(gender, race, part_type, body_type, texture_type, face_number=None):
    gender_lower = gender.lower()

    # Map texture types to JSON keys
    texture_map = {
        "Diffuse/Base": "base",
        "Normal": "norm",
        "Mask": "mask"
    }
    json_texture = texture_map.get(texture_type, texture_type.lower())

    # Map body type to JSON key
    json_body_type = body_type_mapping.get(body_type, body_type)

    if part_type == "Body":
        json_key = f"{gender}Body{json_texture.capitalize()}"
        return ALL_DATA[gender_lower]['body'][json_body_type][json_key][race]

    elif part_type == "Face":
        json_key = f"{gender}Face{json_texture.capitalize()}"
        return ALL_DATA[gender_lower]['face'][json_key][race][f"Face {face_number}"]

    elif part_type == "Eyes":
        json_key = f"{gender}Eye{json_texture.capitalize()}"
        return ALL_DATA[gender_lower]['eye'][json_key][race]

    elif part_type == "Brow/Lash":
        json_key = f"{gender}Etc{json_texture.capitalize()}"
        return ALL_DATA[gender_lower]['etc'][json_key][race][f"Face {face_number}"]

    return "Unsupported combination"


def get_valid_face_numbers(race, gender):
    gender_lower = gender.lower()
    face_data = ALL_DATA[gender_lower]['face'][f"{gender}FaceBase"][race]
    return list(range(1, len(face_data) + 1))


# Streamlit App
st.title("XIV Texture Path Generator")

# First row
col1, col2 = st.columns(2)
with col1:
    gender = st.selectbox("Gender", options=["Female", "Male"], index=0)

with col2:
    race_options = races_list
    race = st.selectbox("Race", options=race_options, index=0)

# Second row
col3, col4, col5 = st.columns(3)
with col3:
    part_type = st.selectbox("Part Type", options=part_types, index=0)

with col4:
    if part_type == "Body":
        body_types = body_types_female if gender == "Female" else body_types_male
        body_type = st.selectbox("Body Type", options=body_types, index=0)
        face_number = None
    else:
        body_type = None
        if part_type in ["Face", "Eyes", "Brow/Lash"]:
            valid_face_numbers = get_valid_face_numbers(race, gender)
            face_number = st.selectbox("Face Number", options=valid_face_numbers, index=0)
        else:
            face_number = None

with col5:
    # Handle display name mapping
    texture_display_names = {
        ("Face", "Diffuse/Base"): "Makeup/Diffuse",
        ("Body", "Diffuse/Base"): "Skin/Diffuse",
        ("Eyes", "Diffuse/Base"): "Eye Texture/Diffuse",
        ("Brow/Lash", "Mask"): "Dye Change/Mask"
    }

    # Determine the texture options and display names
    if part_type == "Brow/Lash":
        texture_options = [t for t in texture_types if t != "Diffuse/Base"]
    else:
        texture_options = texture_types

    # Create a display name mapping
    display_names = {
        t: texture_display_names.get((part_type, t), t) for t in texture_options
    }

    # Create a reversed mapping to get the selected value
    reversed_display_names = {v: k for k, v in display_names.items()}

    # Get the selected texture type from the dropdown
    selected_display_name = st.selectbox("Texture", options=list(display_names.values()), index=0)

    # Map the selected display name back to the original texture type
    texture_type = reversed_display_names.get(selected_display_name, "Diffuse/Base")

# Generate the path based on selections
generated_path = get_texture_path(gender, race, part_type, body_type, texture_type, face_number)

# Display the generated path
col1, col2, col3 = st.columns([8, 1, 1])
with col1:
    st.subheader("Path:")
with col3:
    if st.button("Help"):
        show_dialog()

st.code(generated_path, language="text")

# Extra notes expander
with st.expander("For Gen 3 body users"):
    st.markdown(
        "If the paths are not working, you may need to install the [Universal Compatibility Patch]("
        "https://www.xivmodarchive.com/modid/113626).")
with st.expander("Can't find your path?"):
    st.markdown(
        "A more complete list of paths can be found [here]("
        "https://docs.google.com/spreadsheets/d/1eccxWizhEQRdKkMMTB5721aMclo9KpEsfsKXT43iKqQ/).")