
from src.GL.BusinessLayer.ConfigManager import *
from src.UI.sg.ViewModels.BaseViewModel import *

CM = Singleton()


class MainViewModel( BaseViewModel ):

    def __init__(self):
        super().__init__()

    def get_view(self) -> list:
        repo_dirs = CM.get_config_item(CF_REPO_DIRS) or []
        repo_dirs_soph = CM.get_config_item(CF_REPO_DIRS_SOPH) or []

        # Start
        x_GN = max( len( self.get_label( CF_REPO_DIR ) ), len( self.get_label( CF_REPO_DIRS_SOPH ) ),
                    len( self.get_label( CF_INPUT_PATH ) ), len( self.get_label( CF_INPUT_PATHS_SOPH ) ),
                    len(self.get_label(CF_FILE_NAME)), len( self.get_label( CF_DEBUG_METHOD_NAME ) ) )

        tab1_layout = [
            self.inbox( CF_FILE_NAME, x=x_GN, evt=True ),
            # Repositories
            self.frame( FRAME_REPOSITORIES, [
                self.inbox( CF_REPO_DIR, x=x_GN, x2=self._x_path, evt=True, folder_browse=True,
                            dft=repo_dirs[0] if repo_dirs and len( repo_dirs ) > 0 else None ),
                self.multi_frame(
                    FRAME_REPO_BUTTONS,
                    [[self.button( CMD_ADD_REPO )],
                     [self.button( CMD_DELETE_REPO )],
                     [self.button( CMD_CLEAR_REPO )]],
                    expand_x=True, justify='r' ),
                self.combo( CF_REPO_DIRS_SOPH, [i for i in repo_dirs_soph], x=x_GN,
                            dft=repo_dirs_soph[0] if repo_dirs_soph and len( repo_dirs_soph ) > 0 else None ),
                self.inbox( CF_DEBUG_METHOD_NAME, x=x_GN ),
            ], border_width=1, expand_x=True ),
            # Compare paths
            # self.frame( FRAME_COMPARE_PATHS, [
            #     self.inbox( CF_INPUT_PATH, x=x_GN, x2=self._x_path, evt=True, file_browse=True,
            #                 dft=CmpM.compare_paths[0] if len(CmpM.compare_paths) > 0 else None ),
            #     self.multi_frame(
            #         FRAME_COMPARE_BUTTONS,
            #         [[self.button( CMD_ADD_FILE_NAME )],
            #          [self.button( CMD_DELETE_FILE_NAME )],
            #          [self.button( CMD_CLEAR_FILE_NAME )]],
            #         expand_x=True, justify='r' ),
            #     self.combo( CF_INPUT_PATHS_SOPH, [i for i in CmpM.compare_paths_sophisticated], x=x_GN,
            #                 dft=CmpM.compare_paths_sophisticated[0] if len(CmpM.compare_paths_sophisticated) > 0
            #                 else None ),
            # ], border_width=1, expand_x=True ),
        ]

        # Parms
        x_OP = max( len( self.get_label( CF_OUTPUT_BASE_DIR ) ), len( self.get_label( CF_LIST_DIFF_ONLY ) ) )

        tab2_layout = [
            self.frame( FRAME_OUTPUT_PARMS, [
                self.inbox( CF_OUTPUT_BASE_DIR, x=x_OP, x2=self._x_path, folder_browse=True ),
                self.cbx( CF_LIST_DIFF_ONLY, x=x_OP, dft=True),
            ], border_width=1, expand_x=True, title='Output' ),
            self.frame(
                CMD_FACTORY_RESET, [[self.button( CMD_FACTORY_RESET )]],
                border_width=0, relief=sg.RELIEF_RAISED ),
        ]

        # The TabGroup layout - WTyp.IN must contain only Tabs
        tab_group_layout = [[sg.Tab( TAB_START, tab1_layout, key=TAB_START ),
                             sg.Tab( TAB_PARMS, tab2_layout, key=TAB_PARMS ),
                             ]]

        # The window layout - defines the entire window
        layout = [[sg.TabGroup( tab_group_layout, enable_events=True, key=TAB_GROUP, font=FONT_BIG )],
                  [self.frame( '-BUTTONS-',
                               [[self.button( CMD_START, font=FONT_BIG )]],
                               expand_x=True, justify='r' )],
                  [sg.Text( key=EXPAND, font='ANY 1', pad=(0, 0) )],
                  [sg.StatusBar( EMPTY, key=STATUS_MESSAGE, size=(90, 1), expand_x=True, relief=sg.RELIEF_SUNKEN )]]
        return layout

    @staticmethod
    def _disable(window, key, disabled=True):
        window[key].update( visible=not disabled, disabled=disabled )
