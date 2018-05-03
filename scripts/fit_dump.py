from fitparse import FitFile
import json, datetime

# INPUT / OUTPUT SETTINGS
FIT_FILE_FP = "2018-03-28-16-43-17.fit"
OUTPUT_DIR = "fit_out"


def run(infile, outpath):
    fitdata = FitFile(infile)

    fields = []
    data = []

    msg = fitdata.get_messages()

    msg_flags = {"0": "file_id", "1": "capabilities", "2": "device_settings", "3": "user_profile", "4": "hrm_profile", "5": "sdm_profile", "6": "bike_profile", "7": "zones_target", "8": "hr_zone", "9": "power_zone", "10": "met_zone", "12": "sport", "15": "goal", "18": "session", "19": "lap", "20": "record", "21": "event", "23": "device_info", "26": "workout", "27": "workout_step", "28": "schedule", "30": "weight_scale", "31": "course", "32": "course_point", "33": "totals", "34": "activity", "35": "software", "37": "file_capabilities", "38": "mesg_capabilities", "39": "field_capabilities", "49": "file_creator", "51": "blood_pressure", "53": "speed_zone", "55": "monitoring", "72": "training_file", "78": "hrv", "80": "ant_rx", "81": "ant_tx", "82": "ant_channel_id", "101": "length", "103": "monitoring_info", "105": "pad", "106": "slave_device", "127": "connectivity", "128": "weather_conditions", "129": "weather_alert", "131": "cadence_zone", "132": "hr", "142": "segment_lap", "145": "memo_glob", "148": "segment_id", "149": "segment_leaderboard_entry", "150": "segment_point", "151": "segment_file", "158": "workout_session", "159": "watchface_settings", "160": "gps_metadata", "161": "camera_event", "162": "timestamp_correlation", "164": "gyroscope_data", "165": "accelerometer_data", "167": "three_d_sensor_calibration", "169": "video_frame", "174": "obdii_data", "177": "nmea_sentence", "178": "aviation_attitude", "184": "video", "185": "video_title", "186": "video_description", "187": "video_clip", "188": "ohr_settings", "200": "exd_screen_configuration", "201": "exd_data_field_configuration", "202": "exd_data_concept_configuration", "206": "field_description", "207": "developer_data_id", "208": "magnetometer_data", "209": "barometer_data", "210": "one_d_sensor_calibration", "225": "set", "227": "stress_level", "258": "dive_settings", "259": "dive_gas", "262": "dive_alarm", "264": "exercise_title", "268": "dive_summary"}

    for m in msg:
        m_name = m.name
        if "unknown" in m_name:
            try:
                m_name = msg_flags[str(m.mesg_num)]
            except:
                pass
        # print m.name, m.mesg_num, m.mesg_type
        if m_name not in fields:
            fields.append(m_name)
            data.append([])
        idx = fields.index(m_name)

        data[idx].append(m.get_values())

    for i in xrange(len(fields)):
        outfile = "{}/{}.json".format(outpath, fields[i])

        f = open(outfile,mode='w')
        try:
            json.dump(data[i], f, sort_keys=True, indent=4, separators=(',',':'), default=str)
        except:
            print("ERROR")
            print(data[i])
        f.close()

if __name__ == "__main__":
    run(FIT_FILE_FP, OUTPUT_DIR)
