from __future__ import print_function
import sys
import argparse
import textwrap

# import eagle2svg
from eagle2svg import eagle_parser
from eagle2svg.options import options


def render_main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Convert eagle file to svg.'
    )
    parser.add_argument('-l', '--layers', metavar='L', nargs='+',
                        help='eagle layers, e.g. board top layers : 1 20 17 18 21 25 19')
    parser.add_argument('-p', '--part', default=0,
                        help='drawing custom part, e.g. "packages.0" or ""')
    parser.add_argument('-f', '--filename', required=True,
                        help='a eagle filename to convert')
    parser.add_argument('-r', '--replace',
                        help='replace strings, e.g. ">NAME:STM32", ">VALUE:none"')
    parser.add_argument('-s', '--style', metavar='S', nargs='+',
                        help=textwrap.dedent('''\
                        svg style, e.g. "background:rgba(0,0,0,0.2)". 
                        All available style: 
                            background: [color] - css color
                            color-map: [{       - colors
                                "default": '#FF761A',
                                "gray": 'gray',
                                "navy": 'navy',
                                "green": 'green',
                                "olive": 'olive'
                            }]
                            font-family: [font-name]
                        '''))

    args = parser.parse_args()
    options.install(args)

    print(args)

    argv = sys.argv
    sys.exit()

    if len(argv) < 2:
        # print('eagle2svg %s' % eagle2svg.__version__)
        print('usage: eagle2svg eagle-file [sheet# [layer# [layer# ...]]]')
        print('- board top layers   : 1 20 17 18 21 25 19')
        print('- board bottom layers: 16 20 17 18 22 26 19')
        sys.exit()

    data = eagle_parser.Eagle(argv[1])
    if len(argv) > 2:
        sheet = argv[2]
    else:
        sheet = 0

    if len(argv) > 3:
        name = argv[3]
    else:
        name = ''

    if len(argv) > 4:
        layers = {}
        for i in range(4, len(argv) - 1):
            layers[int(argv[i])] = True
    else:
        layers = {
            91: True, 92: True, 93: True, 94: True,
            95: True, 96: True, 97: True, 104: True,
            1: True, 16: True, 17: True, 18: True,
            19: True, 20: True, 21: True, 22: True,
            25: True, 26: True, 29: True, 30: True
        }

    data.render(sheet, layers, {'>NAME': name})
