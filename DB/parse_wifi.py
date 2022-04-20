import re
import argparse
import json
import requests
import urllib.request
import os
import time
import sys


API = "https://apicactus.herokuapp.com"  # remote
# API = "http://localhost:5000"  # local


# finds the position of frame
def gather_all_frames(data: str, search_string: str):
    iterator = re.finditer(search_string, data)
    arr = []
    try:
        start, _ = next(iterator).span()
        for i in iterator:
            stop, _ = i.span()
            arr.append(data[start: stop])  # packet info
            start = stop
    except:
        pass

    return arr

# given a frame, find all the data containing `search_string`


def ind_packet_data(data, search_string, end_string=None):
    pos = data.find(search_string)
    if pos >= 0:
        e = pos + data[pos:].find(end_string) if end_string else -1
        return data[len(search_string) + pos:e].strip()
    return None


def parse_data(data, file_creation_time: int):
    """ Gathers request_to_send, clear_to_send data, signal strength, authentication"""
    frames = gather_all_frames(data, "Frame \d+")

    # parse request-to-send and generate dict
    request_to_send_headers = [ind_packet_data(
        frame, "Request-to-send") for frame in frames]

    rts_dict = []

    # get source/dst addr for all rts header
    for header in request_to_send_headers:
        if not header:
            rts_dict.append({"source": None, "destination": None})
            continue
        source = ind_packet_data(header, "Receiver address:", "\n")
        destination = ind_packet_data(header, "Transmitter address:", "\n")
        rts_dict.append({"source": source, "destination": destination})

    # parse clear-to-send and generate dict
    clear_to_send_headers = [ind_packet_data(
        frame, "Clear-to-send") for frame in frames]

    cts_dict = []

    # get source addr for all cts header
    for header in clear_to_send_headers:
        if not header:
            cts_dict.append({"source": None})
            continue
        source = ind_packet_data(header, "Receiver address:", "\n")
        cts_dict.append({"source": source})

    # frame signal strength
    radio_headers = [ind_packet_data(
        frame, "802.11 radio information") for frame in frames]

    signal_strength = []

    # get signal_strength info
    for header in radio_headers:
        if not header:
            signal_strength.append({"signal_strength": None})
            continue

        ss = ind_packet_data(header, "Signal strength (dBm):", "\n")
        signal_strength.append({"signal_strength": ss})

    # get authentication and BSS id info
    authentication_header = [ind_packet_data(
        frame, "IEEE 802.11 Authentication") for frame in frames]

    auth_dict = []

    # get signal_strength info
    for header in authentication_header:
        if not header:
            auth_dict.append(
                {"source": None, "destination": None, "BSS": None})
            continue

        s = ind_packet_data(header, "Receiver address:", "\n")
        d = ind_packet_data(header, "Transmitter address:", "\n")
        bss = ind_packet_data(header, "BSS Id:", "\n")
        auth_dict.append({"source": s, "destination": d, "BSS": bss})

    # get channel frequency
    channel_frequency = ind_packet_data(
        frames[0], "Channel frequency:", "\n")

    final_table = {
        "data":
            {
                "request_to_send": rts_dict,
                "clear_to_send": cts_dict,
                "signal_strength": signal_strength,
                "auth": auth_dict,
                "_timestamp": file_creation_time,
                "channel_frequency": channel_frequency
            },
        "type": "wifi"
    }

    return final_table

# create a function that sees if a file has been added into a directory, and if so, calls the parse_data function and immediately delte the file from the folder.


def push_file_to_backup(file_name: str, parsed_data: dict):
    # create directory backup_folder if it does not exist
    backup_folder = "/".join(file_name.split("/")[:-1]) + "/"
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    with open(file_name + ".json", "w") as f:
        json.dump(parsed_data, f, indent=4)


def live_feed(folder_name: str, backup_folder: str):
    # if folder_name doesnt end with /, add it
    if not folder_name.endswith("/"):
        folder_name += "/"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
    if not backup_folder.endswith("/"):
        backup_folder += "/"

    # get the files in the folder
    files = [folder_name + x for x in os.listdir(folder_name)]
    files = sorted(files,
                   key=os.path.getmtime, reverse=True)
    # if there are files in the folder
    if files:
        # for each file in the folder
        for file in files:
            time.sleep(1)  # delay to ensure files aren't skipped
            # open the file
            if os.stat(file).st_size == 0:
                print("File is empty, deleting...", file=sys.stderr)
                os.remove(file)
                continue  # empty file

            with open(file, "r") as f:
                backup_file_name = backup_folder + file.split("/")[-1]
                # read the file
                data = f.read()
                # parse the data
                parsed_data = parse_data(data, os.path.getctime(file))
                # replace `file_creation_time` with file.split("/")[-1]

                if not connect():
                    push_file_to_backup(backup_file_name, parsed_data)
                else:
                    #  send a post request to the server with the txt file
                    response = requests.post(
                        API + "/api/sniff", json=parsed_data)
                    if response.status_code != 200:
                        print(
                            "Server push failed! Uploading to backup folder...", file=sys.stderr)
                        push_file_to_backup(backup_file_name, parsed_data)
                    else:
                        print("Successfully sent data to server!", file=sys.stderr)

                # delete the file
                os.remove(file)


def connect(host=API):
    """ Function that checks if the internet is connected and access to API """
    try:
        urllib.request.urlopen(host)  # Python 3.x
        return True
    except:
        return False


def backup_process(backup_folder: str):
    if not backup_folder.endswith("/"):
        backup_folder += "/"

    # check if connected to the internet
    if connect() and os.path.exists(backup_folder):
        # get all the files in the backup folder and send a post request
        files = [backup_folder + x for x in os.listdir(backup_folder)]
        files = sorted(files,
                       key=os.path.getmtime, reverse=True)
        for file in files:
            time.sleep(1)  # delay to ensure files aren't skipped
            with open(file, "r") as f:
                data = json.loads(f.read())
                response = requests.post(
                    API + "/api/sniff", json=data)
                if response.status_code == 200:
                    print("Successfully sent backup file to server!",
                          file=sys.stderr)
                    os.remove(file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--folder", help="folder to add hook on", default="DB/capture/wifi")

    parser.add_argument(
        "-b", "--backup_folder", help="backup folder to add hook on", default="DB/backup/wifi")
    args = parser.parse_args()

    BACKUP_TIMELOG = 20  # calls the backup process every X seconds

    start = time.time()

    while True:
        try:
            live_feed(args.folder, args.backup_folder)
            time.sleep(1)
            # call the backup process every X seconds
            if time.time() - start > BACKUP_TIMELOG:
                backup_process(args.backup_folder)
                start = time.time()
        except:
            print("Something bad WiiFi!")
