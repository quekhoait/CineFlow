from abc import ABC, abstractmethod
from app.repository import film_repo

class FilmsStrategy(ABC):
    @abstractmethod
    def get_films(self):
        pass

class ShowingFilmsStrategy(FilmsStrategy):
    def get_films(self):
        return film_repo.get_now_showing()

class FutureFilmsStrategy(FilmsStrategy):
    def get_films(self):
        return film_repo.get_release_showing()

class AllFilmsStrategy(FilmsStrategy):
    def get_films(self):
        return film_repo.get_all()

class FilmFilterContext:
    def __init__(self):
        self._strategy: dict[str, FilmsStrategy] = {
            "future": FutureFilmsStrategy(),
            "showing": ShowingFilmsStrategy(),
            "all": AllFilmsStrategy()
        }

    def add_strategy(self, key:str, value:FilmsStrategy):
        if key in self._strategy:
            raise ValueError(f"Films strategy {key} already exists")
        self._strategy[key] = value

    def get_films(self, key = None):
        return self._strategy.get(key, self._strategy["all"]).get_films()