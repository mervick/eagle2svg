import xmltodict
import copy
import os
from datetime import datetime

from eagle2svg import svg_common, eagle_element, eagle_types


class EagleFileBase(object):
    def __init__(self, data):
        self.libraries = {}

        if 'libraries' in data:
            for library_data in eagle_types.named_array(data['libraries']):
                library = eagle_element.Library(library_data)
                if library.name in self.libraries:
                    self.libraries[library.name].append(library)
                else:
                    self.libraries[library.name] = library


class Library(object):
    def __init__(self, data):
        self.library = eagle_element.Library(data)

    def render(self, sheet=0, layers={}, replace={}):
        replace2 = copy.deepcopy(replace)
        view_box = svg_common.ViewBox()

        args = []
        if sheet != 0:
            args = sheet.split(".")

        if self.library:
            if self.library.symbols and sheet == 0 or args[0] == 'symbols':
                idx = 0
                for name, symbol in self.library.symbols.items():
                    if sheet == 0 or len(args) == 1 or args[1] == name or args[1] == str(idx):
                        symbol.render(replace=replace2, mirror_text=True, view_box=view_box)
                        if sheet != 0 or len(args) > 1:
                            break
                    idx = idx + 1

            if self.library.packages and sheet == 0 or args[0] == 'packages':
                idx = 0
                for name, package in self.library.packages.items():
                    if sheet == 0 or len(args) == 1 or args[1] == name or args[1] == str(idx):
                        package.render(replace=replace2, mirror_text=True, view_box=view_box)
                        if sheet != 0 or len(args) > 1:
                            break
                    idx = idx + 1

            # if self.library.devicesets and sheet == 0 or args[0] == 'devicesets':
            #     idx = 0
            #     for name, deviceset in self.library.devicesets.items():
            #         if sheet == 0 or len(args) < 2 or args[1] == name or args[1] == idx:
            #             if sheet == 0 or len(args) < 3 or args[2] == 'gates':
            #                 idy = 0
            #                 for gate_name, gate in deviceset.gates.items():
            #                     if sheet == 0 or len(args) < 4 or args[3] == gate_name or args[3] == idy:
            #                         gate.render(replace=replace2, mirror_text=True, view_box=view_box)
            #                         if len(args) > 2:
            #                             break
            #                     idy = idy + 1
            #             if sheet == 0 or len(args) < 3 or args[2] == 'devices':
            #                 idy = 0
            #                 for device_name, device in deviceset.devices.items():
            #                     if sheet == 0 or len(args) < 4 or args[3] == device_name or args[3] == idy:
            #                         device.render(replace=replace2, mirror_text=True, view_box=view_box)
            #                         if len(args) > 2:
            #                             break
            #                     idy = idy + 1
            #         idx = idx + 1

        view_box.x1 = view_box.x1 - 1
        view_box.y1 = view_box.y1 - 1
        view_box.x2 = view_box.x2 + 1
        view_box.y2 = view_box.y2 + 1

        print('<?xml version="1.0"?>')
        print('<svg version="1.1" xmlns="http://www.w3.org/2000/svg"'
              + ' viewBox="%f %f %f %f" width="%fmm" height="%fmm">'
              % (view_box.x1, view_box.y1,
                 view_box.x2 - view_box.x1, view_box.y2 - view_box.y1,
                 view_box.x2 - view_box.x1, view_box.y2 - view_box.y1))
        print('<style type="text/css">:root{background-color: black;}'
              + ' *{font-family:Consolas, \'Courier New\', '
              + 'Courier, Monaco, monospace;}</style>')
        print('<rect x="%f" y="%f" width="%f" height="%f" fill="black"/>'
              % (view_box.x1, view_box.y1,
                 view_box.x2 - view_box.x1, view_box.y2 - view_box.y1))

        for layer in layers:
            if layer in view_box.layers:
                for line in view_box.layers[layer]:
                    print(line)

        print('</svg>')


