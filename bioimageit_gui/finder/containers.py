from bioimageit_framework.framework import BiContainer


class BiFinderContainer(BiContainer):
    RELOAD = 'reload'
    RELOADED = 'reloaded'
    OPEN_TOOL = 'open_tool'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiFinderContainer'

        # data
        self.curent_category = 'root'
        self.curent_category_name = 'Home'
        self.curent_category_doc = ''
        self.categories = []
        self.tools = []
        self.parent_category = 'root'
        self.history = []
        self.history_names = []
        self.history_docs = []
        self.pos_history = 0
        self.clicked_tool = -1

    def set_current_category(self, id:str, name:str, doc:str = ''):
        self.curent_category = id
        self.curent_category_name = name
        self.current_category_doc = doc
        if self.pos_history <= len(self.history):
            for i in range(len(self.history), self.pos_history):
                self.history.pop(i)
                self.history_names.pop(i)
                self.history_docs.pop(i)
        self.history.append(id)
        self.history_names.append(name)
        self.history_docs.append(doc)
        self.pos_history = len(self.history) - 1 

    def action_previous(self, action):
        self.pos_history -= 1
        if self.pos_history < 0 :
            self.pos_history = 0
        self.curent_category = self.history[self.pos_history]
        self.curent_category_name = self.history_names[self.pos_history]
        self.curent_category_doc = self.history_docs[self.pos_history]
        self._notify(BiFinderContainer.RELOAD)

    def action_next(self, action):
        self.pos_history += 1
        if self.pos_history >= len(self.history):
            self.pos_history = len(self.history) - 1
        self.current_category = self.history[self.pos_history] 
        self.current_category_name = self.history_names[self.pos_history] 
        self.current_category_doc = self.history_docs[self.pos_history] 
        self._notify(BiFinderContainer.RELOAD)

    def action_home(self, action):
        self.set_current_category('root', 'Home', '')    
        self._notify(BiFinderContainer.RELOAD)

    def action_open_tile(self, action, tile_info):
        self.set_current_category(tile_info.id, tile_info.name, tile_info.doc)
        self._notify(BiFinderContainer.RELOAD)

    def action_open_tool(self, action, tool_id):
        self.clicked_tool = tool_id
        self._notify(BiFinderContainer.OPEN_TOOL)

    def action_reload_categories(self, action, categories):
        self.categories = categories
        self.tools = []
        self._notify(BiFinderContainer.RELOADED)

    def action_reload_tools(self, action, tools):
        self.tools = tools   
        self.categories = []  
        self._notify(BiFinderContainer.RELOADED)  

    def init(self):
        self._notify(BiFinderContainer.RELOAD)     
