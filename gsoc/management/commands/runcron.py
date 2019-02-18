from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Run the cron command to process items such as sending scheduled emails etc.'
        
    def handle(self, *args, **options):
        # Add yout logic here
        # This is the task that will be run
        self.stdout.write('This was extremely simple!!!', ending='')
        