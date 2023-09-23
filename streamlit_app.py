import lsystc as ls
import mpld3
import specific_values as sv
import streamlit as st
import streamlit.components.v1 as components
from streamlit.errors import StreamlitAPIException
import yaml

st.set_page_config(page_title="Curves with L-systems", page_icon="🖼️", layout="wide")


@st.cache_data
def load_result(axiom, mult_axiom, rules, rotation_angle, starting_angle, skipped, nb_iterations):
    try:
        rules = rules.strip("; ")
        rules_list = []

        if rules:
            for item in rules.split(";"):
                if ':' in item:
                    splits = item.split(":")
                    if len(splits) == 2 and splits[0].strip():
                        left = splits[0].strip()
                        right = splits[1].strip()
                        rules_list.append((left, right))
                    else:
                        raise ValueError(f"Every rule must be correctly written ( {item} )")
                else:
                    raise ValueError(f"Every non empty rule must include a column character ( {item} ) ")

        rls = ls.Lsystc(axiom * mult_axiom, rules_list, nbiter=nb_iterations)
        rls.turtle(step=sv.step, angle=rotation_angle, angleinit=starting_angle, coeff=sv.coeff, skipped=skipped,
                   color_length=sv.color_length, color_map=sv.color_map)

        result = rls.render(sv.renderer, save_files=sv.save_files, show_more=sv.show_more, show_3d=sv.show_3d,
                            return_type=sv.return_type)
    except ValueError as ex:
        st.warning(f"Please verify your parameters - {ex}")
        st.stop()
    except Exception as ex:
        st.warning(f"Please verify your parameters")
        print(f"Something went wrong : {ex}")
        st.stop()
    else:
        return result


def write_specific(content):
    try:
        st.write(content)
    except StreamlitAPIException as exc:
        # Currently : streamlit.errors.StreamlitAPIException: `_repr_html_()` is not a valid Streamlit command.
        if sv.verbose:
            print(exc)


def on_change_selection():
    current_selection = st.session_state.my_selection
    axiom, mult_axiom, rules, rotation_angle, starting_angle, nb_iter, skipped = examples_data[current_selection]
    st.session_state.my_axiom = axiom
    st.session_state.my_mult_axiom = mult_axiom
    st.session_state.my_rules = rules
    st.session_state.my_rotation_angle = rotation_angle
    st.session_state.my_starting_angle = starting_angle
    st.session_state.my_nb_iter = nb_iter
    st.session_state.my_skipped = skipped
    sv.redraw_auto = True


with open("curves_parameters.yaml", 'r') as f:
    curves_parameters = yaml.safe_load(f)

examples_default = 0
examples_names = []
examples_data = {}
for c_name, c_params in curves_parameters.items():
    examples_names.append(c_name)
    c_axiom = c_params.get('axiom', '')
    c_axiom_multiplier = c_params.get('axiom_multiplier', 1)
    c_rules = c_params.get('rules', '')
    c_rotation_angle = c_params.get('rotation_angle', 90.0)
    c_starting_angle = c_params.get('starting_angle', 0)
    c_nb_iter = c_params.get('nb_iter', 1)
    c_skipped = c_params.get('skipped', '')
    examples_data[c_name] = (c_axiom, c_axiom_multiplier, c_rules,
                             c_rotation_angle, c_starting_angle, c_nb_iter, c_skipped)


examples_default_name = examples_names[examples_default]
def_axiom, def_mult_axiom, def_rules, def_rotation_angle, def_starting_angle, def_nb_iter, def_skipped = examples_data[examples_default_name]

with st.sidebar:
    md_intro = """
    You have the flexibility to select a starting example and to change the parameters :sunglasses:
    """

    st.markdown(md_intro)

    input_selection = st.selectbox('Starting example', examples_names,
                                   index=examples_default, on_change=on_change_selection, key="my_selection")

    input_axiom = st.text_input('Starting axiom', def_axiom, key="my_axiom")
    input_mult_axiom = st.number_input('Multiplier for axiom', value=def_mult_axiom, min_value=1, key="my_mult_axiom")

    input_rules = st.text_input('Rules', def_rules, help="Example for 2 rules ->   A:  ABC ;  B:   CAB ; ", key="my_rules")
    input_rotation_angle = st.number_input('Angle of rotation',
                                           value=def_rotation_angle, min_value=1.0, max_value=360.0, step=1.0,
                                           format='%f', key="my_rotation_angle")
    input_starting_angle = st.number_input('Starting angle',
                                           value=def_starting_angle, min_value=0, max_value=360,
                                           format='%d', key="my_starting_angle")

    input_skipped = st.text_input('Skipped characters', def_skipped, key="my_skipped")

    input_nb_iter = st.number_input('Number of iterations',
                                    value=def_nb_iter, min_value=1, max_value=15, format='%d', key="my_nb_iter")

st.markdown("# Curves with L-systems")

st.markdown("""**Click on "Draw" to display the curve**""")

if st.button('Draw') or sv.redraw_auto or 'start' not in st.session_state:
    sv.redraw_auto = False
    st.session_state['start'] = True
    res = load_result(input_axiom, input_mult_axiom, input_rules, input_rotation_angle, input_starting_angle,
                      input_skipped, input_nb_iter)

    if sv.return_type == 'image':
        write_specific(st.image(res, caption='Generated image'))
    else:
        if sv.renderer == 'matplot':
            # Pyplot figure
            # write_specific(st.pyplot(res))
            fig_html = mpld3.fig_to_html(res)
            components.html(fig_html, height=600)
        elif sv.renderer == 'bokeh':
            st.bokeh_chart(res, use_container_width=True)
        elif sv.renderer == 'plotly':
            st.plotly_chart(res, use_container_width=True)

st.markdown("---")
st.markdown("More infos and :star: at [github.com/gdarid/curves](https://github.com/gdarid/curves)")
