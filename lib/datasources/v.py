from datasource import DataSource
import subprocess
from lib.record import Record

class V(DataSource):

    def scrape_data(self):

        output = subprocess.check_output(self.connection_options['command'].split())

        line_buffer = list()
        for line in output.splitlines():
            line = line.strip()
            if line != "---------------------------------------------------":
                line_buffer.append(line)
            else:
                valuemap = dict()
                for l in line_buffer:
                    l_split = l.split()
                    value_flag = False
                    title_holder = ''
                    for word in l_split:
                        if value_flag:
                            valuemap[title_holder] = word
                            value_flag = False
                            title_holder = ''
                        elif word.endswith(':'):
                            title_holder = word.strip(':').lower()
                            value_flag = True

                if valuemap['ip'] != 'CannotFindIP':
                    entry = Record(valuemap['ip'])
                    for key in valuemap:
                        if key != 'ip':
                            entry.add_attribute(key, valuemap[key])
                    self.add_entry(entry)
                line_buffer = list()
        return self.entries