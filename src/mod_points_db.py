import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Constants
POSTGRE_INT_MIN = -2147483648
POSTGRE_INT_MAX =  2147483647

TABLE_NAME = "points"
USER_KEY = "user_id"
POINT_KEY = "user_points"

# Set to False to use a dictionary instead of the database
REAL_DB = True

class ModPointsDb():
    def __init__(self):
        
        if (REAL_DB):
            # Connect to the mod-points-db
            result = urlparse(DATABASE_URL)
            username = result.username
            password = result.password
            database = result.path[1:]
            hostname = result.hostname
            port = result.port
            self.connection = psycopg2.connect(
                                  database = database,
                                  user = username,
                                  password = password,
                                  host = hostname,
                                  port = port
                              )
            self.cursor = self.connection.cursor()

            # Create a table if one doesn't exist
            query_string = "CREATE TABLE IF NOT EXISTS %s \
                            (%s BIGINT PRIMARY KEY NOT NULL, \
                             %s INTEGER NOT NULL);" % \
                            (TABLE_NAME, USER_KEY, POINT_KEY)
            self.cursor.execute(query_string)
        else:
            self.database = {}

    def isOverUnderflow(self, a: int, b: int, result: int):
        result = a + b
        if(result < POSTGRE_INT_MIN or result > POSTGRE_INT_MAX):
            return True
        return False

    def getUserPoints(self, user_id: int):
        if(REAL_DB):
            query_string = "SELECT (%s) FROM %s WHERE %s = %d;" % (POINT_KEY, TABLE_NAME, USER_KEY, user_id)
            self.cursor.execute(query_string)
            points = self.cursor.fetchone()
            if (points):
                return points[0]
            return 0
        else:
            if (user_id in self.database):
                return self.database[user_id]
            else:
                return 0

    def setUserPoints(self, user_id: int, point_change: int):
        points = self.getUserPoints(user_id)

        # If there's an over or underflow, set it to the maximum/minimum
        if (self.isOverUnderflow(points, point_change, points + point_change)):
            if (point_change < 0):
                points = POSTGRE_INT_MIN
            else:
                points = POSTGRE_INT_MAX
        else:
            points += point_change
        
        print("FIND ME LOGS: points = %d" % points)

        # Set the user's points
        if(REAL_DB):
            query_string = "INSERT INTO %s (%s, %s) VALUES (%d, %d) ON CONFLICT (%s) DO UPDATE SET %s = EXCLUDED.%s;" \
                            % (TABLE_NAME, USER_KEY, POINT_KEY, user_id, points, USER_KEY, POINT_KEY, POINT_KEY)
            self.cursor.execute(query_string)
            self.connection.commit()
        else:
            self.database[user_id] = points
        
        # Verify the user's points were set properly; commenting out to save CPU cycles
        #newPoints = self.getUserPoints(user_id)
        #return (0 if newPoints == points else -1)
        return 0

    def getAllUserScores(self):
        query_string = "SELECT * FROM %s" % (TABLE_NAME)
        self.cursor.execute(query_string)
        allUserScores = self.cursor.fetchall()
        return allUserScores

    def removeUser(self, user_id: int):
        query_string = "DELETE FROM %s WHERE %s = %s" % (TABLE_NAME, USER_KEY, user_id)
        self.cursor.execute(query_string)
        self.connection.commit()
        return