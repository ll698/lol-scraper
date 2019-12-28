import asyncio
import aiofiles
import json

from watcher.watcher import Watcher


class CrawlJob:

    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.watchers = []
        self.keys = set()

        self.seen_matches = set()
        #self.seen_matches_lock = threading.Lock()

        self.player_queue = set()
        #self.player_queue_lock = threading.Lock()

        self.seen_players = set()
        self.match_count = 0

    def register_key(self, key):
        if key not in self.keys:
            self.watchers.append(Watcher(self.rate_limit, key))
            self.keys.add(key)

    async def _crawl_match(self, watcher, match_id):
        #self.seen_matches_lock.acquire()
        if match_id['gameId'] not in self.seen_matches:
            self.seen_matches.add(match_id['gameId'])
            #self.seen_matches_lock.release()
            match_object = await watcher.get_match(match_id['gameId'])
            print(f'writing match object {match_id["gameId"]}')
            try:
                async with aiofiles.open(f'match_data/match_{match_id["gameId"]}.json', 'a+') as outfile:
                    await outfile.write(json.dumps(match_object))
            except Exception as e:
                print(e)
            if match_object:
                for participant in match_object['participantIdentities']:
                    user_id = participant['player']['accountId']

                    # this is threadsafe since we double check before adding it,
                    # thus not needing to acquire the lock for cases where players already exist in the queue
                    if user_id not in self.seen_players:
                        self.seen_players.add(user_id)
                        #self.player_queue_lock.acquire()
                        if user_id not in self.player_queue:
                            self.player_queue.add(user_id)
                        #self.player_queue_lock.release()

    async def _start_watching(self, watcher, max_runs=1000, max_retries=100):
        retries = 0
        try:
            for i in range(0, max_runs):
                print(f'waiting, number of completed runs {i}')
                while len(self.player_queue) == 0:
                    await asyncio.sleep(1)
                    retries += 1
                    if retries == max_retries:
                        return

                #self.player_queue_lock.acquire()
                user_id = self.player_queue.pop()
                #self.player_queue_lock.release()

                match_ids = await watcher.get_match_ids(user_id)

                if match_ids:
                    await asyncio.gather(*[self._crawl_match(watcher, m_id) for m_id in match_ids])

        except Exception as e:
            print("EXCEPTION ", e)

    async def run(self, user_id):
        print(f'starting crawl job with user {user_id}')
        self.player_queue.add(user_id)
        print(f'{self.player_queue}')
        return await asyncio.gather(*[self._start_watching(w_obj) for w_obj in self.watchers])


