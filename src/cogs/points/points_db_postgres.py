import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

from .points_db import PointsDb

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Constants
INT_MIN = -2147483648
INT_MAX =  2147483647

TABLE_NAME = "points"
USER_KEY = "user_id"
POINT_KEY = "user_points"

NUM_RETRY = 1

class PointsDbPostgres(PointsDb):
    def __init__(self):
        # Connect to the points-db
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
                                port = port,
                                keepalives=1,
                                keepalives_idle=30,
                                keepalives_interval=10,
                                keepalives_count=5
                            )
        cursor = self.connection.cursor()

        # Create a table if one doesn't exist
        query_string = "CREATE TABLE IF NOT EXISTS %s \
                        (%s BIGINT PRIMARY KEY NOT NULL, \
                            %s INTEGER NOT NULL);" % \
                        (TABLE_NAME, USER_KEY, POINT_KEY)
        cursor.execute(query_string)

    def reconnectDb(self):
        # Connect to the points-db
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
                                port = port,
                                keepalives=1,
                                keepalives_idle=30,
                                keepalives_interval=10,
                                keepalives_count=5
                            )

    def isOverUnderflow(self, a: int, b: int, result: int):
        result = a + b
        if(result < INT_MIN or result > INT_MAX):
            return True
        return False

    def getUserPoints(self, user_id: int):
        for i in range(NUM_RETRY + 1):
            try:
                with self.connection.cursor() as cursor:
                    query_string = "SELECT (%s) FROM %s WHERE %s = %d;" % (POINT_KEY, TABLE_NAME, USER_KEY, user_id)
                    cursor.execute(query_string)
                    points = cursor.fetchone()
                    if (points):
                        return points[0]
                    return 0
            except:
                self.reconnectDb()

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
        for i in range(NUM_RETRY + 1):
            try:
                with self.connection.cursor() as cursor:
                    query_string = "INSERT INTO %s (%s, %s) VALUES (%d, %d) ON CONFLICT (%s) DO UPDATE SET %s = EXCLUDED.%s;" \
                                    % (TABLE_NAME, USER_KEY, POINT_KEY, user_id, points, USER_KEY, POINT_KEY, POINT_KEY)
                    cursor.execute(query_string)
                    self.connection.commit()
                    return
            except:
                self.reconnectDb()

        # Verify the user's points were set properly; commenting out to save CPU cycles
        #newPoints = self.getUserPoints(user_id)
        #return (0 if newPoints == points else -1)
        return 0

    def getAllUserScores(self):
        for i in range(NUM_RETRY + 1):
            try:
                with self.connection.cursor() as cursor:
                    query_string = "SELECT * FROM %s" % (TABLE_NAME)
                    cursor.execute(query_string)
                    allUserScores = cursor.fetchall()
                    return allUserScores
            except:
                self.reconnectDb()

    def removeUser(self, user_id: int):
        for i in range(NUM_RETRY + 1):
            try:
                with self.connection.cursor() as cursor:
                    query_string = "DELETE FROM %s WHERE %s = %s" % (TABLE_NAME, USER_KEY, user_id)
                    cursor.execute(query_string)
                    self.connection.commit()
                    return
            except:
                self.reconnectDb()


    def getIntMax(self):
        return INT_MAX