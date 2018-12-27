from collections import OrderedDict
from simple_salesforce import Salesforce
import pandas as pd
import json
import requests

import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
            

class SfReportsApi(Salesforce):
    def __init__(self, *args, **kwargs):
        super(SfReportsApi, self).__init__(*args, **kwargs)

    def describe_report(self, report_id):
        return self._call_report(report_id, command='/describe')

    def detail_to_df(self, report_id, metadata=None):
        """SF report details exported to DataFrame, can be modified by metadata"""
        with requests.session() as s:
            d = s.get("https://efec.my.salesforce.com/{}?export=1&enc=UTF-8&xf=csv".format(report_id), 
                      headers=self.headers, 
                      cookies={'sid': self.session_id})
        return pd.read_csv(StringIO(d.text), sep=",")
    
    def matrix_to_df(self, report_id, metadata=None):
        """SF report matrix exported to DataFrame, can be modified by metadata"""
        
        resp = self._call_report(report_id, metadata=metadata)
        col_list,col_header = self._get_col_idx('groupingsAcross',resp)
        col_header.reverse()
        row_list,row_header = self._get_col_idx('groupingsDown',resp)
        
        data_list = []
        for r in row_list:
            for c in col_list:
                data_list.append(r[0]+c[0]+[resp['factMap'][r[1]+'!'+c[1]]['aggregates'][0]['value']])
        unindexed_header = row_header+col_header+['value']
        df_unindexed = pd.DataFrame(data_list,columns=unindexed_header)
        df = df_unindexed.set_index(unindexed_header[:-1])
        if len(col_header) == 2:
            df = df.unstack(2).unstack().fillna(0)
        else:
            df = df.unstack().fillna(0)
        return df

    def _call_report(self, report_id, metadata=None, command=None):
        url = '{}analytics/reports/{}{}'.format(self.base_url, report_id, command or '')
        data = json.dumps({'reportMetadata': metadata}) if metadata else None
        resp = self._call_salesforce('POST' if metadata else 'GET', url, data=data)
        return resp.json(object_pairs_hook=OrderedDict)
    
    def _get_col_idx(self,gtype,resp):
        idx_list = []
        for a0 in resp[gtype]['groupings']:
            if len(a0['groupings'])==0:
                idx_list.append(([a0['label']],a0['key']))
            else:
                for a1 in a0['groupings']:
                    idx_list.append(([a0['label'],a1['label']],a1['key']))
        unstack_header = []
        for i in range(0,len(metadata[gtype])):
            unstack_header.append(metadata[gtype][i]['name'])
        return idx_list,unstack_header
