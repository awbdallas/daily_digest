import sys
import os
import datetime

from ast import literal_eval
from dateutil import parser


class CalendarVim():
    """ Used for parsing calendar.vim directories """

    def __init__(self, calendar_folder_path):
        if not os.path.exists(calendar_folder_path):
            print('Calendar folder does not exist')
            sys.exit(0)
        else:
            self.calendar_folder = calendar_folder_path
            self.calendars = []
            self.load_calendar()

    def load_calendar(self):
        """
        Layout (as far as I can tell) is something like
        calendar.vim/local/calendarList <-- gives us calendar lists
        calendar.vim/local/event/{calendar.id}/year/month/0
        ^ actual events

        This method should load all of those files, and return a list of
        calendars. Those calendars should have lists of events
        """
        calendar_list_file = self.calendar_folder + '/local/calendarList'

        if not os.path.isfile(calendar_list_file):
            print('Unable to find calendarList. May be no entries')
            sys.exit(0)

        with open(calendar_list_file, 'r') as fh:
            file_contents = fh.read()

        try:
            calendar_list_dict = literal_eval(file_contents)
        except:
            print('Error parsing calendar_file')
            sys.exit(0)

        for calendar in calendar_list_dict['items']:
            self.calendars.append(Calendar(calendar))

        self.populate_calendars()

    def populate_calendars(self):
        if len(self.calendars) == 0:
            print('Either no calendars or not loaded.')
            sys.exit(0)

        for calendar in self.calendars:
            calendar_path = self.calendar_folder +\
                    '/local/event/{}/'.format(calendar.id)

            # grabbed from: http://stackoverflow.com/a/19587581
            for subdir, dirs, files in os.walk(calendar_path):
                for file in files:
                    with open(os.path.join(subdir, file), 'r') as fh:
                        result = fh.read()

                    try:
                        events_dict = literal_eval(result)
                    except:
                        print('Error parsing events on file {}'.fomrat(
                            os.path.join(subdir, file)
                        ))
                        sys.exit(0)

                    for event in events_dict['items']:
                        calendar.add_event(event)

    def get_events_for_day(self, day):
        holding_dict = {}

        for calendar in self.calendars:
            holding_dict[calendar] = calendar.get_events_for_day(day)
            
        return holding_dict


class Calendar():
    """Calendars for calendar.vim."""

    def __init__(self, setup_dict):
        # something tells me this is a bad idea.
        for key in setup_dict:
            setattr(self, key, setup_dict[key])
        self.events = []

    def add_event(self, setup_dict):
        self.events.append(Events(setup_dict))

    # get events for a day
    def get_events_for_day(self, day):
        returning_events = []

        for event in self.events:
            start = datetime.date(event.start.year, event.start.month,
                                    event.start.day)
            end = datetime.date(event.end.year, event.end.month,
                                event.end.day)
            if day >= start and day <= end:
                returning_events.append(event)

        return returning_events


class Events():
    """Calendar events for calendar.vim."""

    def __init__(self, setup_dict):
        # yeah, probably still a bad idea
        required_keys = ['id', 'summary', 'end', 'start']
        for key in required_keys:
            if not setup_dict.get(key, None):
                print('Events not setup correct')
                sys.exit(0)

        for key in setup_dict:
            if key == 'start' or key == 'end':
                if setup_dict[key].get('date', None):
                    setattr(self, key, parser.parse(setup_dict[key]['date']))
                elif setup_dict[key].get('dateTime', None):
                    setattr(self, key,
                            parser.parse(setup_dict[key]['dateTime']))
            else:
                setattr(self, key, setup_dict[key])
