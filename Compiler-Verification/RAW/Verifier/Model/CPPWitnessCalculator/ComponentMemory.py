

class ComponentMemory:

    def __init__(self, templateId: int,
                 templateName: str,
                 signalStart: int,
                 inputCounter: int,
                 componentName: str,
                 idFather: int,
                 subcomponents: list,
                 subcomponentsParallel: list = None):
        self.templateId = templateId
        self.templateName = templateName
        self.signalStart = signalStart
        self.inputCounter = inputCounter
        self.componentName = componentName
        self.idFather = idFather
        self.subcomponents = subcomponents
        self.subcomponentsParallel = subcomponentsParallel


