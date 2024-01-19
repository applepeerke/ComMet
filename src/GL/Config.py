# ---------------------------------------------------------------------------------------------------------------------
# ConfigManager.py
#
# Author      : Peter Heijligers
# Description : Return the configuration (crisp.config) in a dictionary.
# If crisp.config does not exist, it is created with default properties.
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-08-23 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------

from src.GL.Const import EMPTY

CONFIG = 'Config'
LATEST = 'Latest'

# Parameters
CF_DEBUG_METHOD_NAME = 'CF_DEBUG_METHOD_NAME'
CF_FILE_NAME = 'CF_FILE_NAME'
CF_REPO_DIR = 'CF_REPO_DIR'
CF_REPO_DIRS = 'CF_REPO_DIRS'
CF_REPO_DIRS_SOPH = 'CF_REPO_DIRS_SOPH'

CF_INPUT_PATH = 'CF_INPUT_PATH'
CF_INPUT_PATHS = 'CF_INPUT_PATHS'
CF_INPUT_PATHS_SOPH = 'CF_INPUT_PATHS_SOPH'
CF_OUTPUT_DIR = 'CF_BASE_OUTPUT_DIR'
CF_LIST_DIFF_ONLY = 'CF_DIFF_ONLY'
CF_AUTO_CLOSE_TIME_S = 'CF_AUTO_CLOSE_TIME_S'


configDict = {
    CF_DEBUG_METHOD_NAME: EMPTY,
    CF_FILE_NAME: EMPTY,
    CF_REPO_DIR: EMPTY,
    CF_REPO_DIRS: EMPTY,
    CF_REPO_DIRS_SOPH: EMPTY,

    CF_INPUT_PATH: EMPTY,
    CF_INPUT_PATHS: EMPTY,
    CF_INPUT_PATHS_SOPH: EMPTY,
    CF_OUTPUT_DIR: EMPTY,
    CF_LIST_DIFF_ONLY: True,
    CF_AUTO_CLOSE_TIME_S: 3,
}

config_desc_dict = {
    CF_DEBUG_METHOD_NAME: 'Debug method name',
    CF_FILE_NAME: 'File name',
    CF_REPO_DIR: 'Repository to compare',
    CF_REPO_DIRS_SOPH: 'Repositories selected',

    CF_INPUT_PATH: 'File to compare',
    CF_INPUT_PATHS_SOPH: 'Files selected',
    CF_OUTPUT_DIR: 'Output directory',
    CF_LIST_DIFF_ONLY: 'List different methods only',
    # Hidden
    CF_INPUT_PATHS: '-hidden-',
    CF_AUTO_CLOSE_TIME_S: 'Message box auto-close time',
}

configDictTooltip = {
    CF_AUTO_CLOSE_TIME_S: 'Message box auto-close time in seconds after a successful action. 0=Do not auto-close',
}
