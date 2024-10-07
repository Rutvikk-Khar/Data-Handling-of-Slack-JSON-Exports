import os
import json
import pandas as pd
exportname = "channel_name_here"        #Insert the Channel Name here
working_directory = os.getcwd()
slackexport_folder_path = f"{working_directory}/{exportname}"

channels_path = f"{slackexport_folder_path}/channels.json"
with open(channels_path, encoding='utf-8') as f:
    channels_json = json.load(f)

channel_list = pd.DataFrame(columns=["ch_id", "name", "created", "creator", "is_archived",
                                     "is_general", "members", "topic", "purpose"])

for channel in range(len(channels_json)):
    channel_list.at[channel, "ch_id"] = channels_json[channel]['id']
    channel_list.at[channel, "name"] = channels_json[channel]['name']
    channel_list.at[channel, "created"] = channels_json[channel]['created']
    channel_list.at[channel, "creator"] = channels_json[channel]['creator']
    channel_list.at[channel, "is_archived"] = channels_json[channel]['is_archived']
    channel_list.at[channel, "is_general"] = channels_json[channel]['is_general']
    memberlist = ", ".join(channels_json[channel]['members'])
    channel_list.at[channel, "members"] = memberlist
    channel_list.at[channel, "topic"] = channels_json[channel]['topic']['value']
    channel_list.at[channel, "purpose"] = channels_json[channel]['purpose']['value']

    channel_folder_path = f"{slackexport_folder_path}/{channel_list.at[channel, 'name']}"
    channels_json[channel]['dayslist'] = os.listdir(channel_folder_path)

def slack_json_to_dataframe(slack_json):
    messages_df = pd.DataFrame(columns=["msg_id", "ts", "user", "type", "text", "reply_count",
                                         "reply_users_count", "ts_latest_reply", "ts_thread", 
                                         "parent_user_id"])
    for message in range(len(slack_json)):
        if 'files' in slack_json[message] and slack_json[message]['files']:
            messages_df.at[message, "msg_id"] = slack_json[message]['files'][0]['id']
        elif 'client_msg_id' in slack_json[message]:
            messages_df.at[message, "msg_id"] = slack_json[message]['client_msg_id']
        if 'ts' in slack_json[message]:
            messages_df.at[message, "ts"] = slack_json[message]['ts']
        else:
            messages_df.at[message, "ts"] = None
        messages_df.at[message, "user"] = slack_json[message].get('user', None)
        if 'type' in slack_json[message]:
            messages_df.at[message, "type"] = slack_json[message]['type']
        else:
            messages_df.at[message, "type"] = None
        
        if 'text' in slack_json[message]:
            messages_df.at[message, "text"] = slack_json[message]['text']
        else:
            messages_df.at[message, "text"] = None
        if 'reply_count' in slack_json[message]:
            messages_df.at[message, "reply_count"] = slack_json[message]['reply_count']
            messages_df.at[message, "reply_users_count"] = slack_json[message]['reply_users_count']
            messages_df.at[message, "ts_latest_reply"] = slack_json[message]['latest_reply']
        if 'parent_user_id' in slack_json[message]:
            messages_df.at[message, "ts_thread"] = slack_json[message]['thread_ts']
            messages_df.at[message, "parent_user_id"] = slack_json[message]['parent_user_id']
    return messages_df

all_channels_all_files_df = pd.DataFrame(columns=["msg_id", "ts", "user", "type", "text",
                                                  "reply_count", "reply_users_count", 
                                                  "ts_latest_reply", "ts_thread", "parent_user_id", 
                                                  "channel"])

for channel in range(len(channels_json)):
    all_channel_files_df = pd.DataFrame(columns=["msg_id", "ts", "user", "type", "text",
                                                 "reply_count", "reply_users_count", 
                                                 "ts_latest_reply", "ts_thread", "parent_user_id"])

    for file_day in range(len(channels_json[channel]['dayslist'])):
        parentfolder_path = f"{slackexport_folder_path}/{channels_json[channel]['name']}"
        filejson_path = f"{parentfolder_path}/{channels_json[channel]['dayslist'][file_day]}"
        with open(filejson_path, encoding='utf-8') as f:
            import_file_json = json.load(f)
        import_file_df = slack_json_to_dataframe(import_file_json)
        all_channel_files_df = pd.concat([all_channel_files_df, import_file_df], ignore_index=True)

    all_channel_files_df['channel'] = channels_json[channel]['name']
    all_channels_all_files_df = pd.concat([all_channels_all_files_df, all_channel_files_df], ignore_index=True)

filename_mindate = pd.to_datetime(all_channels_all_files_df['ts'], unit='s').min().date()
filename_maxdate = pd.to_datetime(all_channels_all_files_df['ts'], unit='s').max().date()
slack_export_df_filename = f"{exportname}_{filename_mindate}_to_{filename_maxdate}.csv"
all_channels_all_files_df.to_csv(slack_export_df_filename, index=False)

users_path = f"{slackexport_folder_path}/users.json"
with open(users_path, encoding='utf-8') as f:
    users_json = json.load(f)

user_list_df = pd.DataFrame(columns=["user_id", "team_id", "name", "deleted", "real_name",
                                      "tz", "tz_label", "tz_offset", "title", "display_name", 
                                      "is_bot"])

for user in range(len(users_json)):
    user_list_df.at[user, "user_id"] = users_json[user]['id']
    user_list_df.at[user, "team_id"] = users_json[user]['team_id']
    user_list_df.at[user, "name"] = users_json[user]['name']
    user_list_df.at[user, "deleted"] = users_json[user]['deleted']
    user_list_df.at[user, "real_name"] = users_json[user].get('real_name', None)
    user_list_df.at[user, "title"] = users_json[user]['profile']['title']
    user_list_df.at[user, "display_name"] = users_json[user]['profile']['display_name']
    user_list_df.at[user, "is_bot"] = users_json[user]['is_bot']
    user_list_df.at[user, "tz"] = users_json[user].get('tz', None)
    user_list_df.at[user, "tz_label"] = users_json[user].get('tz_label', None)
    user_list_df.at[user, "tz_offset"] = users_json[user].get('tz_offset', None)

slack_export_user_filename = f"{exportname}_users.csv"
user_list_df.to_csv(slack_export_user_filename, index=False)
slack_export_channel_filename = f"{exportname}_channels.csv"
channel_list.to_csv(slack_export_channel_filename, index=False)
