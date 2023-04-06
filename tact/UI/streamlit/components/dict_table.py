import streamlit as st

@st.experimental_singleton
class DictTable:
    def __init__(self, input_dict:dict, label:str):
        self.data = input_dict
        self.label = label
    
    def update_data(self):
        for key, value in self.data.items():
            value = st.session_state[value]
            self.data[key] = st.session_state[value]

    def replace_key(self, old_key, new_key):
        self.data[new_key] = self.data.pop(old_key)
    
    def render(self):
        combined_dict = {}
        with st.expander(label=self.label, expanded=True):
            for key, value in self.data.items():
                col1,col2 = st.columns([4,4])
                with col1:
                    st.text_input(key=key,value=key,label='Key')
                with col2:
                    st.text_input(key=value, value=value,label='Value')
        
        print_state = st.button(label='Print State')
        if print_state:
            st.write(self.data)
            st.write(st.session_state)
        
        update = st.button(label='Update')
        if update:
            self.update_data()
