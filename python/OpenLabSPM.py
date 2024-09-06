import socket
import numpy as np
import os
import re
import struct

class Client:
    def __init__(self, port=8070, ip='127.0.0.1'):
        """Constructor

        :param port: Specifies the port number of the server
        :param ip: Specifies the IP Address of the server
        """
        self._server = ip
        self._port = port
        
    def send(self, command_str):
        self._connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect.connect((self._server, self._port))        
        command = command_str.encode(encoding='utf-8')
        length = len(command)
        self._connect.send(length.to_bytes(4, 'big'))
        self._connect.send(command)
        self._connect.close()

    def _val_to_str(self, val):
        """Internal function to NI JSON string
        
        :param val: Specifies the value for convert
        :return: JSON string value
        """
        if type(val) is float:
            if val == float("Inf"):
                return "Infinity"
            elif val == -float("Inf"):
                return "-Infinity"
        elif type(val) is bool:
            if val:
                return "true"
            else:
                return "false"
        elif type(val) is str:
            return '"%s"' % (val,)
        return str(val)

    def send_command(self, command_name: str, args: dict =dict()):
        """Send command string
        
        :param command_name: Specifies the command name
        :param args: Specifies the argument list
        """
        # Create command string
        cmd = '{"cmd":"%s"' % (command_name,)
        if len(args) > 0:
            cmd += ',"args":{'
            for key, val in args.items():
                if type(val) is list or type(val) is np.ndarray:
                    cmd += '"%s":[' % (key,)
                    for v in val:
                        cmd += '%s,' % (self._val_to_str(v),)
                    if len(val) > 0:
                        cmd = cmd[:-1]
                    cmd += '],'
                else:
                    cmd += '"%s":%s,' % (key, self._val_to_str(val))
            cmd = cmd[:-1] # Drop ","
            cmd += '}'
        cmd += '}'
        self.send(cmd)

    def advanced_scan(
            self, nx: int,ny: int,dx: np.ndarray,dy: np.ndarray,
            avg: int,bidirectional_scan: bool = True, auto_reversal: bool = False) -> None:
        """Call advanced_scan command

        Before use this command, we need to move the analog outputs to an inital position.
        When you want to use auto_reversal mode, please also call set_threshold command before this command.

        :param nx: Specifies the number of fast scan points
        :param ny: Specifies the number of slow scan points
        :param dx: Specifies the delta for fast scan (8ch)
        :param dy: Specifies the delta for slow scan (8ch)
        :param avg: Specifies the average counts
        :param bidirectional: Bidirectional scan flag
        :param auto_reversal: Auto reversal flag
        :return: None
        """
        args = locals()
        args.pop('self')
        self.send_command("advanced_scan", args)

    def approach(
            self, sleep: int, avg: int, dz: float, zstart: float, zend: float,
            z2ch: int, avg2: int, dz2: float, z2start: float, z2end :float) -> None:
        """Perform an approach using the coarse approach mechanism with sawtooth wave signals. 
        
        Before calling this command, an approaced condition should be set 
        by set_threshold command.

        :param sleep: Specifies the delay between z2 motion and z motion
        :param avg: Specifies the average count for z
        :param dz: Specifies the change of z
        :param zstart: Specifies the start position of z
        :param zend: Specifies the end position of z
        :param z2ch: Specifies the z2 channel for sawtooth wave
        :param avg2: Specifies the average count for z2
        :param dz2: Specifies the change of z2
        :param z2start: Specifies the start position of z2
        :param z2end: Specifies the end position of z2
        """
        args = locals()
        args.pop('self')
        self.send_command("approach", args)

    def move(self, ch: int, val: float) -> None:
        """Change output target

        You can specify the output channel and value.
        
        :param ch: Specifies the output channel
        :param val: Specifies the output value
        """
        args = locals()
        args.pop('self')
        self.send_command("move", args)

    def note(self, note: str) -> None:
        """Call note command

        This is just for taking a note in the log file

        :param note: Note
        """
        args = locals()
        args.pop('self')
        self.send_command("note", args)

    def open_form(self, name: str) -> None:
        """Opens the GUI window specified in the argument

        :param name: Specifies the form name
        """
        args = locals()
        args.pop('self')
        self.send_command("open_form", args)

    def quit(self):
        """Exit the system
        """
        self.send_command('quit')

    def scan(self, nx: int, ny: int,
             lx: float, ly: float, cx: float, cy: float, avg: int):
        """Perform a simple x-y scan.

        :param nx: Specifies the number of data point x
        :param ny: Specifies the number of data point y
        :param lx: Specifies the length along x
        :param ly: Specifies the length along y
        :param cx: Specifies the center position x
        :param cy: Specifies the center position y
        :param avg: Specifies the averaged count for each data point
        """
        args = locals()
        args.pop('self')
        self.send_command("scan", args)

    def scan_output_list(self, filename: str, avg: int):
        """Performs a scan using a file
        
        :param filename:  Specifies the file name which include output data
        :param avg: Specifies an averaged count
        """
        args = locals()
        args.pop('self')
        self.send_command("scan_output_list", args)

    def set_ai_gain(self, gain: np.ndarray) -> None:
        """Sets the gain of the analogue input.

        :param gain: Specifies the ai gain (8ch)
        """
        args = locals()
        args.pop('self')
        self.send_command("set_ai_gain", args)

    def set_ao_gain(self, gain: np.ndarray) -> None:
        """Sets the gain of the analogue input.

        :param gain: Specifies the ao gain (8ch)
        """
        args = locals()
        args.pop('self')
        self.send_command("set_ao_gain", args)

    def set_ao_range(self, low: np.ndarray, high: np.ndarray) -> None:
        """Set the maximum and minimum analogue output values. 

        :param low: Specifies the lower limit of the output (8ch)
        :param high: Specifies the higher limit of the output (8ch)
        """
        args = locals()
        args.pop('self')
        self.send_command("set_ao_range", args)

    def set_feedback(self, fb_ch: int, input_ch: int, output_ch: int,
                     out_limit_low: float, out_limit_high: float,
                     setpoint: float,
                     p_gain: float, i_gain: float,
                     negative: bool,
                     reset: bool = False,
                     hold: bool = False,
                     err_limit_low: float = -float("Inf"), 
                     err_limit_high: float = float("Inf"), wait_for_fb: int = 0
                     ):
        """Set feedback parameters
        
        :param fb_ch: Specifies the feedback channel 0 or 1
        :param input_ch: Specifies the input channel 0-7
        :param output_ch: Specifies the output channel 0-7
        :param out_limit_low: Specifies the lower output limit
        :param out_limit_high: Specifies the higher output limit
        :param setpoint: Specifies the setpoint
        :param p_gain: Specifies the propotional gain
        :param i_gain: Specifies the integral gain
        :param negative: if true, output value becomes negative
        :param reset: reset the feedback
        :param hold: hold the feedback
        :param err_limit_low: Specifies the lower error limit for wait for feedback
        :param err_limit_high: Specifies the higher error limit for wait for feedback
        :param wait_for_fb: Specifies the count for wait for weedback, if 0, wait for weedback is deactivated.
        """
        cmd = '{"cmd":"set_feedback","args":{'
        cmd += '"fb channel":%d, ' % (fb_ch,)
        cmd += '"fb config":{"Setpoint":%g, ' % (setpoint,)
        cmd += '"Output limit (low)":%s, ' % (self._val_to_str(out_limit_low))
        cmd += '"Output limit (high)":%s, ' % (self._val_to_str(out_limit_high))
        cmd += '"P gain":%g, ' % (p_gain,)
        cmd += '"I gain":%g, ' % (i_gain,)
        cmd += '"Reset":%s, ' % (self._val_to_str(reset),)
        cmd += '"Hold":%s, ' % (self._val_to_str(hold))
        cmd += '"Negative":%s, ' % (self._val_to_str(negative))
        cmd += '"Input channel":%d, ' % (input_ch,)
        cmd += '"Output channel":%d, ' % (output_ch,)
        cmd += '"wait for fb":%d, ' % (wait_for_fb,)
        cmd += '"Error limit (high)":%s, ' % (self._val_to_str(err_limit_high))
        cmd += '"Error limit (low)":%s}}}' % (self._val_to_str(err_limit_low))
        self.send(cmd)

    def set_loop_timer(self, val=350):
        """Set interval of the FPGA main loop

        :param val: Specifies the interval in ticks
        """
        args = locals()
        args.pop('self')
        self.send_command("set_loop_timer", args)

    def set_speed(self, speed: np.ndarray) -> None:
        """Set the maximum change in analogue output per output.
        
        :param speed: Specifies the maximum changes (8ch)
        """
        args = locals()
        args.pop('self')
        self.send_command("set_speed", args)

    def set_threshold(self, 
                      ai_low: np.ndarray, fb_low: np.ndarray, 
                      ai_high: np.ndarray, fb_high: np.ndarray) -> None:
        """Specifies the auto reversal threshold

        :param ai_low: Specifies the low threshold for ai (8ch)
        :param fb_low: Specifies the low threshold for feed back  (2ch)
        :param ao_low: Specifies the hight threshold for ai (8ch)
        :param fb_high: Specifies the hight threshold for feedback (2ch)
        """
        args = locals()
        args.pop('self')
        self.send_command("set_threshold", args)

    def set_tip_guard(self, 
                      tg_position: int, 
                      ai_low: np.ndarray, fb_low: np.ndarray, 
                      ai_high: np.ndarray, fb_high: np.ndarray) -> None:
        """Specifies the tip gurard threshold

        :param tg_position: Specifies the z position of the tip when tip guard is triggered
        :param ai_low: Specifies the low threshold for ai (8ch)
        :param fb_low: Specifies the low threshold for feed back  (2ch)
        :param ao_low: Specifies the hight threshold for ai (8ch)
        :param fb_high: Specifies the hight threshold for feedback (2ch)
        """
        args = locals()
        args.pop('self')
        self.send_command("set_tip_guard", args)

def get_dat_file_list(dir="./"):
    """Function which returns a list of data files. 
    
    The data files are sorted by creation date.
    """
    files = os.listdir(dir)
    files = [file for file in files if re.match(r"([0-9]){6}.dat", file)]
    files = sorted(files, key=lambda f: os.path.getctime(os.path.join(dir, f)))
    return files

def load(file_name):
    with open(file_name, "rb") as f:
        data_shape = struct.unpack('<iiii', f.read(4*4))
        data_n = data_shape[0] * data_shape[1] * data_shape[2] * data_shape[3]
        data = np.fromfile(f, dtype=np.float32).reshape(data_shape)

    return data

def save_output_list(file_name, ch_list, output_data):
    """Function which generates data to be used in the scan_output_list command

    :param file_name: Specifies the file name of output data.
    :param ch_list: Specifies the channel list for output.
    :param output_data: Specifies the output data.
    """
    with open(file_name + ".dat", 'wb') as f:
        f.write(struct.pack('<iiii', *output_data.shape))
        output_data.astype(np.float32).tofile(f)

    with open(file_name + "_ch.dat", 'wb') as f:
        f.write(struct.pack('<i', len(ch_list)))
        ch_list.astype(np.int32).tofile(f)