class Board(EagleFileBase):
    def __init__(self, data):
        super(Board, self).__init__(data)
        self.plain = eagle_element.Plain(data['plain'])

        self.elements = {}
        for element_data in eagle_types.named_array(data['elements']):
            element = eagle_element.Element(element_data)
            self.elements[element.name] = element

        self.signals = {}
        for signal_data in eagle_types.named_array(data['signals']):
            signal = eagle_element.Signal(signal_data)
            self.signals[signal.name] = signal

    def render(self, sheet=0, layers={}, replace={}):
        replace2 = copy.deepcopy(replace)
        view_box = svg_common.ViewBox()

        self.plain.render(replace=replace2, mirror_text=True, view_box=view_box)

        for key, element in self.elements.items():
            element.render(libraries=self.libraries, replace=replace2, mirror_text=True, view_box=view_box)

        for key, signal in self.signals.items():
            signal.render(view_box=view_box)

        view_box.x1 = view_box.x1 - 1
        view_box.y1 = view_box.y1 - 1
        view_box.x2 = view_box.x2 + 1
        view_box.y2 = view_box.y2 + 1

        print('<?xml version="1.0"?>')
        print('<svg version="1.1" xmlns="http://www.w3.org/2000/svg"'
              + ' viewBox="%f %f %f %f" width="%fmm" height="%fmm">'
              % (view_box.x1, view_box.y1,
                 view_box.x2 - view_box.x1, view_box.y2 - view_box.y1,
                 view_box.x2 - view_box.x1, view_box.y2 - view_box.y1))
        print('<style type="text/css">:root{background-color: black;}'
              + ' *{font-family:Consolas, \'Courier New\', '
              + 'Courier, Monaco, monospace;}</style>')
        print('<rect x="%f" y="%f" width="%f" height="%f" fill="black"/>'
              % (view_box.x1, view_box.y1,
                 view_box.x2 - view_box.x1, view_box.y2 - view_box.y1))

        for layer in layers:
            if layer in view_box.layers:
                for line in view_box.layers[layer]:
                    print(line)

        print('</svg>')


class Schematic(EagleFileBase):
    def __init__(self, data):
        super(Schematic, self).__init__(data)

        self.sheets = []
        for sheet_data in eagle_types.named_array(data['sheets']):
            self.sheets.append(eagle_element.Sheet(sheet_data))

        self.parts = {}
        for part_data in eagle_types.named_array(data['parts']):
            part = eagle_element.Part(part_data)
            self.parts[part.name] = part

    def render(self, sheet=0, layers={}, replace={}):
        replace2 = copy.deepcopy(replace)
        replace2['>SHEET'] = str(sheet + 1) + '/' + str(len(self.sheets))
        view_box = svg_common.ViewBox()
        self.sheets[sheet].render(libraries=self.libraries, parts=self.parts, replace=replace2, view_box=view_box)

        view_box.x1 = view_box.x1 - 1
        view_box.y1 = view_box.y1 - 1
        view_box.x2 = view_box.x2 + 1
        view_box.y2 = view_box.y2 + 1

        print('<?xml version="1.0"?>')
        print('<svg version="1.1" xmlns="http://www.w3.org/2000/svg"'
              + ' viewBox="%f %f %f %f" width="%fmm" height="%fmm">'
              % (view_box.x1, view_box.y1,
                 view_box.x2 - view_box.x1, view_box.y2 - view_box.y1,
                 view_box.x2 - view_box.x1, view_box.y2 - view_box.y1))
        print('<style type="text/css">:root{background-color: white;}'
              + ' *{font-family:Consolas, \'Courier New\','
              + ' Courier, Monaco, monospace;}</style>')
        print('<rect x="%f" y="%f" width="%f" height="%f" fill="white"/>'
              % (view_box.x1, view_box.y1,
                 view_box.x2 - view_box.x1, view_box.y2 - view_box.y1))
        for layer in layers:
            if layer in view_box.layers:
                for line in view_box.layers[layer]:
                    print(line)
        print('</svg>')


class Eagle(object):
    def __init__(self, filename):
        f = open(filename)
        data = xmltodict.parse(f.read())

        self.layers = data['eagle']['drawing']['layers']

        if 'library' in data['eagle']['drawing']:
            self.data = Library(data['eagle']['drawing']['library'])

        elif 'schematic' in data['eagle']['drawing']:
            self.data = Schematic(data['eagle']['drawing']['schematic'])

        elif 'board' in data['eagle']['drawing']:
            self.data = Board(data['eagle']['drawing']['board'])

        self.replace = {}
        self.replace['>DRAWING_NAME'], ext = os.path.splitext(
            os.path.basename(filename))
        self.replace['>LAST_DATE_TIME'] = datetime.fromtimestamp(
            int(os.path.getmtime(filename)))

    def render(self, sheet=0, layers={}, replace={}):
        replace2 = self.replace
        for key, value in replace.items():
            replace2[key] = value
        return self.data.render(sheet=sheet, layers=layers, replace=replace2)
