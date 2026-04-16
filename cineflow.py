import os
import sys
import webbrowser

import click
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app, db, models

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """Tự động import các model vào Flask Shell để tiện debug."""
    return dict(
        app=app, db=db, User=models.User, Rules=models.Rules, RoleEnum=models.RoleEnum,
        UserAuthMethod=models.UserAuthMethod, Cinema=models.Cinema, Room=models.Room, Seat=models.Seat,
        Film=models.Film, Show=models.Show, BookingStatus=models.BookingStatus, PaymentStatus=models.PaymentStatus,
        Booking=models.Booking, Ticket=models.Ticket, Payment=models.Payment,
        BookingPaymentStatus=models.BookingPaymentStatus, PaymentType=models.PaymentType
    )

@app.cli.command()
@click.option('--length', default=25, help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None, help='Directory where profiler data files are saved.')
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    try:
        from werkzeug.middleware.profiler import ProfilerMiddleware
    except ImportError:
        from werkzeug.contrib.profiler import ProfilerMiddleware

    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


@app.cli.command("seed")
def seed():
    """Run database seeding."""
    from app.utils.seeder import run_seeding
    print("Starting seed...")
    run_seeding()


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    pass