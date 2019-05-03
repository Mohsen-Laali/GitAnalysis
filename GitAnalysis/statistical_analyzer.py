import csv
from operator import itemgetter
from functools import partial
from operator import and_, or_
from datetime import datetime, date
import sys
maxInt = sys.maxsize


def co_routine(func):
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        g.next()
        return g

    return start


class StatisticalAnalyzer:
    def __init__(self, log_flag, read_mode='rb', write_mode='w'):
        self.log_flag = log_flag
        self.read_mode = read_mode
        self.write_mode = write_mode

    def log(self, log_str):
        if self.log_flag:
            print(log_str)
            print '*******************************************************'

    def iter_csv(self, file_name, keep_dictionary=None, except_dictionary=None):
        with open(file_name, self.read_mode) as csv_file_handler:
            reader = csv.DictReader(csv_file_handler)
            csv.field_size_limit(maxInt)

            def keep_except_row(r, f_dic, compare_func, and_or):
                if f_dic:
                    for key, value in f_dic.iteritems():
                        if isinstance(value, list):
                            # Checks condition for all member and reduces them with 'and' or 'or' function
                            if not reduce(and_or, map(partial(compare_func, r=r[key]), value)):
                                # if only one result false all condition is false
                                return False
                        else:
                            if not compare_func(r[key], value):
                                return False
                return True

            keep_row = partial(keep_except_row, compare_func=lambda v, r: r == v)
            except_row = partial(keep_except_row, compare_func=lambda v, r: r != v)

            if keep_dictionary:
                for row in reader:
                    if keep_row(r=row, f_dic=keep_dictionary, and_or=or_) and \
                            except_row(r=row, f_dic=except_dictionary, and_or=and_):
                        yield row
                    else:
                        continue

            else:
                for row in reader:
                    yield row

    def counter(self, iterator, count_column_limited):
        counted = {}
        flag_limited = None
        if isinstance(count_column_limited, list) or isinstance(count_column_limited, set):
            flag_limited = False
            count_column = count_column_limited
        elif isinstance(count_column_limited, dict):
            flag_limited = True
            count_column = count_column_limited.iterkeys()
        for row in iterator:
            for column_name in count_column:
                if flag_limited:
                    if count_column not in count_column_limited[count_column]:
                        continue
                column_value = row[column_name]
                column_counter = counted.get(column_name, {})
                column_counter[column_value] = column_counter.get(column_value, 0) + 1
                counted[column_name] = column_counter
        self.log('Counted !!!!!')
        return counted

    def aggregated_counter(self, iterator, count_column_limited, aggregate_column):
        counted = {}
        pre_aggregated_column = None
        flag_limited = None
        if isinstance(count_column_limited, list) or isinstance(count_column_limited, set):
            flag_limited = False
            count_column = count_column_limited
        elif isinstance(count_column_limited, dict):
            flag_limited = True
            count_column = count_column_limited.iterkeys()

        for row in iterator:
            # initial first time pre_aggregated_column
            print row['line_number']
            if not pre_aggregated_column:
                pre_aggregated_column = row[aggregate_column]
            if pre_aggregated_column != row[aggregate_column] and counted:
                self.log(counted)
                yield counted, pre_aggregated_column
                counted = {}
                pre_aggregated_column = row[aggregate_column]
            for column_name in count_column:
                if flag_limited:
                    if count_column not in count_column_limited[column_name]:
                        continue
                column_value = row[column_name]
                column_counter = counted.get(column_name, {})
                column_counter[column_value] = column_counter.get(column_value, 0) + 1
                counted[column_name] = column_counter
        else:
            if counted:
                self.log(counted)
                yield counted, pre_aggregated_column

    def find_frequency(self, file_name, result_file_address, count_column_limited, keep_dictionary=None):
        iter_csv = self.iter_csv(file_name=file_name, keep_dictionary=keep_dictionary)
        counted = self.counter(iter_csv, count_column_limited)
        self.write_counted_items(counted, result_file_address)

    def find_frequency_normalized_count(self, file_name, result_file_address, count_column_limited,
                                        aggregate_column, keep_dictionary=None, flag_binary_count_normalized=True,
                                        flag_aggregate_count_normalize=True):
        iter_csv = self.iter_csv(file_name=file_name, keep_dictionary=keep_dictionary)
        counted_binary_normalized = {}
        counted_binary = {}
        counted_aggregate_normalized = {}
        flag_limited = None
        if isinstance(count_column_limited, list) or isinstance(count_column_limited, set):
            flag_limited = False
        elif isinstance(count_column_limited, dict):
            flag_limited = True
        if flag_limited is not None:
            for aggregate_count, _ in self.aggregated_counter(iterator=iter_csv,
                                                              count_column_limited=count_column_limited,
                                                              aggregate_column=aggregate_column):
                StatisticalAnalyzer.normalized_count(aggregate_count, count_column_limited, flag_limited,
                                                     counted_aggregate_normalized, counted_binary,
                                                     counted_binary_normalized, flag_aggregate_count_normalize,
                                                     flag_binary_count_normalized)

        result_file_split = result_file_address.split('.')
        base_file_name = result_file_address
        extension = '.csv'
        if len(result_file_split) > 1:
            base_file_name = '.'.join(result_file_split[0:-1])
            extension = '.' + result_file_split[-1]

        if flag_binary_count_normalized:
            binary_count_normalized_file_name = base_file_name + '_binary_count_normalized' + extension
            binary_count_file_name = base_file_name + '_binary_count' + extension
            self.write_counted_items(counted_binary_normalized, result_file_address=binary_count_normalized_file_name)
            self.write_counted_items(counted_binary, result_file_address=binary_count_file_name)
        if flag_aggregate_count_normalize:
            aggregate_count_normalize_file_name = base_file_name + '_aggregate_count_normalized' + extension
            self.write_counted_items(counted_aggregate_normalized,
                                     result_file_address=aggregate_count_normalize_file_name)

    @staticmethod
    def normalized_count(aggregate_count, count_column_limited, flag_limited, counted_aggregate_normalized,
                         counted_binary, counted_binary_normalized, flag_aggregate_count_normalize,
                         flag_binary_count_normalized):
        if flag_limited:
            count_columns = count_column_limited.iterkeys()
        else:
            count_columns = count_column_limited

        for counted_column_name in count_columns:
            total_tokens = reduce(lambda a, b: int(a) + int(b),
                                  aggregate_count[counted_column_name].itervalues())
            total_tokens_binary = len(aggregate_count[counted_column_name])
            for item, value in aggregate_count[counted_column_name].iteritems():

                # skip is not in limited list
                if flag_limited:
                    if item not in count_column_limited[counted_column_name]:
                        continue

                if flag_binary_count_normalized:
                    counted_column = counted_binary.get(counted_column_name, {})
                    counted_column_normalized = counted_binary_normalized.get(counted_column_name, {})
                    counted_column[item] = counted_column.get(item, 0) + 1
                    counted_column_normalized[item] = counted_column_normalized.get(item, 0) + \
                        1 / float(total_tokens_binary)
                    counted_binary[counted_column_name] = counted_column
                    counted_binary_normalized[counted_column_name] = counted_column_normalized
                if flag_aggregate_count_normalize:
                    counted_column = counted_aggregate_normalized.get(counted_column_name, {})
                    counted_column[item] = counted_aggregate_normalized.get(item, 0) \
                        + int(value) / float(total_tokens)
                    counted_aggregate_normalized[counted_column_name] = counted_column

        return counted_aggregate_normalized, counted_binary, counted_binary_normalized

    def write_counted_items(self, counted, result_file_address):
        with open(result_file_address, self.write_mode) as csv_file:
            column_names_number = sorted(map(lambda k: (k, len(counted[k])), counted.iterkeys()),
                                         key=itemgetter(1), reverse=True)

            header_names = []
            value_label = '_value'
            for column_name in map(lambda p: p[0], column_names_number):
                header_names.append(column_name)
                header_names.append(column_name + value_label)
            writer = csv.DictWriter(csv_file, header_names)
            writer.writeheader()
            if len(column_names_number) > 0:
                i_cnn = column_names_number[0]
                for idx in range(0, i_cnn[1]):
                    dictionary_data = {}
                    for cnn in column_names_number:
                        if idx < cnn[1]:
                            pair = counted[cnn[0]].items()[idx]
                            dictionary_data[cnn[0]] = pair[0]
                            dictionary_data[cnn[0] + value_label] = pair[1]
                    self.log(dictionary_data)
                    writer.writerow(dictionary_data)

    def find_frequency_per_line_aggregated(self, file_name, result_file_address, count_column_limited, aggregate_column,
                                           keep_dictionary=None,
                                           flag_binary_count_normalized=True, flag_aggregate_count_normalize=True):
        iter_csv = self.iter_csv(file_name=file_name, keep_dictionary=keep_dictionary)
        counted = self.counter(iter_csv, count_column_limited)
        base_counted = dict(map(lambda (k, v):
                                (k, dict(map(lambda (ik, iv): (ik, 0), v.iteritems()))),
                                counted.iteritems()))
        for key in list(base_counted.iterkeys()):
            base_counted[key][aggregate_column] = 0

        def update_with_default_value(c, b_c, a_d):
            for ki in list(c.iterkeys()):
                b_c[ki][a_d[0]] = a_d[1]
            for fn, cnt in b_c.iteritems():
                for f, v in cnt.iteritems():
                    if f not in c[fn]:
                        c[fn][f] = v

        iter_csv = self.iter_csv(file_name=file_name, keep_dictionary=keep_dictionary)

        flag_limited = None
        if isinstance(count_column_limited, list) or isinstance(count_column_limited, set):
            flag_limited = False
        elif isinstance(count_column_limited, dict):
            flag_limited = True

        dict_writer_binary_count_normalized = None
        dict_writer_binary_count = None

        if flag_binary_count_normalized:
            dict_writer_binary_count_normalized = self._initial_writer_frequency(
                result_file_address=result_file_address, base_counted=base_counted,
                extension_name='_binary_count_normalized')
            dict_writer_binary_count = self._initial_writer_frequency(
                result_file_address=result_file_address, base_counted=base_counted,
                extension_name='_binary_count')

        dict_writer_aggregate_count = None
        if flag_aggregate_count_normalize:
            dict_writer_aggregate_count = self._initial_writer_frequency(
                result_file_address=result_file_address, base_counted=base_counted,
                extension_name='_aggregate_count')
        dict_writer = self._initial_writer_frequency(
            result_file_address=result_file_address, base_counted=base_counted,
            extension_name='')
        if flag_limited is not None:
            for aggregate_count, aggregate_column_value in self.aggregated_counter(
                    iterator=iter_csv, count_column_limited=count_column_limited, aggregate_column=aggregate_column):
                print '*********************'
                print aggregate_column_value
                print '*********************'
                counted_binary_normalized = None
                counted_binary = None
                counted_aggregate_normalized = None
                amended_column = (aggregate_column, aggregate_column_value)
                if flag_binary_count_normalized or flag_aggregate_count_normalize:
                    counted_binary_normalized = {}
                    counted_binary = {}
                    counted_aggregate_normalized = {}
                    StatisticalAnalyzer.normalized_count(aggregate_count, count_column_limited, flag_limited,
                                                         counted_aggregate_normalized, counted_binary,
                                                         counted_binary_normalized, flag_aggregate_count_normalize,
                                                         flag_binary_count_normalized)

                for category_name in base_counted.iterkeys():
                    update_with_default_value(aggregate_count, base_counted, amended_column)
                    dict_writer[category_name].send(aggregate_count[category_name])
                    if flag_binary_count_normalized:
                        update_with_default_value(counted_binary, base_counted, amended_column)
                        dict_writer_binary_count[category_name].send(counted_binary[category_name])
                        update_with_default_value(counted_binary_normalized, base_counted, amended_column)
                        dict_writer_binary_count_normalized[category_name].send(
                            counted_binary_normalized[category_name])
                    if flag_aggregate_count_normalize:
                        update_with_default_value(counted_aggregate_normalized, base_counted, amended_column)
                        dict_writer_aggregate_count[category_name].send(counted_aggregate_normalized[category_name])

            for category_name in base_counted.iterkeys():
                dict_writer[category_name].close()
                if flag_binary_count_normalized:
                    dict_writer_binary_count[category_name].close()
                    dict_writer_binary_count_normalized[category_name].close()
                if flag_aggregate_count_normalize:
                    dict_writer_aggregate_count[category_name].close()

    def _initial_writer_frequency(self, result_file_address, base_counted, extension_name):
        result_file_split = result_file_address.split('.')
        base_file_name = result_file_address
        extension = '.csv'
        if len(result_file_split) > 1:
            base_file_name = '.'.join(result_file_split[0:-1])
            extension = '.' + result_file_split[-1]
        dictionary_writers = {}

        for category_name, counted_items in base_counted.iteritems():
            file_name = base_file_name + '_' + category_name + '_' + extension_name + extension
            dictionary_writers[category_name] = self.writer_frequency_aggregated(
                file_name,
                list(counted_items.iterkeys()))
        return dictionary_writers

    @co_routine
    def writer_frequency_aggregated(self, result_file_address, header_names):
        try:
            with open(result_file_address, self.write_mode) as csv_file:
                writer = csv.DictWriter(csv_file, header_names)
                writer.writeheader()
                while True:
                    dictionary_data = (yield)
                    writer.writerow(dictionary_data)
        except GeneratorExit:
            pass

    def find_frequency_sub_group(self, file_name, result_file_address, group_column,
                                 count_sub_column, keep_dictionary=None, count_sub_exception=None):
        except_dictionary = None
        if count_sub_exception:
            except_dictionary = {count_sub_column: count_sub_exception}

        iter_csv = self.iter_csv(file_name=file_name, keep_dictionary=keep_dictionary,
                                 except_dictionary=except_dictionary)
        counted = self.counter(iter_csv, count_column_limited=[group_column])
        print('All counted')

        split_file_name = result_file_address.split('.')
        if len(file_name) != 0:
            base_file_name = split_file_name[-2] + '_'
        else:
            base_file_name = file_name + '_'

        for counted_item in counted[group_column].iterkeys():
            keep_dictionary[group_column] = counted_item
            iter_csv = self.iter_csv(file_name=file_name, keep_dictionary=keep_dictionary,
                                     except_dictionary=except_dictionary)
            sub_column_counted = self.counter(iter_csv, count_column_limited=[count_sub_column])
            self.write_counted_items(sub_column_counted, result_file_address=base_file_name + counted_item + '.csv')
            print(counted_item + ' finished !!!')
        print('All processed !!!')

    def fix_time_format(self, file_name, result_file_address):
        keep_dictionary = None
        except_dictionary = None
        iter_csv = self.iter_csv(file_name=file_name, keep_dictionary=keep_dictionary,
                                 except_dictionary=except_dictionary)
        with open(result_file_address, self.write_mode) as csv_file:
            row = iter_csv.next()
            header_names = list(row.iterkeys())
            header_names.append('h')
            writer = csv.DictWriter(csv_file, header_names)
            writer.writeheader()
            data = datetime.strptime(row['authored_date'], '%a %b %d %X %Y')
            off_set_time = datetime.strptime(row['authored_time_zone_offset'], '%H:%M').time()
            d = datetime.combine(date.today(), data.time()) - datetime.combine(date.today(), off_set_time)
            row['h'] = d.seconds//3600
            writer.writerow(row)
            for row in iter_csv:
                print row['authored_time_zone_offset']
                print row['authored_date']

                data = datetime.strptime(row['authored_date'], '%a %b %d %X %Y')
                off_set_time = datetime.strptime(row['authored_time_zone_offset'], '%H:%M').time()
                # print off_set_time
                d = datetime.combine(date.today(), data.time()) - datetime.combine(date.today(), off_set_time)
                row['h'] = d.seconds // 3600
                writer.writerow(row)

    def generate_change_on_not_fixed_files(self, file_address_all_changed, file_address_all_fixed,
                                           result_file_address):

        keep_dictionary = None
        except_dictionary = None
        field_name_file = 'path'
        set_all_fixed_files = set()

        fixed_iter_csv = self.iter_csv(file_name=file_address_all_fixed,
                                       keep_dictionary=keep_dictionary,
                                       except_dictionary=except_dictionary)
        for row in fixed_iter_csv:
            set_all_fixed_files.add(row[field_name_file].strip())

        all_changed_iter_csv = self.iter_csv(file_name=file_address_all_changed,
                                             keep_dictionary=keep_dictionary,
                                             except_dictionary=except_dictionary)

        with open(result_file_address, self.write_mode) as csv_file:
            row = all_changed_iter_csv.next()
            header_names = list(row.iterkeys())
            writer = csv.DictWriter(csv_file, header_names)
            writer.writeheader()
            if row[field_name_file].strip() in set_all_fixed_files:
                writer.writerow(row)
            for row in all_changed_iter_csv:
                if row[field_name_file].strip() not in set_all_fixed_files:
                    writer.writerow(row)




