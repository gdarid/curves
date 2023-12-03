"""
Lindenmayer System (L-system) with personal customizations

See also

    https://en.wikipedia.org/wiki/L-system

    https://onlinemathtools.com/l-system-generator
"""

import io
import math
import attrs as at
from bokeh.plotting import figure, show, output_file
from bokeh.io import export_png, export_svgs
from bokeh.io.export import get_screenshot_as_png
from loguru import logger
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import PIL.Image as pimage


@at.define
class Config:  # pylint: disable=too-few-public-methods
    """
    Configuration of the important active characters
    """
    reserved: str = ':; '  # reserved characters

    color: str = '.'
    move_lifted_pen: str = 'UVW'
    move_angle_init: str = '_'
    move: str = 'ABCDEFGHIJKLMNOPQRST'

    move_up_3d: str = '⇧'
    move_down_3d: str = '⇩'

    move_multi: str = at.field(init=False)
    move_all: str = at.field(init=False)

    delta_add: str = 'u'
    delta_sub: str = 'v'

    skipped: str = ''
    total_skipped: str = at.field(init=False)  # all skipped characters

    def __attrs_post_init__(self):
        self.move_multi = self.move.lower()
        self.move_all = self.color + self.move_lifted_pen + self.move_angle_init + self.move_multi + self.move
        self.total_skipped = ' ' + self.skipped


