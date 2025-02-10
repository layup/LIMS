


''' tool bar items
- create report
- modify report
- search reports
-------
- upload ICP data
- add CHM data
-------


'''
from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject


class ToolbarManager(QObject):

    action_name = pyqtSignal(str)

    def __init__(self, toolbar):
        super().__init__()
        self.toolbar = toolbar
        self.actions = {}

        self.init_toolbar_setup()


    def init_toolbar_setup(self):
        print('init_toolbar')

        # set the icon sizes
        self.toolbar.setIconSize(QSize(36, 36))

        # define the actions
        create_action = QAction(QIcon('assets/icons/add_icon.png'), 'Create New Report', self.toolbar)
        edit_action = QAction(QIcon('assets/icons/edit_icon.svg'), 'Modify Existing Report', self.toolbar)
        search_action = QAction(QIcon('assets/icons/search_icon.png'), 'Search for Report', self.toolbar)
        upload_action = QAction(QIcon('assets/icons/upload_icon.png'), 'upload ICP data', self.toolbar)
        write_action = QAction(QIcon('assets/icons/write_icon.png'), 'write CHM data', self.toolbar)
        settings_action = QAction(QIcon('assets/icons/settings_icon.png'), 'Settings', self.toolbar)

        # save the actions
        self.actions['create'] = create_action
        self.actions['edit'] = edit_action
        self.actions['search'] = search_action
        self.actions['upload'] = upload_action
        self.actions['write'] = write_action
        self.actions['settings'] = settings_action

        # add actions to the tool bar
        self.toolbar.addAction(create_action)
        self.toolbar.addAction(edit_action)
        self.toolbar.addAction(search_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(upload_action)
        self.toolbar.addAction(write_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(settings_action)
        self.toolbar.addSeparator()

        # connect action signals
        create_action.triggered.connect(lambda: self.emit_signal('create'))
        edit_action.triggered.connect(lambda: self.emit_signal('edit'))
        search_action.triggered.connect(lambda: self.emit_signal('search'))
        upload_action.triggered.connect(lambda: self.emit_signal('upload'))
        write_action.triggered.connect(lambda: self.emit_signal('write'))
        settings_action.triggered.connect(lambda: self.emit_signal('settings'))

    def emit_signal(self, action_name):
        print(f'Entering emit_signal with action_index: {action_name}')
        self.action_name.emit(action_name)
