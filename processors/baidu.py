from processors import BaseProcessor
from mongo import get_mongodb

__author__ = 'zephyre'


class BaiduPoiProcessor(BaseProcessor):
    name = 'baidu-poi'

    def __init__(self, *args, **kwargs):
        BaseProcessor.__init__(self, *args, **kwargs)

        self.args = self.args_builder()

    def args_builder(self):
        parser = self.arg_parser
        parser.add_argument('--limit', default=None, type=int)
        parser.add_argument('--skip', default=0, type=int)
        return parser.parse_args()

    def run(self):
        BaseProcessor.run(self)

        col = get_mongodb('poi', 'ViewSpot', profile='mongo')
        col_raw = get_mongodb('raw_baidu', 'BaiduPoi', profile='mongo-raw')

        cursor = col_raw.find({'tips': {'$ne': None}}, {'tips': 1, 'sid': 1, 'sname': 1})
        cursor.skip(self.args.skip)
        if self.args.limit:
            cursor.limit(self.args.limit)

        for entry in cursor:
            tips = []
            for item in entry['tips']:
                title = item['title']
                desc = '<div>%s</div>' % item['contents']
                tips.append({'title': title, 'desc': desc})

            self.log('Updating: sid: %s, sname: %s...' % (entry['sid'], entry['sname']))
            col.update({'source.baidu.id': entry['sid']}, {'$set': {'tips': tips}})
