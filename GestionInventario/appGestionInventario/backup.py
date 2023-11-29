from django.core.management import call_command

def backup():
    try:        
        call_command('dbbackup')        
    except:
        pass