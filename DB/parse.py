import re
import argparse
import json
import requests

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


def parse_data(data):
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

    final_table = {
        "request_to_send": rts_dict,
        "clear_to_send": cts_dict,
        "signal_strength": signal_strength,
        "auth": auth_dict
    }
    return final_table


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="file to parse", required=True)
    args = parser.parse_args()

    file = open(args.file)
    data = file.read()
    final_table = parse_data(data)

    # save final_table to json file with same name as input file
    file_name = args.file.split(".")[0]
    with open(file_name + ".json", "w") as f:
        json.dump(final_table, f, indent=4)

    #  send a post request to the server with the txt file
    response = requests.post(
        "https://apicactus.herokuapp.com/api/sniff", json=final_table)
    print(response.text)
