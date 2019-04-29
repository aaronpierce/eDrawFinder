from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class Updater():
    def __init__(self, core_app):
        self.app = core_app
        self.scheduler  = BackgroundScheduler()
        self.trigger = IntervalTrigger(minutes=120)

        self.scheduler.add_job(self.update, self.trigger)
        self.scheduler.start()

    
    def update(self):
        self.app.log.writter.info('Updating event start')
        self.app.pre_build(True)