import sys
import os
import datetime

from ast import literal_eval
from dateutil import parser
from tabulate import tabulate
from lib.source_interface import Source_Interface


class CalendarVim(Source_Interface):
    """Used for parsing calendar.vim directories"""

    def __init__(self, calendar_folder_path, forecast_days):
        """
        Purpose: Setting up Calendar Vim Object. This includes loading the
        calendars
        which in turn sets up the events.
        PArameters: Path to the calendar.vim folder that we're assuming is
        setup correctly.
        Returns CalendarVim object
        """
        if not os.path.exists(calendar_folder_path):
            print('Calendar folder does not exist')
            sys.exit(0)
        else:
            self._calendar_folder = calendar_folder_path
            self._calendars = []
            self._load_calendar()
            self._forecast_days = forecast_days

    def get_digest(self):
        """Hopefully this is the only real method that's used"""
        table_headers = ['Calendar', 'Event', 'Date Start', 'Date End']
        table_data = []

        today = datetime.date.today()
        calendar_events = self._get_events_for_day(today)
        try:
            for calendar in calendar_events:
                for event in calendar_events[calendar]:
                    # reoccuring event, so it's today
                    table_data.append([
                        calendar.summary,
                        event.summary,
                        event.start,
                        event.end])

            return tabulate(table_data, table_headers, tablefmt='html')
        except:
            return 'Error getting Reddit digest'

    def _load_calendar(self):
        """
        Purpose:
        Returns: Nothing, but populates calendar
        Layout (as far as I can tell) is something like
        calendar.vim/local/calendarList <-- gives us calendar lists
        calendar.vim/local/event/{calendar.id}/year/month/0
        ^ actual events

        """
        calendar_list_file = self._calendar_folder + '/local/calendarList'

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
            self._calendars.append(self.Calendar(calendar))

        self._populate_calendars()

    def _populate_calendars(self):
        """
        Purpose: Populate vim calendars with events
        Parameters: None
        Returns: Nothing, but _self.calendars.events should be populated
        Notes:
            Was noted before, but events are stored as dicts in files, that's
            why os.walk is used to look for files and then literal_evaled. Also worth noting
            you should be really careful about what ends up in calendar_Vim folders because
            of the literal eveal
        """
        if len(self._calendars) == 0:
            print('Either no calendars or not loaded.')
            sys.exit(0)

        for calendar in self._calendars:
            calendar_path = self._calendar_folder +\
                    '/local/event/{}/'.format(calendar.id)

            # grabbed from: http://stackoverflow.com/a/19587581
            for subdir, dirs, files in os.walk(calendar_path):
                for file in files:
                    if file != '0':
                        # Filename as far as I can tell is always 0
                        continue
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

    def _get_events_for_day(self, day):
        """
        Purpose: Collect all events for all calendars.
        Returns: Dict of calendars as keys with list of events as values
        parameters: days and optionally a number of days as forecast
        """
        holding_dict = {}

        for calendar in self._calendars:
            holding_dict[calendar] = calendar.get_events_for_day(
                day, forecast=self._forecast_days)
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
            self.events.append(CalendarVim.Events(setup_dict))

        def get_events_for_day(self, day, forecast):
            """
            Purpose: Get all events for a calendar for a date and forecase if
            specified.
            Parameters: day should be a datetime
            Returns: List of events for that day
            """
            returning_events = []
            possible_days = self.get_date_range(
                day, day + datetime.timedelta(days=forecast))

            for event in self.events:
                event_days = self.get_date_range(event.start, event.end)

                for pday in possible_days:
                    if pday in event_days:
                        returning_events.append(event)
                        break
            return returning_events

        def get_date_range(self, day_one, day_two):
            """
            Purpose: Giving a range of datetimes mostly to check if it's in it
            Parameters: Day should be a datetime
            Returns: List of datetimes between day_two and day_one
            """
            returning_list = []
            delta = day_two - day_one

            for x in range(delta.days + 1):
                if isinstance(day_one, datetime.datetime):
                    returning_list.append(day_one.date() +
                                          datetime.timedelta(days=x))
                elif isinstance(day_one, datetime.date):
                    returning_list.append(day_one +
                                          datetime.timedelta(days=x))

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
                        setattr(self, key,
                                parser.parse(setup_dict[key]['date']))
                    elif setup_dict[key].get('dateTime', None):
                        setattr(self, key,
                                parser.parse(setup_dict[key]['dateTime']))
                else:
                    setattr(self, key, setup_dict[key])
