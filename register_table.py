# -*- coding: utf-8 -*-
"""
Created on Tue May 19 15:46:35 2020

@author: jidong
"""

import mysql.connector
import pandas as pd
from sqlalchemy import create_engine

class competition_register(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cnx = mysql.connector.connect(user = self.username, password = self.password, 
                                  host = '127.0.0.1', database = 'grmds054_drup881')
        
    def load_data(self):
        db_cursor = self.cnx.cursor()
        db_cursor.execute('SHOW columns FROM dr_webform_submission_data')
        column_names = [column[0] for column in db_cursor.fetchall()]
        db_cursor.execute("select * from dr_webform_submission_data where webform_id = '2020_ds_competition_registration'")
        wholetable = pd.DataFrame(columns = column_names)
        for tuples in db_cursor:
            dic = dict(zip(column_names, list(tuples)))
            wholetable = wholetable.append(dic,ignore_index = True)           
        self.cnx.close()
        
        return wholetable,column_names
                
    def process_data(self):
        data, columns = self.load_data()
        data.drop(columns=['webform_id'], inplace = True)
        grouped = data.groupby('sid')
        columns_list = ['sid','team_name','email','email_is_primary_y_n',
                        'full_name','mentor_full_name',
                        'mentor_email','need_mentor_y_n','need_team_y_n']
        table = pd.DataFrame(columns = columns_list)
        for group_name, group in grouped:
            sid = group_name
            email_pri = group[group['name'] == 'email_primary'].iloc[0]['value']
            mentor_email = group[group['name'] == 'mentor_email'].iloc[0]['value']
            mentor_name = group[group['name'] == 'mentor_name'].iloc[0]['value']
            need_mentor = group[group['name'] == 'need_mentor'].iloc[0]['value']
            need_team = group[group['name'] == 'need_team'].iloc[0]['value']
            team_name = group[group['name'] == 'team_name'].iloc[0]['value']
            dic = dict(zip(columns_list, [sid, team_name, email_pri, 1, '', mentor_name, mentor_email, need_mentor, need_team]))
            table = table.append(dic, ignore_index = True)            
            for _,group2 in group[group['name'] == 'member'].groupby('delta'):
                mem_name = group2[group2['property'] == 'member_name'].iloc[0]['value']
                mem_email = group2[group2['property'] == 'member_email'].iloc[0]['value']
                dic = dict(zip(columns_list, [sid, team_name, mem_email, 0, mem_name, mentor_name, mentor_email, need_mentor, need_team]))
                table = table.append(dic, ignore_index = True)
        return table

    def upload_table(self):
        data = self.process_data()
        engine = create_engine('mysql+mysqlconnector://grmds_analyst:Cmethods1@54.189.68.146/grmds054_drup881',echo=True)
        data.to_sql(name='dr_2020_ds_competition_registration', con=engine, if_exists = 'replace', index=False)
        return 





if __name__ == "__main__":
    x = competition_register('grmds_analyst','Cmethods1')
    x.upload_table()