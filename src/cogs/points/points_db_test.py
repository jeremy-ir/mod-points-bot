from .points_db import PointsDb
# Constants
INT_MIN = -2147483648
INT_MAX =  2147483647

TABLE_NAME = "points"
USER_KEY = "user_id"
POINT_KEY = "user_points"

class PointsDbTest(PointsDb):
    def __init__(self):
       self.database = {}

    def isOverUnderflow(self, a: int, b: int, result: int):
        result = a + b
        if(result < INT_MIN or result > INT_MAX):
            return True
        return False

    def getUserPoints(self, user_id: int):
        if (user_id in self.database):
            return self.database[user_id]
        else:
            return 0

    def setUserPoints(self, user_id: int, point_change: int):
        points = self.getUserPoints(user_id)

        # If there's an over or underflow, set it to the maximum/minimum
        if (self.isOverUnderflow(points, point_change, points + point_change)):
            if (point_change < 0):
                points = INT_MIN
            else:
                points = INT_MAX
        else:
            points += point_change

        # Set the user's points
        self.database[user_id] = points

        # Verify the user's points were set properly; commenting out to save CPU cycles
        #newPoints = self.getUserPoints(user_id)
        #return (0 if newPoints == points else -1)
        return 0

    def getAllUserScores(self):
        return list(self.database.items())

    def removeUser(self, user_id: int):
        del self.database[user_id]
        return

    def getIntMax(self):
        return INT_MAX