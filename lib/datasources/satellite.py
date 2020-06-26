from datasource import DataSource
from lib.record import Record
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import dateutil.parser
from datetime import datetime, timedelta

class Satellite(DataSource):

    def scrape_data(self):

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        page = 1
        page_not_empty = True
        max_attempts = 50
        attempts = 0
        while page_not_empty and attempts < max_attempts:
            url = self.connection_options['url'] + '?page=' + str(page)
            page += 1
            req = requests.get(url,
                               auth=HTTPBasicAuth(self.connection_options['username'],
                                                  self.connection_options['password']),
                               verify=False)
            full_results = req.json()
            for key in req.json():
                if key == 'results':
                    if len(full_results[key]) == 0:
                        page_not_empty = False
                    else:
                        results = full_results[key]
                        for host in results:
                            if 'ip' in host and host['ip'] is not None and len(host['ip']) >= 6:
                                r = Record(host['ip'].strip())
                                for attribute_name in host:
                                    if attribute_name.lower().strip() == 'last_report' and \
                                            isinstance(host['last_report'], basestring):
                                        # determine if actively reporting to satellite based on min_days_reported_considered_active
                                        r.add_attribute('is_reporting_to_satellite',
                                                        self.is_reporting_to_satellite(str(host['last_report'])))
                                    elif attribute_name != 'ip':
                                        r.add_attribute(str(attribute_name), host[attribute_name])
                                self.add_entry(r)
            attempts += 1
        return self.entries

    def is_reporting_to_satellite(self, last_reported_time):
        """
        :param last_reported_time:
        :return: bool
        """
        min_days = int(self.connection_options['min_days_reported_considered_active'])
        dt = dateutil.parser.parse(last_reported_time).replace(tzinfo=None)
        time_delta_between_last_report = datetime.now() - dt
        if time_delta_between_last_report.days > min_days:
            return False
        else:
            return True
