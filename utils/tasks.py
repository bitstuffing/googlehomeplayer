from background_task import background
from player.models import Playlist

@background(schedule=5)
def run_playlist():
    pass
