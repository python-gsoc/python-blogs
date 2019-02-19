from multiprocessing.dummy import Pool as ThreadPool
from django.core.management.base import BaseCommand, CommandError

import gsoc.settings as config
from gsoc.models import Scheduler
from gsoc.common.utils import commands

class Command(BaseCommand):
    help = 'Run the cron command to process items such as sending scheduled emails etc.'
    requires_system_checks = False   # for debugging

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(title='task', dest='subcommand')

        subparser_process_items = subparsers.add_parser('process_items', help='Process items')
        subparser_process_items.add_argument(
            '-t',
            '--timeout',
            nargs='?',
            default=config.RUNCRON_TIMEOUT,
            type=int,
            help='Set timeout'
        )
        subparser_process_items.add_argument(
            '-n',
            '--num_workers',
            nargs='?',
            default=config.RUNCRON_NUM_WORKERS,
            type=int,
            help='Set number of workers'
        )
        subparser_process_items.set_defaults(func=self.process_items)

        subparser_build_items = subparsers.add_parser('build_items', help='Build items')
        subparser_build_items.set_defaults(func=self.build_items)

    def build_items(self, options):
        self.stdout.write(self.style.SUCCESS('Build Items'), ending='\n')

    def handle_process(self, scheduler):
        self.stdout.write('Running command {}'.format(scheduler.command), ending='\n')
        if getattr(commands, scheduler.command)(scheduler):
            scheduler.success = True
            scheduler.save()

    def process_items(self, options):
        try:
            schedulers = Scheduler.objects.filter(success=False)
            if len(schedulers) is not 0:
                pool = ThreadPool(options['num_workers'])
                pool.map(self.handle_process, schedulers)
                pool.close()
                pool.join()
            else:
                self.stdout.write('No scheduled tasks', ending='\n')

        except Exception as e:
            self.stdout.write(e, ending='\n')

    def handle(self, *args, **options):
        if options['subcommand']:
            getattr(self, options['subcommand'])(options)
        else:
            self.build_items(options)
