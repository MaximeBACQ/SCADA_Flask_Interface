class SharedState:
    def __init__(self):
        self.coils_state = {
            "entry": False,
            "exit": False,
            "b": False,
            "g": False,
            "m": False
        }
        
        self.driverHasControl = {
            "entry": True,
            "exit": True,
            "b": True,
            "g": True,
            "m": True
        }