import riotwatcher
import asyncio
import time


class Watcher(riotwatcher.riotwatcher.RiotWatcher):

    def __init__(self, max_per_second, *args):
        self.lock = asyncio.Lock()
        self.interval = 1.0 / float(max_per_second)
        super().__init__(*args)

    async def rate_limited(self, f, *args):

        # acquire lock and start timer
        await self.lock.acquire()
        start = time.process_time()
        # execute function
        try:
            resp = f(*args)
        except Exception as e:
            print(f'exception occurred {e}')
            self.lock.release()
            return
        # check elapsed time
        elapsed = (time.process_time() - start)
        time_diff = self.interval - elapsed

        if time_diff > 0:
            await asyncio.sleep(time_diff)

        self.lock.release()
        return resp

    async def get_match_ids(self, user_id):
        match_ids = await self.rate_limited(self.match.matchlist_by_account, 'na1', user_id)
        if match_ids:
            return match_ids['matches']

    async def get_match(self, match_id):
        print('querying api for match data')
        return await self.rate_limited(self.match.by_id, 'na1', match_id)
