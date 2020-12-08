from singleton import Singleton

class UpdateManager(metaclass=Singleton):
    def __init__(self):
        self.jobs = []
    
    def add_job(self, job):
        self.jobs.append(job)