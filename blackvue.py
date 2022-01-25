import uuid
from datetime import datetime
from tempfile import TemporaryDirectory

import blackclue
import hansken.util
import pytz
from blackvue_gps import parse_blackvue_nmea
from hansken_extraction_plugin.api.extraction_plugin import ExtractionPlugin
from hansken_extraction_plugin.api.plugin_info import Author, MaturityLevel, PluginInfo, PluginId, PluginResources
from hansken_extraction_plugin.runtime.extraction_plugin_runner import run_with_hanskenpy
from logbook import Logger

log = Logger(__name__)


class BlackVue(ExtractionPlugin):

    def plugin_info(self):
        log.info('pluginInfo request')
        plugin_info = PluginInfo(
            self,
            id=PluginId(domain='nfi.nl', category='media', name='BlackVue'),
            version='2022.1.25',
            description='BlackVue GPS parser for Hansken',
            author=Author('FBDA', 'fbda@nfi.nl', 'NFI'),
            maturity=MaturityLevel.PROOF_OF_CONCEPT,
            webpage_url='https://hansken.org',
            # matcher="file.extension=mp4 pittasoft AND $data.type=raw",
            matcher="file.extension=mp4 AND $data.type=raw",
            license="Apache License 2.0",
            resources=PluginResources.builder().maximum_cpu(1).maximum_memory(2048).build(),
        )
        log.debug(f'returning plugin info: {plugin_info}')
        return plugin_info

    def process(self, trace, data_context):
        """

        :param trace: expected to be a BlackVue dashcam recording
        :param data_context: data_context
        """
        log.info(f"processing trace {trace.get('name')}")
        with TemporaryDirectory() as temporary_directory:
            # Try to read in the fragment that we are going to process and store it temporarily
            temporary_file = f'{temporary_directory}/{str(uuid.uuid4())}.mp4'
            with open(temporary_file, 'wb') as temporary_inputfragment:
                temporary_inputfragment.write(trace.open().read(data_context.data_size()))
            blackclue.dump([temporary_file], True, True, True, True)
            gps_records = parse_blackvue_nmea(temporary_file)
            for i, record in enumerate(gps_records):
                child_trace = trace.child_builder(f'GPS point {i} in {trace.get("name")}')
                child_trace.update('gps.createdOn', datetime.fromtimestamp(int(record.unix_ms) / 1000, tz=pytz.utc))  # TODO actual timezone if possible
                child_trace.update('gps.latlong', hansken.util.GeographicLocation(record.lat, record.lon))
                child_trace.build()


if __name__ == '__main__':
    run_with_hanskenpy(BlackVue)
