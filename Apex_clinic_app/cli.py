
import click
from Apex_clinic_app.extensions import db
from sysfunction import backendsysuser



def register_cli(app):
    @app.cli.command('runfunction')
    @click.argument('fname')
    def runfunction(fname):
        fname = backendsysuser
        if fname:
            fname()
            print(f'function:{fname} executed successfully')
        else:
            print(f'function:{fname} not recognized')



