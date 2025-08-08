class Adapter:
    def __init__(self, *args, **kwargs):
        self.stats = kwargs.get("stats")

    def process_stats(self, stat_data: dict):
        raise NotImplementedError("process_stats method must be implemented")
