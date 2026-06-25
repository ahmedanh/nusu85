from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Start the SHAMEL gRPC face-recognition service (default port 50051)'

    def add_arguments(self, parser):
        parser.add_argument('--port', type=int, default=50051, help='gRPC server port')

    def handle(self, *args, **options):
        port = options['port']
        self.stdout.write(self.style.SUCCESS(f'Starting gRPC face service on port {port}...'))
        from attendance.grpc_server import serve
        srv = serve(port)
        try:
            srv.wait_for_termination()
        except KeyboardInterrupt:
            self.stdout.write('Stopping gRPC server...')
            srv.stop(grace=5)
