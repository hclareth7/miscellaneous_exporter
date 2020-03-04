import logging
import os
import shlex
import stat
import subprocess
import multiprocessing
import sys
import yaml
import time

from prometheus_client import start_http_server
from prometheus_client.core import (GaugeMetricFamily,
                                    CounterMetricFamily,
                                    SummaryMetricFamily,
                                    HistogramMetricFamily,
                                    REGISTRY)

logging.basicConfig(level=logging.DEBUG)
DEBUG = int(os.environ.get('DEBUG', '0'))
VIRTUAL_PORT = int(os.environ.get('VIRTUAL_PORT', '9797'))


class Util(object):
    metrics_path = 'metrics'
    @classmethod
    def get_dir_list(cls):
        dirs = [
            f'{cls.metrics_path}/{file}' for file in os.listdir(cls.metrics_path)]
        return dirs

    @classmethod
    def get_dir_tuple(cls):
        dirs = []
        for file in os.listdir(cls.metrics_path):
            file_tuple = (f'{cls.metrics_path}/{file}',)
            dirs.append(file_tuple)
        return dirs

    @classmethod
    def _set_lang_to_file(cls, file):
        file_extention = file.split('.')[1]
        result = f"{cls._get_lang_by_file_extension(file_extention)} {file}"
        return result

    @classmethod
    def _get_lang_by_file_extension(cls, extension):
        if extension == 'py':
            return 'python'
        elif extension == 'sh':
            return 'bash'

        else:
            logging.debug(f'the extension {extension} is not supported.')

    @classmethod
    def set_as_executable_files(cls, files):
        for file in files:
            try:
                st = os.stat(file)
                os.chmod(file, st.st_mode | stat.S_IEXEC)
            except Exception as error:
                logging.debug(
                    f'Error making executable the file {file}, error: {error}')

    @classmethod
    def exec_files(cls, file):
        try:
            command = shlex.split(f"{cls._set_lang_to_file(file)}")
            proc = subprocess.Popen(command, stdout=subprocess.PIPE)
            metrics = yaml.safe_load(proc.stdout)
            proc.communicate()
            return metrics['metrics']
        except Exception as error:
            logging.debug(f'Error executing the file {file}, error: {error}')

    @classmethod
    def multiprocessing_funct(cls, func, arg_list=()):
        try:
            data = []
            pool = multiprocessing.Pool(len(arg_list))
            results = pool.starmap(func, arg_list)
            for resul in results:
                for metric in results:
                    data.extend(metric)
            return data
        except Exception as error:
            logging.debug(
                f'Error executing multiprocessing thread, error: {error}')


class MiscellaneousCollector(object):
    def __init__(self):
        super(MiscellaneousCollector, self).__init__()
        self.metric_prefix = 'miscellaneous_metric_'
        self.files = Util.get_dir_list()
        self.tuple_files = Util.get_dir_tuple()
        Util.set_as_executable_files(self.files)

    def collect(self):
        logging.debug(f'Starting to collect metrics')
        metrics_data = Util.multiprocessing_funct(
            func=Util.exec_files, arg_list=self.tuple_files)
        self._set_up_metrics(metrics_data)
        self._get_metrics(metrics_data)

        for metric in self._prometheus_metrics.values():
            yield metric

    def _set_up_metrics(self, metrics_data):
        logging.debug(f'Configuring metrics')
        self._prometheus_metrics = {}
        for metric in metrics_data:
            labels = []
            for label in metric['labels']:
                labels.append(str(label['label']))
            if metric['type'] == 'gauge':
                self._prometheus_metrics[f"{self.metric_prefix}{metric['metric']}"] = GaugeMetricFamily(f"{self.metric_prefix}{metric['metric']}",
                                                                                                        f"{metric['description']}",
                                                                                                        labels=labels)
            elif metric['type'] == 'counter':
                self._prometheus_metrics[f"{self.metric_prefix}{metric['metric']}"] = CounterMetricFamily(f"{self.metric_prefix}{metric['metric']}",
                                                                                                          f"{metric['description']}",
                                                                                                          labels=labels)
            elif metric['type'] == 'histogram':
                self._prometheus_metrics[f"{self.metric_prefix}{metric['metric']}"] = HistogramMetricFamily(f"{self.metric_prefix}{metric['metric']}",
                                                                                                            f"{metric['description']}",
                                                                                                            labels=labels)
            elif metric['type'] == 'summary':
                self._prometheus_metrics[f"{self.metric_prefix}{metric['metric']}"] = SummaryMetricFamily(f"{self.metric_prefix}{metric['metric']}",
                                                                                                          f"{metric['description']}",
                                                                                                          labels=labels)
            else:
                logging.debug(
                    f"The type of metric {metric['type']} is not supported")

    def _get_metrics(self, metrics_result):
        for metric in metrics_result:
            labels = []
            for label in metric['labels']:
                labels.append(str(label['value']))
            self._prometheus_metrics[f"{self.metric_prefix}{metric['metric']}"].add_metric(
                labels, metric['value'])


def main():
    try:
        REGISTRY.register(MiscellaneousCollector())
        start_http_server(VIRTUAL_PORT)
        logging.debug(
            f"Polling http://0.0.0.0:{VIRTUAL_PORT}/metrics. Serving at port: {VIRTUAL_PORT}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.debug("\nInterrupted")
        exit(0)


if __name__ == "__main__":
    main()
