class BiObject():
    def __init__(self):
        self._object_name = 'BiObject'

class BiContainer(BiObject):
    def __init__(self):
        super(BiContainer, self).__init__()
        self._object_name = 'BiContainer'
        self._observers = []
        self.action = ''

    def addObserver(self, observer):
        self._observers.append(observer)

    def notify(self, action: str):
        self.action = action
        initial_action = action
        for observer in self._observers:
            if self.action == initial_action:
                observer.update(self)


class BiObserver(BiObject):
    def __init__(self):
        super(BiObserver, self).__init__()
        self._object_name = 'BiObserver'

    def update(self, container: BiContainer):
        print('All observer should implement the update method: ', self._object_name) 

    def is_action(self, container: BiContainer, action: str):
        if container.action == action:
            return True
        return False     


class BiComponent(BiObserver):
    def __init__(self):
        super(BiComponent, self).__init__()
        self._object_name = 'BiComponent'    

    def update(self, container: BiContainer):
        print('All component should implement the update method: ', self._object_name) 

    def get_widget(self):  
        return None   


class BiModel(BiObserver):
    def __init__(self):
        super(BiModel, self).__init__()
        self._object_name = 'BiModel'    

    def update(self, container: BiContainer):
        print('All model should implement the update method: ', self._object_name ) 
            
