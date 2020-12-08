class UpdateJob:
    def __init__(self, schedule_time):
        self.schedule_time = schedule_time
        self.start_time = None
        self.end_time = None
        self.files_created = []
        self.successful = False