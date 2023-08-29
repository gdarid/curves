"""
Lindenmayer System (L-system) with personal customizations

See also

    https://en.wikipedia.org/wiki/L-system

    https://onlinemathtools.com/l-system-generator
"""

import math
import matplotlib as mpl
import matplotlib.pyplot as plt


class Lsystc:
    """
    Classic L-System with few customizations
    """
    def __init__(self, axiom, rules, nbiter, dev_ini=True):
        self.axiom = axiom
        self.rules = rules
        self.nbiter = nbiter
        self.dev_ini = dev_ini

        self.dev = ''
        self.turt = []

        self.reserved = ':; '  # reserved characters
        self.default_skipped = ' '

        self.char_color = '.'
        self.char_up_move = 'UVW'
        self.char_move_angle_init = '_'
        self.char_move = 'ABCDEFGHIJLMNOP'
        self.char_move_multi = self.char_move.lower()
        self.char_move_all = self.char_color + self.char_up_move + self.char_move_angle_init + self.char_move_multi + self.char_move

        if dev_ini:
            self.develop()

    @staticmethod
    def dev_unit(source, regles):
        """
        Develop source with regles
        """
        result = source
        position = 0
        lreg = None

        while True:
            # The leftmost usable rule is applied
            newpos = None
            for lr, regle in enumerate(regles):
                lpos = result.find(regle[0], position)
                if lpos >= 0:
                    if newpos is None or lpos < newpos:
                        newpos = lpos
                        lreg = lr

            if newpos is None:
                break
            else:
                result = result[0:newpos] + result[newpos:].replace(regles[lreg][0], regles[lreg][1], 1)
                position = newpos + len(regles[lreg][1])

        return result

    @staticmethod
    def ls_simplifie(chaine, skipped):
        """
        Returns a simplified string where all "skipped" characters are removed
        """
        return [car for car in chaine if car not in skipped]

    @staticmethod
    def color_from_map(name, index):
        """
        :param name: name of the discrete colormap (matplotlib source) to be used
        :param index: index of the color in the map
        :return: tuple (red, green, blue)
        """
        r, g, b = mpl.colormaps[name].colors[index]
        r, g, b = int(r * 255), int(g * 255), int(b * 255)

        return r, g, b

    @staticmethod
    def new_pos(ax, ay, astep, aangle):
        """
        New position from (ax, ay) with the use of astep and aangle
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

    def develop(self):
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
            for li in range(self.nbiter):
                result = self.dev_unit(result, self.rules)

        self.dev = result

    def turtle(self, step=10.0, angle=90.0, angleinit=0.0, coeff=1.1,
               angle2=10.0, skipped='', color_length=3, color_map="Set1"):
        """
        Develop self.dev in [(lx, ly, color),...] where lx and ly are lists of positions
        The result goes to self.turt

        step : the turtle size
        angle : angle of rotation (in degrees)     ( + - )
        angleinit : initial angle
        coeff : magnification or reduction factor for the step ( * / ) and factor for "lowered" characters
        angle2 : 2nd usable angle ( < > )
        skipped : skipped characters
        color_length : maximal number of colours
        color_map : color map to use (matplotlib name)

        """
        if skipped:
            skipped = skipped + self.default_skipped
        else:
            skipped = self.default_skipped

        # print('Simplified string : ', self.ls_simplifie(self.dev, skipped))

        res = []
        stock = []  # List of (point, angle) kept for [] et ()

        lix = [0.0]
        liy = [0.0]
        tx = 0.0
        ty = 0.0
        tstep = step
        tangle = angleinit
        tsens = 1
        ncolor = False
        color_index = 0
        tcouleur = self.color_from_map(color_map, color_index)

        for car in self.dev:

            if car in skipped:
                continue

            npos = False
            npospos = False
            nliste = False
            ncolor = False

            if car in self.char_move_all:
                if car in self.char_color:
                    ncolor = True
                else:
                    ltstep = tstep

                    if car in self.char_move_multi:
                        ltstep = tstep * coeff
                    elif car in self.char_move_angle_init:
                        tangle = angleinit

                    ltangle = tangle

                    tx, ty = self.new_pos(tx, ty, ltstep, ltangle)

                # npos true <-> new position with the pen down
                npos = (car in self.char_move + self.char_move_multi + self.char_move_angle_init)

                # nliste true <-> new list because of a change of color or a raised pen
                nliste = (car in self.char_color + self.char_up_move)
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
            elif car in '[(':
                stock.append((tx, ty, tangle))
            elif car in '])':
                if stock:
                    tx, ty, tangle = stock.pop()
                    nliste = True  # the pen is raised to go back to the stocked position
            elif car == '|':
                # Single "return" ("round-trip")
                npospos = True
            elif car == '!':
                # Change the sens of rotation
                tsens = tsens * -1

            # Take into account the read character
            # ------------------------------------
            if nliste:
                # New list because of new color or lifted pen
                if ncolor:
                    # Change of color
                    color_index = (color_index + 1) % color_length
                    tcouleur = self.color_from_map(color_map, color_index)

                if len(lix) > 1:
                    res.append((lix, liy, tcouleur))
                lix = [tx]
                liy = [ty]
            elif npos:
                # New position and no new list
                lix.append(tx)
                liy.append(ty)
            elif npospos:
                # 2 new positions for a "round-trip"
                tnx, tny = self.new_pos(tx, ty, tstep, tangle)

                lix.append(tnx)
                liy.append(tny)

                lix.append(tx)
                liy.append(ty)

        if len(lix) > 1:
            if ncolor:
                # Change of color
                color_index = (color_index + 1) % color_length
                tcouleur = self.color_from_map(color_map, color_index)
            res.append((lix, liy, tcouleur))

        self.turt = res

    def render(self, showtype='matplot', image_destination='images_out/', save_files=True, show_more=False,
               return_type=''):
        """
        Render self.turt using a specific show type

        :param showtype: 'matplot' or 'bokeh'
        :param image_destination: folder for images backup
        :param save_files: True to save files
        :param show_more: True to show with specific showtype
        :param return_type: '', 'image' or 'figure'
        :return: None or an image if return_type is 'image' or a figure if return_type is 'figure'
        """
        if showtype == 'matplot':
            fig, ax = plt.subplots()

            for (lx, ly, coul) in self.turt:
                r, g, b = coul
                ax.plot(lx, ly, color=(r / 255., g / 255., b / 255., 1.0))

            if show_more:
                plt.show()

            if save_files:
                ax.set_axis_off()
                ax.grid(visible=False)
                fig.savefig(f'{image_destination}plot_{showtype}.png', bbox_inches='tight')
                fig.savefig(f'{image_destination}plot_{showtype}.svg', bbox_inches='tight')

            if return_type == 'image':
                from PIL import Image

                ax.set_axis_off()
                ax.grid(visible=False)
                fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
                fig.canvas.draw()

                # Return an image : PIL.Image.Image
                return Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
            elif return_type == 'figure':
                ax.set_axis_off()
                ax.grid(visible=False)

                return fig

        elif showtype == 'bokeh':
            from bokeh.plotting import figure, show, output_file
            from bokeh.io import export_png, export_svgs

            if save_files:
                output_file(f'{image_destination}lines_{showtype}.html')

            fig = figure(title="LSyst", x_axis_label='x', y_axis_label='y', width=800, height=800)

            for (lx, ly, coul) in self.turt:
                cr, cg, cb = coul
                fig.line(lx, ly, line_color=(cr, cg, cb))

            fig.xgrid.grid_line_color = None
            fig.ygrid.grid_line_color = None

            if show_more:
                _ = show(fig)

            if save_files:
                export_png(fig, filename=f'{image_destination}plot_{showtype}.png')

                fig.output_backend = "svg"
                export_svgs(fig, filename=f'{image_destination}plot_{showtype}.svg')

            if return_type == 'image':
                from bokeh.io.export import get_screenshot_as_png

                fig.toolbar_location = None
                fig.axis.visible = False
                fig.title = ""

                # Return an image : PIL.Image.Image
                return get_screenshot_as_png(fig)
            elif return_type == 'figure':
                return fig

        else:
            raise ValueError("The given showtype is not correct")
