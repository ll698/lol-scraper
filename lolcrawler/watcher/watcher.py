import riotwatcher
import threading
import time


class Watcher(riotwatcher.riotwatcher.RiotWatcher):

    def __init__(self, max_per_second, *args):
        self.lock = threading.Lock()
        self.interval = 1.0 / float(max_per_second)
        super().__init__(*args)

    async def rate_limited(self, f, *args):

        # acquire lock and start timer
        self.lock.acquire()
        start = time.process_time()

        # execute function
        resp = f(*args)

        # check elapsed time
        elapsed = (time.process_time() - start)
        time_diff = self.interval - elapsed

        if time_diff > 0:
            time.sleep(time_diff)

        self.lock.release()
        return resp

    async def get_match_ids(self, user_id):
        match_ids = await self.rate_limited(self.match.matchlist_by_account, 'na1', user_id)
        return match_ids['matches']

    async def get_match(self, match_id):
        return await self.rate_limited(self.match.by_id, 'na1', match_id)
