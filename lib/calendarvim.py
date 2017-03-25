import sys
import os
import datetime

from ast import literal_eval
from dateutil import parser


class CalendarVim():
    """ Used for parsing calendar.vim directories """

    def __init__(self, calendar_folder_path):
        """
        Purpose: Setting up Calendar Vim Object. This includes loading the calendars
        which in turn sets up the events.
        PArameters: Path to the calendar.vim folder that we're assuming is
        setup correctly.
        Returns CalendarVim object
        """
        if not os.path.exists(calendar_folder_path):
            print('Calendar folder does not exist')
            sys.exit(0)
        else:
            self.calendar_folder = calendar_folder_path
            self.calendars = []
            self.load_calendar()

    def load_calendar(self):
        """
        Purpose:
        Returns: Nothing, but populates calendar
        Layout (as far as I can tell) is something like
        calendar.vim/local/calendarList <-- gives us calendar lists
        calendar.vim/local/event/{calendar.id}/year/month/0
        ^ actual events

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
        """
        Purpose: Populate vim calendars with events
        Parameters: None
        Returns: Nothing, but self.calendars.events should be populated
        Notes:
            Was noted before, but events are stored as dicts in files, that's
            why os.walk is used to look for files and then literal_evaled. Also worth noting
            you should be really careful about what ends up in calendar_Vim folders because
            of the literal eveal
        """
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

    def get_events_for_day(self, day, forecast=None):
        """
        Purpose: Collect all events for all calendars.
        Returns: Dict of calendars as keys with list of events as values
        parameters: days and optionally a number of days as forecast
        """
        holding_dict = {}

        if not isinstance(forecast, int):
            raise TypeError("forecast must be type int")
        if not isinstance(day, datetime.date):
            raise TypeError("Expecting datetime.date")

        for calendar in self.calendars:
            if forecast:
                holding_dict[calendar] = calendar.get_events_for_day(day)
            else:
                holding_dict[calendar] = calendar.get_events_for_day(day, forecast=forecast)

        return holding_dict


class Calendar():
    """Calendars for calendar.vim."""

    def __init__(self, setup_dict):
        """
        Purpose: Setup a calendar object
        Parameters: setup_dict which is a bunch of keys that are taken from
        the calendarList file. The biggest ones are id and summary
        returns object
        """
        for key in setup_dict:
            setattr(self, key, setup_dict[key])
        self.events = []

    def add_event(self, setup_dict):
        "Add events to calendar with setup dict of the event"
        self.events.append(Events(setup_dict))

    def get_events_for_day(self, day, forecast=None):
        """
        Purpose: Get all events for a calendar for a date and forecase if
        specified.
        Parameters: day should be a datetime
        Returns: List of events for that day
        """
        returning_events = []

        for event in self.events:
            if forecast:
                event_days = self._get_date_range(event.start,
                    event.end + datetime.timedelta(days=forecast))
            else:
                event_days = self._get_date_range(event.start, event.end)
            if day in event_days:
                returning_events.append(event)
        return returning_events

    def _get_date_range(self, day_one, day_two):
        """
        Purpose: Giving a range of datetimes mostly to check if it's in it
        Parameters: Day should be a datetime
        Returns: List of datetimes between day_two and day_one
        """
        returning_list = []
        delta = day_two - day_one

        for x in range(delta.days):
            returning_list.append(day_one.date() + datetime.timedelta(days=x))
        return returning_list


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