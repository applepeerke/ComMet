import PySimpleGUI as sg


class ProgressMeter(object):
    def __init__(self, title=None, count_max=100):
        self._max = count_max
        self._title = title
        self._step = int(count_max / 100) or 1

    def increment(self, count) -> bool:
        if count % self._step == 0:
            return sg.one_line_progress_meter(self._title, count + self._step, self._max)
        return True
