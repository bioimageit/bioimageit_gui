class BiObject:
    def __init__(self):
        self._object_name = 'BiObject'

   
class BiAction(BiObject):
    def __init__(self, state: str = ""):
        super().__init__()
        self._object_name = "BiAction"
        self.state = state
        self.parent_container = None


class BiStates:
    DEFAULT = "States.DEFAULT"


class BiContainer(BiObject):
    def __init__(self, parent: BiObject = None):
        super().__init__()
        self._object_name = 'BiContainer'
        self._observers = []

        self.states = None
        self.current_state = BiStates.DEFAULT    

        self._childs = []
        self._parent = parent
        if parent:
            parent.add_child(self)

    def add_child(self, child: BiObject):
        self._childs.append(child)

    def register(self, observer):
        self._observers.append(observer)

    def emit(self, state_name: str):
        self.current_state = state_name
        action = BiAction(state_name)
        action.parent_container = self
        self.emit_action(action)

    def emit_action(self, action: BiAction):
        for observer in self._observers:
            observer.update(action)


class BiActuator(BiObject):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiObserver'

    def update(self, action: BiAction):
        raise NotImplementedError("Please implement BiObserver update method")


class BiComponent(BiActuator):
    def __init__(self):
        super(BiComponent, self).__init__()
        self._object_name = 'BiComponent'    
        self.show_viewer = False

    def update(self, action: BiAction):
        raise NotImplementedError("Please implement ", self._object_name,
                                  " update method")

    def get_widget(self):  
        return None   


class BiModel(BiActuator):
    def __init__(self):
        super(BiModel, self).__init__()
        self._object_name = 'BiModel'    

    def nowarning(self):
        pass    

    def update(self, action: BiAction):
        raise NotImplementedError("Please implement ", self._object_name,
                                  " update method")
