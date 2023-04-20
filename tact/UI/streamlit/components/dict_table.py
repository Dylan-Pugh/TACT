import streamlit as st
import uuid


class DictTable:
    def __init__(
        self,
        input_dict: dict,
        top_level_dict: str,
        label: str,
        key_label: str,
        value_label: str,
    ):
        self.data = input_dict
        self.top_level_dict = top_level_dict
        self.label = label
        self.key_label = key_label
        self.value_label = value_label

    def update_data(self, key, value):
        if self.top_level_dict in st.session_state:
            st.session_state[self.top_level_dict][key] = value

        if key in self.data.keys():
            self.data[key] = value

    def replace_key(self, old_key, new_key):
        self.data[new_key] = self.data.pop(old_key)

    def render(self):
        with st.container():
            st.header(self.label)

            for key, value in self.data.items():
                col1, col2 = st.columns([4, 4])
                with col1:
                    st.text_input(
                        key=uuid.uuid4(),
                        value=key,
                        label=self.key_label,
                    )
                with col2:
                    updated_value = st.text_input(
                        key=uuid.uuid4(),
                        value=value,
                        label=self.value_label,
                    )
                    if updated_value:
                        self.update_data(key, updated_value)