class Lsystc:
    """
    Classic L-System with few customizations
    """
    def __init__(self, config: Config, axiom: str, rules: list[tuple[str, str]], nbiter: int,
                 dev_ini: bool = True, verbose: bool = False) -> None:
        self.config = config
        self.axiom = axiom
        self.rules = rules
        self.nbiter = nbiter
        self.dev_ini = dev_ini
        self.verbose = verbose

        self.dev = ''
        self.turt = []

        self.dimension = 2

        if self.verbose:
            logger.info(f"Axiom: {self.axiom:.50} ; Rules : {self.rules} ; Nb iterations : {self.nbiter}")

        if self.dev_ini:
            self.develop()
            if self.verbose:
                logger.info(f"Axiom: {self.axiom:.50} ; Rules : {self.rules} ; Nb iterations : {self.nbiter} ; After")

    @staticmethod
    def dev_unit(source: str, rules: list[tuple[str, str]]) -> str:
        """
        Develop source with rules
        """
        result = source
        position = 0
        lreg = None

        while True:
            # The leftmost usable rule is applied
            newpos = None
            for lr, regle in enumerate(rules):
                lpos = result.find(regle[0], position)
                if lpos >= 0:
                    if newpos is None or lpos < newpos:
                        newpos = lpos
                        lreg = lr

            if newpos is None:
                break

            result = result[0:newpos] + result[newpos:].replace(rules[lreg][0], rules[lreg][1], 1)
            position = newpos + len(rules[lreg][1])

        return result

    @staticmethod
    def color_from_map(name: str, index: int) -> tuple[int, int, int]:
        """
        :param name: name of the discrete colormap (matplotlib source) to be used
        :param index: index of the color in the map
        :return: tuple (red, green, blue)
        """
        r, g, b = mpl.colormaps[name].colors[index]
        r, g, b = int(r * 255), int(g * 255), int(b * 255)

        return r, g, b

    @staticmethod
    def new_pos(ax: float, ay: float, astep: float, aangle: float) -> tuple[float, float]:
        """
        New position from (ax, ay) with the use of astep and aangle

        :param ax: 1st coordinate of starting point
        :param ay: 2nd coordinate of starting point
        :param astep: step size
        :param aangle: step angle
        """
        if aangle == 0.0:
            lx = ax + astep
            ly = ay
        elif aangle == 90.0:
            lx = ax
            ly = ay + astep
        elif aangle == 180.0:
            lx = ax - astep
            ly = ay
        elif aangle == 270.0:
            lx = ax
            ly = ay - astep
        else:
            lx = ax + astep * math.cos(math.radians(aangle))
            ly = ay + astep * math.sin(math.radians(aangle))

        return lx, ly

    def develop(self) -> None:
        """
        Develop self.axiom from the list of rules (self.rules) with nbiter iterations

        A rule is a couple (source, target) where source can be replaced by target

        Example of Koch :
            axiom = 'F'
            rules = [('F','F+F-F-F+F')]

        Example with 2 rules :
            axiom = 'A'
            rules = [('A','AB'),('B','A')]
        """
        result = self.axiom

        if self.rules:
            for _ in range(self.nbiter):
                result = self.dev_unit(result, self.rules)

        self.dev = result

    def turtle(self, step: float = 10.0, angle: float = 90.0, angleinit: float = 0.0, coeff: float = 1.1,
               angle2: float = 10.0, color_length: int = 3, color_map: str = "Set1",
               delta: float = 0.1) -> None:
        """
        Develop self.dev in [(lx, ly, lz, color),...] where lx, ly, lz are lists of positions
        The result goes to self.turt

        :param step: the turtle step size
        :param angle: angle of rotation (in degrees)     ( + - )
        :param angleinit: initial angle
        :param coeff: magnification or reduction factor for the step ( * / ) and factor for "lowered" characters
        :param angle2: 2nd usable angle ( < > )
        :param color_length: maximal number of colours
        :param color_map: color map to use (matplotlib name)
        :param delta: value to add to the step
        """
        res = []
        stock = []  # List of ("point", angle) kept for [] et ()

        lix = [0.0]
        liy = [0.0]
        liz = [0.0]

        tx = 0.0
        ty = 0.0
        tz = 0.0
        tstep = step
        tangle = angleinit
        tsens = 1
        color_index = 0
        tcouleur = self.color_from_map(color_map, color_index)

        for car in self.dev:

            if car in self.config.total_skipped:
                continue

            npos = False
            npospos = False
            nliste = False
            ncolor = False

            if car in self.config.move_all:
                if car in self.config.color:
                    ncolor = True
                else:
                    ltstep = tstep

                    if car in self.config.move_multi:
                        ltstep = tstep * coeff
                    elif car in self.config.move_angle_init:
                        tangle = angleinit

                    ltangle = tangle

                    tx, ty = self.new_pos(tx, ty, ltstep, ltangle)

                # npos true <-> new position with the pen down
                npos = car in self.config.move + self.config.move_multi + self.config.move_angle_init

                # nliste true <-> new list because of a change of color or a raised pen
                nliste = car in self.config.color + self.config.move_lifted_pen
            elif car in self.config.move_up_3d or car in self.config.move_down_3d:
                npos = True
                self.dimension = 3
                if car in self.config.move_up_3d:
                    tz += tstep
                else:
                    tz -= tstep
            elif car in '+':
                tangle = (tangle + angle * tsens) % 360.0
            elif car in '-':
                tangle = (tangle - angle * tsens) % 360.0
            elif car in '>':
                tangle = (tangle + angle2 * tsens) % 360.0
            elif car in '<':
                tangle = (tangle - angle2 * tsens) % 360.0
            elif car == '*':
                tstep *= coeff
            elif car == '/':
                tstep /= coeff
            elif car in self.config.delta_add:
                tstep += delta
            elif car in self.config.delta_sub:
                tstep -= delta
            elif car in '[(':
                stock.append((tx, ty, tz, tangle, tcouleur, tstep))
            elif car in '])':
                if stock:
                    tx, ty, tz, tangle, tcouleur, tstep = stock.pop()
                    nliste = True  # the pen is raised to go back to the stocked position
            elif car == '|':
                # Single "return" ("round-trip")
                npospos = True
            elif car == '!':
                # Change the sens of rotation
                tsens = tsens * -1
            else:
                continue

            # Take into account the read character
            # ------------------------------------
            if nliste:
                # New list because of new color or lifted pen
                if ncolor:
                    # Change of color
                    color_index = (color_index + 1) % color_length
                    tcouleur = self.color_from_map(color_map, color_index)

                if len(lix) > 1:
                    res.append((lix, liy, liz, tcouleur))
                lix = [tx]
                liy = [ty]
                liz = [tz]
            elif npos:
                # New position and no new list
                lix.append(tx)
                liy.append(ty)
                liz.append(tz)
            elif npospos:
                # 2 new positions for a "round-trip"
                tnx, tny = self.new_pos(tx, ty, tstep, tangle)

                lix.append(tnx)
                liy.append(tny)
                liz.append(tz)

                lix.append(tx)
                liy.append(ty)
                liz.append(tz)

        if len(lix) > 1:
            # Finally, append the last points
            res.append((lix, liy, liz, tcouleur))

        self.turt = res

    def render(self, show_type: str = 'matplot', image_destination: str = 'images_out/',
               save_files: bool = True, show_more: bool = False, show_3d: bool = False,
               return_type: str = ''):
        """
        Render self.turt using a specific show type

        :param show_type: 'matplot' or 'bokeh'
        :param image_destination: folder for images backup
        :param save_files: True to save files
        :param show_more: True to show with specific show_type
        :param show_3d: True to show 3D (implemented with plotly only)
        :param return_type: '', 'image' or 'figure'
        :return: None or an image if return_type is 'image' or a figure if return_type is 'figure'
        """
        if show_type == 'matplot':
            fig, ax = plt.subplots()

            for (lx, ly, _, coul) in self.turt:
                r, g, b = coul
                ax.plot(lx, ly, color=(r / 255., g / 255., b / 255., 1.0))

            ax.set_axis_off()
            ax.grid(visible=False)

            if show_more:
                plt.show()

            if save_files:
                fig.savefig(f'{image_destination}plot_{show_type}.png', bbox_inches='tight')
                fig.savefig(f'{image_destination}plot_{show_type}.svg', bbox_inches='tight')

            if return_type == 'image':
                fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
                fig.canvas.draw()

                # Return an image : PIL.Image
                return pimage.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())

            if return_type == 'figure':
                return fig

        elif show_type == 'bokeh':
            if save_files:
                output_file(f'{image_destination}lines_{show_type}.html')

            fig = figure(title="LSyst", x_axis_label='x', y_axis_label='y', width=800, height=800)

            for (lx, ly, _, coul) in self.turt:
                cr, cg, cb = coul
                fig.line(lx, ly, line_color=(cr, cg, cb))

            fig.xgrid.grid_line_color = None
            fig.ygrid.grid_line_color = None

            if show_more:
                _ = show(fig)

            if save_files:
                export_png(fig, filename=f'{image_destination}plot_{show_type}.png')

                fig.output_backend = "svg"
                export_svgs(fig, filename=f'{image_destination}plot_{show_type}.svg')

            if return_type == 'image':
                fig.toolbar_location = None
                fig.axis.visible = False
                fig.title = ""

                # Return an image : PIL.Image
                return get_screenshot_as_png(fig)

            if return_type == 'figure':
                return fig

        elif show_type == 'plotly':
            fig = go.Figure()

            axis_dict = {
                "showline": True,
                "showgrid": False,
                "showticklabels": True,
                "zeroline": False,
                "ticks": 'outside',
            }

            index = 0

            if self.dimension == 2 or not show_3d:
                for (lx, ly, lz, coul) in self.turt:
                    index += 1
                    cr, cg, cb = coul
                    fig.add_trace(go.Scatter(x=lx, y=ly, mode='lines',
                                             name=f"t{index}", line={"color": f'rgb({cr},{cg},{cb})', "width": 1}))

            else:
                # 3D
                for (lx, ly, lz, coul) in self.turt:
                    index += 1
                    cr, cg, cb = coul
                    fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines',
                                               name=f"t{index}", line={"color": f'rgb({cr},{cg},{cb})', "width": 1}))

            fig.update_layout(
                xaxis=axis_dict,
                yaxis=axis_dict,
                autosize=True,
                showlegend=False
            )

            if show_more:
                fig.show()

            if save_files:
                fig.write_image(f'{image_destination}plot_{show_type}.png')
                fig.write_image(f'{image_destination}plot_{show_type}.svg')

            if return_type == 'image':
                fig_bytes = fig.to_image(format="png")
                buf = io.BytesIO(fig_bytes)

                # Return an image : PIL.Image
                return pimage.open(buf)

            if return_type == 'figure':
                return fig

        else:
            raise ValueError("The given show_type is not correct")
