import asyncio
import aiofiles
import threading
import time

from watcher.watcher import Watcher


class CrawlJob:

    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.watchers = []
        self.keys = set()

        self.seen_matches = set()
        self.seen_matches_lock = threading.Lock()

        self.player_queue = set()
        self.player_queue_lock = threading.Lock()

        self.seen_players = set()

    def register_key(self, key):
        if key not in self.keys:
            self.watchers.append(Watcher(key, self.rate_limit, self))
            self.keys.add(key)

    async def _crawl_match(self, watcher, match_id):
        self.seen_matches_lock.acquire()
        if match_id['gameId'] not in self.seen_matches:
            self.seen_matches.add(match_id['gameId'])
            self.seen_matches_lock.release()

            match_object = await watcher.get_match(match_id['gameId'])

            async with aiofiles.open(f'all_matches/match_{match_id["gameId"]}.json', 'w') as outfile:
                await outfile.write(match_object)

            for participant in match_object['participantIdentities']:
                user_id = participant['player']['accountId']

                # this is threadsafe since we double check before adding it,
                # thus not needing to acquire the lock for cases where players already exist in the queue

                if user_id not in self.seen_players:
                    self.seen_players.add(user_id)
                    self.player_queue_lock.acquire()
                    if user_id not in self.player_queue:
                        self.player_queue.add(user_id)
                    self.player_queue_lock.release()

    async def _start_watching(self, watcher, max_runs=1000, max_retries=100):
        retries = 0

        for i in range(0, max_runs):
            while len(self.player_queue) > 0:
                time.sleep(.3)
                retries += 1
                if retries == max_retries:
                    return

            self.player_queue_lock.acquire()
            user_id = self.player_queue.pop()
            self.player_queue_lock.release()

            match_ids = watcher.get_match_ids(user_id)
            asyncio.gather(*[watcher.get_match(m_id) for m_id in match_ids])

    def run(self, user_id):
        self.player_queue.add(user_id)
        asyncio.gather(*[self._start_watching(w_obj) for w_obj in self.watchers])
