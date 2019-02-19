from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import TimeoutError
from django.core.management.base import BaseCommand, CommandError

import gsoc.settings as config
from gsoc.models import Scheduler
from gsoc.common.utils import commands

class Command(BaseCommand):
    help = 'Run the cron command to process items such as sending scheduled emails etc.'
    tasks = ['build_items', 'process_items']
    requires_system_checks = False   # for debugging

    def add_arguments(self, parser):
        parser.add_argument(
            'task',
            nargs='?',
            default=self.tasks[0],
            choices=self.tasks,
            type=str,
            help='The task which will be started'
        )
        parser.add_argument(
            '-t',
            '--timeout',
            nargs='?',
            default=config.RUNCRON_TIMEOUT,
            type=int,
            help='Set timeout'
        )
        parser.add_argument(
            '-n',
            '--num_workers',
            nargs='?',
            default=config.RUNCRON_NUM_WORKERS,
            type=int,
            help='Set number of workers'
        )

    def build_items(self, options):
        # build tasks
        self.stdout.write(self.style.SUCCESS('Build items'), ending='\n')
        # process items
        self.process_items(options)

    def handle_process(self, scheduler):
        self.stdout.write('Running command {}:{}'
            .format(scheduler.command, scheduler.id), ending='\n')
        err = getattr(commands, scheduler.command)(scheduler)
        if not err:
            self.stdout.write(self.style.SUCCESS('Finished command {}:{}'
                .format(scheduler.command, scheduler.id)), ending='\n')
            scheduler.success = True
            scheduler.save()

        else:
            self.stdout.write(self.style.ERROR('Command {}:{} failed with error: {}'
                .format(scheduler.command, scheduler.id, err)), ending='\n')
            scheduler.success = False
            scheduler.last_error = err
            scheduler.save()

    def process_items(self, options):
            schedulers = Scheduler.objects.exclude(success=True)
            if len(schedulers) is not 0:
                try:
                    pool = ThreadPool(options['num_workers'])
                    res = pool.map_async(self.handle_process, schedulers)
                    res.get(timeout=options['timeout'])
                    pool.close()
                    pool.join()
                except TimeoutError as e:
                    self.stdout.write(self.style.ERROR('Time limit exceeded'), ending='\n')

            else:
                self.stdout.write(self.style.SUCCESS('No scheduled tasks'), ending='\n')

    def handle(self, *args, **options):
        if options['task']:
            getattr(self, options['task'])(options)
        else:
            self.build_items(options)
