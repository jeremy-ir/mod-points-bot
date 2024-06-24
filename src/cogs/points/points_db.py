from abc import ABC, abstractmethod

class PointsDb(ABC):

    @abstractmethod
    def getUserPoints(self, user_id: int):
        pass

    @abstractmethod
    def setUserPoints(self, user_id: int, point_change: int):
        pass

    @abstractmethod
    def getAllUserScores(self):
        pass

    @abstractmethod
    def removeUser(self, user_id: int):
        pass

    @abstractmethod
    def getIntMax(self):
        pass