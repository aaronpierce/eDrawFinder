from apscheduler.schedulers.background import BackgroundScheduler

class Updater():
    def __init__(self, core_app):
        self.app = core_app
        self.sched = BackgroundScheduler()

        self.sched.add_job(self.update, 'interval', hours=1)
        self.sched.start()

    
    def update(self):
        self.app.log.writter.info("Updating event start")
        self.app.pre_build(True)