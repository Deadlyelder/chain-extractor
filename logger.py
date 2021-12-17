import time

class Logger:
    """Class that logs all the parameters from the
        node towards the storage """

    def __init__(self):
        self.last_time_progress_logged = time.time() # For backtracking
        self.log_progress_every = 10  # Interval of the logging time (in sec)
        self.avg_processing_tempo = 0
        self.n_of_tempo_measures = 10
        self.last_processed = 0
        self.minimal_total_count = 50
        self.tx_cache_miss_count = 0 # mempool
        self.tx_cache_length = 0

    def __getattr__(self, item):
        return self.log

    @staticmethod
    def log(*args):
        """Time logging"""
        print('[{}] {}'.format(
            time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            args[0] if len(args) == 1 else args
        ))

    def log_processing(self, i, total):
        """Cleaning logs"""
        if self._has_interval_passed() and self._is_enough_to_log(total):
            self.last_time_progress_logged = time.time()
            self.update_avg_processing_tempo(i)
            if i != self.last_processed:
                self.log('{0:.2f}% done, {1} left, txCache: {2}/{3}'.format(
                    100 * i / total,
                    self.get_time_left(i, total),
                    self.tx_cache_miss_count,
                    self.tx_cache_length,
                ))
                self.tx_cache_miss_count = 0
            self.last_processed = i

    def update_avg_processing_tempo(self, i):
        """Average processing period"""
        self.avg_processing_tempo = (
            (
                self.avg_processing_tempo * (self.n_of_tempo_measures - 1)
                + (i - self.last_processed) / self.log_progress_every
            ) / self.n_of_tempo_measures
        )

    def get_time_left(self, i, total):
        if self.avg_processing_tempo > 0:
            minutes, seconds = divmod(
                (total - i) / self.avg_processing_tempo, 60
            )
            hours, minutes = divmod(minutes, 60)
            return '%d:%02d:%02d' % (hours, minutes, seconds)
        return 'infinite'

    def register_tx_cache_miss(self):
        """Get tx cache"""
        self.tx_cache_miss_count += 1

    def register_cache_length(self, length):
        """Length of mempool"""
        self.tx_cache_length = length

    def _has_interval_passed(self):
        """Internal time passed"""
        return self._get_last_log_interval() > self.log_progress_every

    def _get_last_log_interval(self):
        """Last logged time interval"""
        return time.time() - self.last_time_progress_logged

    def _is_enough_to_log(self, total):
        """Reached logged limit"""
        return total > self.minimal_total_count