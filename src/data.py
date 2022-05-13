import certifi
import pymongo
from _thread import start_new_thread


class Data:
    def __init__(self):
        """initialize the database connection if possible, else data is stored locally"""
        self.scores = []

        self.db_string = "mongodb+srv://emanuel:<secret>@cluster0.ppsbo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        self.db = None
        self.connected = False
        start_new_thread(self.connect_to_db, ())

    def connect_to_db(self):
        """try to connect to the database"""
        try:
            client = pymongo.MongoClient(self.db_string, tlsCAFile=certifi.where())
            self.db = client["SpaceInvaders"]
            self.connected = True
            self.fetch_scores()
        except:
            self.connected = False

    def disconnect_from_db(self):
        """disconnect from the database, if connected"""
        if self.connected:
            self.connected = False
            self.db.client.close()

    def fetch_scores(self) -> None:
        """fetch the scores from the database, sorted by score, if connected"""
        if self.connected:
            scores = [doc for doc in self.db["scores"].find()]
            scores.sort(key=lambda x: x["score"], reverse=True)
            self.scores = scores

    def get_high_score(self) -> int:
        """get the highest score from the database"""
        return self.scores[0]["score"] if len(self.scores) > 0 else 0

    def save_score(self, name: str, score: int):
        """save new score to the database"""
        if len(self.scores) < 10 or score > self.scores[9]["score"]:
            self.scores.append({"name": name, "score": score})
            self.scores.sort(key=lambda x: x["score"], reverse=True)
            if self.connected:
                self.db["scores"].insert_one({"name": name, "score": score})
