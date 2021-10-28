from bioimageit_gui.core.framework import BiContainer


class BiFinderContainer(BiContainer):
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

    def setCurrentCategory(self, id:str, name:str, doc:str = ''):
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

    def movePrevious(self):
        self.pos_history -= 1
        if self.pos_history < 0 :
            self.pos_history = 0
        self.curent_category = self.history[self.pos_history]
        self.curent_category_name = self.history_names[self.pos_history]
        self.curent_category_doc = self.history_docs[self.pos_history]

    def moveNext(self):
        self.pos_history += 1
        if self.pos_history >= len(self.history):
            self.pos_history = len(self.history) - 1
        self.current_category = self.history[self.pos_history] 
        self.current_category_name = self.history_names[self.pos_history] 
        self.current_category_doc = self.history_docs[self.pos_history] 

    def moveHome(self):
        self.setCurrentCategory('root', 'Home', '')    
