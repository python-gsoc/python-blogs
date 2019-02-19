import gsoc.settings as config
from django.core.management.base import BaseCommand, CommandError

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

    def process_items(self, options):
        self.stdout.write(self.style.SUCCESS('Process Items'), ending='\n')

    def handle(self, *args, **options):
        if options['subcommand']:
            getattr(self, options['subcommand'])(options)
        else:
            self.build_items(options)