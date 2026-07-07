import os
import struct
import math
from collections import defaultdict
from enum import Enum, auto


class Opcodes(Enum):
    END = 0
    TIME = 1
    MIKU_MOVE = 2
    MIKU_DISP = 4
    TARGET = 6
    CHANGE_FIELD = 14
    MUSIC_PLAY = 25
    PV_END = 32
    SCENE_FADE = 52
    TARGET_FLYING_TIME = 58
    MOVIE_PLAY = 67
    MOVIE_DISP = 68


class TargetTypes(Enum):
    Triangle = 0
    Circle = 1
    Cross = 2
    Square = 3
    TriangleHold = 4
    CircleHold = 5
    CrossHold = 6
    SquareHold = 7
    SlideL = 12
    SlideR = 13
    SlideChainL = 15
    SlideChainR = 16
    TriangleChance = 18
    CircleChance = 19
    CrossChance = 20
    SquareChance = 21
    SlideLChance = 23
    SlideRChance = 24

class ChartProperties(Enum):
    Scale = "scale"
    Time = "time"
    Targets = "targets"
    TempoMap = "tempo_map"
    ButtonSounds = "button_sounds"
    Difficulty = "difficulty"

class ChartTimeProperties(Enum):
    SongOffset = "Song Offset"
    MovieOffset = "Movie Offset"
    Duration = "Duration"
    SongPreviewStart = "Song Preview Start"
    SongPreviewDuration = "Song Preview Duration"

class CSFMSection(Enum):
    Metadata = "Metadata"
    Chart = "Chart"
    Debug = "Debug"

class HeaderProperties(Enum):
    MajorVersion = "major_version"
    MinorVersion = "minor_version"
    Endianness = "endianness"
    PointerSize = "pointer_size"
    Flags = "flags"
    CreationTime = "creation_time"
    Encoding = "encoding"

class ScaleProperties(Enum):
    TicksPerBeat = "ticks_per_beat"
    PlacementArea = "placement_area"
    FullAngleRotation = "full_angle_rotation"
    ButtonTypeNames = "button_type_names"

class TargetProperties(Enum):
    Tick = "Tick"
    Type = "Type"
    Properties = "Properties"
    Hold = "Hold"
    Chain = "Chain"
    Chance = "Chance"
    Position = "Position"
    Angle = "Angle"
    Frequency = "Frequency"
    Amplitude = "Amplitude"
    Distance = "Distance"

class TempoMapProperties(Enum):
    Tick = "Tick"
    Tempo = "Tempo"
    FlyingTimeFactor = "Flying Time Factor"
    TimeSignature = "Time Signature"
    Flags = "Flags"

class TempoMapFlags(Enum):
    HasTempo = "has_tempo"
    HasFlyingTime = "has_flying_time"
    HasSignature = "has_signature"

class ButtonSounds(Enum):
    ButtonID = "ButtonID"
    SlideID = "SlideID"
    ChainSlideID = "ChainSlideID"
    SliderTouchID = "SliderTouchID"

class DifficultyProperties(Enum):
    Type = "Type"
    Version = "Version"
    LevelWhole = "LevelWhole"
    LevelFraction = "LevelFraction"

class MetadataProperties(Enum):
    SongFileName = "Song File Name"
    MovieFileName = "Movie File Name"
    SongTitle = "Song Title"
    Artist = "Artist"
    Lyricist = "Lyricist"
    Arranger = "Arranger"
    TrackNumber = "Track Number"
    DiskNumber = "Disk Number"
    CreatorName = "Creator Name"
    CreatorComment = "Creator Comment"
    CoverFileName = "Cover File Name"
    LogoFileName = "Logo File Name"
    BackgroundFileName = "Background File Name"
    ExtraInfoKey0 = "Extra Info Key 0"
    ExtraInfoValue0 = "Extra Info Value 0"
    ExtraInfoKey1 = "Extra Info Key 1"
    ExtraInfoValue1 = "Extra Info Value 1"
    ExtraInfoKey2 = "Extra Info Key 2"
    ExtraInfoValue2 = "Extra Info Value 2"
    ExtraInfoKey3 = "Extra Info Key 3"
    ExtraInfoValue3 = "Extra Info Value 3"

class DifficultyOutput(Enum):
    Full = auto()
    StarRating = auto()
    Level = auto()
class TempoMapOutput(Enum):
    Full = auto()
    BPM = auto()
    PerceivedBPM = auto()
    BPMExtremes = auto()
    PerceivedBPMExtremes = auto()
    FlyingTime = auto()
    FlyingTimeExtremes = auto()
class TempoMapEntry(Enum):
    BPM = auto()
    FlyingTime = auto()
class TargetSpawnPrecision(Enum):
    Normal = auto()
    Strict = auto()

class NoteCheck(Enum):
    NOTE_SPAWN_ON_SCREEN =                              "Note Spawn Issue","Note spawns on screen"
    NOTE_SPAWN_FROM_OTHER =                             "Note Spawn Issue","Note spawns from other note"
    NOTE_SPAWN_FROM_SAME =                              "Note Spawn Issue","Note spawns from same note"
    NOTE_SPAWN_0_DISTANCE =                             "Note Spawn Issue","Note with 0 distance"

    NOTE_PLACEMENT_OUTSIDE_GRID =                       "Note Placement Issue","Note placed outside of the grid"
    NOTE_PLACEMENT_BAD_OVERLAP =                        "(WIP)Note Placement Issue","Note creates bad overlap"

    MULTI_PLACEMENT_HORIZONTAL_MULTI_WRONG_COLUMN =     "(WIP)Multi-Note Placement Issue","Horizontal Multi-Note in wrong columns"
    MULTI_PLACEMENT_HORIZONTAL_MULTI_DIFFERENT_HEIGHT = "(WIP)Multi-Note Placement Issue","Horizontal Multi-Note not same height"
    MULTI_PLACEMENT_VERTICAL_MULTI_NOT_ALIGNED =        "(WIP)Multi-Note Placement Issue","Vertical Multi-Note not aligned properly"
    MULTI_PLACEMENT_VERTICAL_NOTE_ORDER =               "(WIP)Multi-Note Placement Issue","Vertical Multi-Note wrong note order"
    MULTI_PLACEMENT_VERTICAL_NOTE_GAPS =                "(WIP)Multi-Note Placement Issue","Vertical Multi-Note wrong note gaps"
    MULTI_PLACEMENT_NON_STANDARD =                      "(WIP)Multi-Note Placement Issue","Non-Standard Multi-Note"

    MULTI_TYPE_MORE_THAN_4 =                            "Multi-Note Type Issue","Multi-Note has more than 4 notes"
    MULTI_TYPE_SLIDER_AND_NORMAL =                      "(WIP)Multi-Note Type Issue","Multi-Note combines slider and normal note"

    STYLE_MULTI_880_DISTANCE =                          "Style Issue","Multi-Note uses 880 or less distance"
    STYLE_DISTANCE_TOO_HIGH =                           "Style Issue","Distance used is too high"
    STYLE_AMPLITUDE_TOO_HIGH =                          "Style Issue","Amplitude used is too high"
    STYLE_FREQUENCY_TOO_HIGH =                          "Style Issue", "Frequency used is too high"
    STYLE_NORMAL_0_FREQUENCY =                          "(WIP)Style Issue","Normal note uses 0 frequency"

    HARD_DIFF_HOLD_ADD_AFTER_2 =                        "(WIP)Hard Difficulty Issue","Hold note added after 2 notes already held"
    HARD_DIFF_SPAM_MORE_THAN_3 =                        "(WIP)Hard Difficulty Issue","Spam longer than 3 notes"
    HARD_DIFF_HOLD_DURING_CHAIN =                       "(WIP)Hard Difficulty Issue","Holds during chainslider"

    NEWBIE_UNSET_NOTE =                                 "New Charter Issue","Note has placeholder placements"
    NEWBIE_192_GRID =                                   "(WIP)New Charter Issue","1/192 Grid was used"
    NEWBIE_GRAYED_OUT_MEASURE =                         "(WIP)New Charter Issue","Notes placed in grayed out measure"
    NEWBIE_ABNORMAL_BPM_CHANGE =                        "(WIP)New Charter Issue","BPM Changes faster than a measure"
    NEWBIE_HOLD_SONG_END_CUTOFF =                       "(WIP)New Charter Issue","Song ends before hold ends"

    CHAINSLIDE_NOT_STRAIGHT =                           "(WIP)Chainslide Issue","Chain slider isn't placed in straight line"
    CHAINSLIDE_FLYING_TIME_CHANGE =                     "(WIP)Chainslide Issue","Flying Time changes during Chainslider"
    CHAINSLIDE_NOTE_DURING =                            "(WIP)Chainslide Issue","Notes placed during Chainslider"
    CHAINSLIDE_MULTI =                                  "(WIP)Chainslide Issue","Multi-Chainslider used"

    PLAYABILITY_SPAM_DURING_HOLD =                      "(WIP)Playability Issue","Spam during Holds"
    PLAYABILITY_SPAM_TOO_FAST =                         "(WIP)Playability Issue","Spam is too fast to play"
    PLAYABILITY_NOT_ENOUGH_PATH =                       "(WIP)Playability Issue","Not enough of path on screen"

    SPACING_TOO_FAR =                                   "(WIP)Spacing Issue","Note is too far away from previous note",
    SPACING_TOO_CLOSE =                                 "(WIP)Spacing Issue","Note is too close to previous note"

    NOTE_GROUP_WRONG_FREQ =                             "(WIP)Note Group Issue","Frequency doesn't match pattern direction"
    NOTE_GROUP_NO_ANGLE_INCREMENT =                     "(WIP)Note Group Issue","Pattern doesn't use angle increments"

    ARCADE_ORDER =                                      "(WIP)Arcade Order Issue","Shit Pattern"

    def __new__(cls, category: str, description: str):
        obj = object.__new__(cls)
        obj._value_ = description
        obj.category = category
        return obj

    @classmethod
    def of_category(cls, category: str):
        return [m for m in cls if m.category == category]

    @classmethod
    def categories(cls):
        return {member.category for member in cls}

class IssueLevel(Enum):
    Info = auto()
    Warning = auto()
    ImportantWarning = auto()
    Error = auto()
class ChartIssue:
    def __init__(self,level:IssueLevel,note_check:NoteCheck,note,parser:CsfmParser,extra_info_dict:dict=None):
        self.level = level
        self.type = note_check
        self.note = note
        self.parser = parser
        self.note_type = self.get_note_type()
        self.timestamp = self.get_timestamp()

        self.extra_info = extra_info_dict
    def get_note_type(self):
        if type(self.note) == list:
            output = "Multi-Note:"
            for note in self.note:
                output = output +" "+ str(get_target_type_enum(note).name)
        else:
            output = str(get_target_type_enum(self.note).name)
        return output
    def get_timestamp(self):
        if type(self.note) == list:
            return self.note[0][TargetProperties.Tick.value]
        else:
            return self.note[TargetProperties.Tick.value]

def get_target_type_enum(target):
    btn_type = target.get("Type", 3)
    is_hold = bool(target.get("Hold", 0))
    is_chain = bool(target.get("Chain", 0))
    is_chance = bool(target.get("Chance", 0))

    if btn_type == 0:
        return TargetTypes.TriangleHold if is_hold else (TargetTypes.TriangleChance if is_chance else TargetTypes.Triangle)
    elif btn_type == 1:
        return TargetTypes.SquareHold if is_hold else (TargetTypes.SquareChance if is_chance else TargetTypes.Square)
    elif btn_type == 2:
        return TargetTypes.CrossHold if is_hold else (TargetTypes.CrossChance if is_chance else TargetTypes.Cross)
    elif btn_type == 3:
        return TargetTypes.CircleHold if is_hold else (TargetTypes.CircleChance if is_chance else TargetTypes.Circle)
    elif btn_type == 4:
        return TargetTypes.SlideChainL if is_chain else (TargetTypes.SlideLChance if is_chance else TargetTypes.SlideL)
    elif btn_type == 5:
        return TargetTypes.SlideChainR if is_chain else (TargetTypes.SlideRChance if is_chance else TargetTypes.SlideR)

    return TargetTypes.Circle


def calculate_time_seconds(tick, ticks_per_beat, tempo_map):
    total_seconds = 0.0
    last_tick = 0
    current_bpm = tempo_map[0]['Tempo'] if tempo_map and 'Tempo' in tempo_map[0] else 160.0

    for tc in tempo_map:
        tc_tick = tc.get('Tick', 0)
        if tc_tick >= tick:
            break
        beats_spent = (tc_tick - last_tick) / ticks_per_beat
        total_seconds += beats_spent * (60.0 / current_bpm)
        last_tick = tc_tick
        if tc.get('Flags', {}).get('has_tempo', True) and 'Tempo' in tc:
            current_bpm = tc['Tempo']

    remaining_beats = (tick - last_tick) / ticks_per_beat
    total_seconds += remaining_beats * (60.0 / current_bpm)
    return total_seconds


def export_dsc(parsed_data, output_filepath, has_song=True, has_movie=True):

    #TODO Needs fixing offset adjustment. Currently it breaks charts that export properly in Comfy Studio

    chart = parsed_data["chart"]
    time_data = chart["time"]
    tpb = chart["scale"]["ticks_per_beat"]
    tempo_map = chart["tempo_map"]

    timeline = defaultdict(list)

    def queue_command(seconds, opcode, params=[]):
        time_point = int(seconds * 100000.0)
        timeline[time_point].append((opcode, params))

    song_offset = abs(time_data.get("Song Offset")) if has_song else 0.0
    movie_offset = abs(time_data.get("Movie Offset")) if has_movie else 0.0

    delay_offset = max(song_offset, movie_offset, 0.0)


    song_play_time = song_offset #it needs to factor in delay_offset
    movie_play_time = movie_offset #it needs to factor in delay_offset

    print(song_offset)
    print(delay_offset)

    print(song_play_time)
    print(movie_play_time)

    queue_command(0.0, Opcodes.CHANGE_FIELD, [1])
    queue_command(0.0, Opcodes.MIKU_DISP, [0, 0])  # Index 0, Hidden


    if has_song:
        queue_command(song_play_time, Opcodes.MUSIC_PLAY, [])
    if has_movie:
        queue_command(movie_play_time, Opcodes.MOVIE_PLAY, [1])
        queue_command(movie_play_time, Opcodes.MOVIE_DISP, [1])

    last_flying_time = -1
    last_processed_time = 0.0
    min_gap = 0.0001

    for target in chart["targets"]:
        target_tick = target.get("Tick", 0)
        raw_seconds = calculate_time_seconds(target_tick, tpb, tempo_map)
        target_seconds = max(0.0, raw_seconds - delay_offset)

        if 0.0 < (target_seconds - last_processed_time) <= min_gap:
            target_seconds = last_processed_time + min_gap
        last_processed_time = target_seconds

        flying_time_ms = 1500
        if flying_time_ms != last_flying_time:
            queue_command(target_seconds, Opcodes.TARGET_FLYING_TIME, [flying_time_ms])
            last_flying_time = flying_time_ms

        pos_x, pos_y = target.get("Position", (0.0, 0.0))
        angle = target.get("Angle", 0.0)
        distance = target.get("Distance", 0.0)
        amplitude = target.get("Amplitude", 0.0)
        frequency = target.get("Frequency", 0.0)

        target_params = [
            get_target_type_enum(target),
            int(pos_x * 250.0),
            int(pos_y * 250.0),
            int(angle * 1000.0),
            int(distance * 250.0),
            int(amplitude),
            int(frequency)
        ]
        queue_command(target_seconds, Opcodes.TARGET, target_params)

    duration_seconds = time_data.get("Duration", 0.0) + delay_offset
    queue_command(duration_seconds, Opcodes.PV_END, [])

    binary_data = bytearray(struct.pack('<I', 0x14050921))

    for time_point in sorted(timeline.keys()):
        binary_data.extend(struct.pack('<Ii', Opcodes.TIME, time_point))

        for opcode, params in timeline[time_point]:
            binary_data.extend(struct.pack('<I', opcode))
            for p in params:
                binary_data.extend(struct.pack('<i', p))

    binary_data.extend(struct.pack('<I', Opcodes.END))

    with open(output_filepath, 'wb') as f:
        f.write(binary_data)

    print(f"Successfully serialized valid binary PVScript to: {output_filepath}")

def flying_time_to_beats(flying_time_percent):
    """Gets amount of beats it takes for note to fly in"""
    #TODO Rename it to something that's more self-explanatory
    if flying_time_percent is None:
        return 4.0

    if flying_time_percent < 100:
        return 4 + (100 - flying_time_percent) / 25.0
    elif flying_time_percent > 100:
        return 4 - (flying_time_percent - 100) / 100.0
    else:
        return 4.0

def get_first_target_from_section(recent_targets):
    target_list = []
    for target in recent_targets:
        if target[TargetProperties.Tick.value] == recent_targets[0][TargetProperties.Tick.value]:
            target_list.append(target)

    return target_list

def get_note_spawn_point(target):
    position = target[TargetProperties.Position.value]
    angle = target[TargetProperties.Angle.value]
    distance = target[TargetProperties.Distance.value]

    angle_rad = math.radians(angle-90)

    x = position[0]
    y = position[1]

    dx = distance * math.cos(angle_rad)
    dy = distance * math.sin(angle_rad)

    return x + dx, y + dy
#### Note Checks ####
def check_if_point_in_visible_area(position,precision:TargetSpawnPrecision):
    button_size = 24
    if precision == TargetSpawnPrecision.Normal:
        button_size = 24
    if precision == TargetSpawnPrecision.Strict:
        button_size = 37 #Will complain even about shadow spawning on screen

    x_min, y_min, x_max, y_max = 0-button_size,0-button_size,1920+button_size,1080+button_size


    x = position[0]
    y = position[1]

    return x_min <= x <= x_max and y_min <= y <= y_max
def check_if_point_in_grid(position):

    x = position[0]
    y = position[1]

    x_min, y_min, x_max, y_max = 96, 192, 1824, 864

    return x_min <= x <= x_max and y_min <= y <= y_max
def position_check_with_tolerance(position, last_section_positions, precision=5.0):
    #Ideally autistic precision of 1 would be used,
    # that however is overkill for faster songs where it's hard to spot misalignment

    x, y = position
    for ref_x, ref_y in last_section_positions:
        distance = math.hypot(x - ref_x, y - ref_y)
        if distance <= precision:
            return True
    return False

def note_check_unset_position(note):
    position = note[TargetProperties.Position.value]

    x = position[0]
    y = position[1]

    if x == 0 or y == 0:
        return True
    else:
        return False

def note_check_spawn_on_screen(note,precision):
    point = get_note_spawn_point(note)
    extra_info_dict = {"Note Spawn Position": round_position(point)}

    check_result = check_if_point_in_visible_area(point,precision)
    return check_result,extra_info_dict
def note_check_spawn_from_other(parser,note):
    point = get_note_spawn_point(note)
    extra_info_dict = {"Note Spawn Position": round_position(point)}

    timestamp = parser.get_flying_time_at_tick(note[TargetProperties.Tick.value] - 1)
    section = parser.get_target_section(note[TargetProperties.Tick.value], flying_time_to_beats(timestamp))
    section_positions = filter_target_properties(get_first_target_from_section(section), TargetProperties.Position)

    check_result = position_check_with_tolerance(round_position(point), section_positions)
    return check_result,extra_info_dict
def note_check_spawn_from_same(parser,note):
    point = get_note_spawn_point(note)
    extra_info_dict = {"Note Spawn Position":round_position(point)}

    timestamp = parser.get_flying_time_at_tick(note[TargetProperties.Tick.value] - 1)
    section = parser.get_target_section(note[TargetProperties.Tick.value], flying_time_to_beats(timestamp))
    target_type = -1

    for target in get_first_target_from_section(section):
        target_position = round_position(target[TargetProperties.Position.value])
        if position_check_with_tolerance(target_position, [round_position(point)]):
            target_type = get_target_type_enum(target).name
            extra_info_dict.update({"Other Note Type":target_type})

    check_result = get_target_type_enum(note).name == target_type
    return check_result, extra_info_dict

def note_check_spawn_0_distance(note):
    point = get_note_spawn_point(note)
    extra_info_dict = {"Note Spawn Position": round_position(point)}

    check_result = note[TargetProperties.Distance.value] == 0
    return check_result, extra_info_dict

#### Multi Checks ####

def multi_check_distance(multi_note,distance):
    for note in multi_note:
        if note[TargetProperties.Distance.value] <= distance:
            return True

    return False

#####################

def round_position(position):
    return round(position[0],None),round(position[1],None)
def filter_target_properties(section, key:TargetProperties):
    filtered_list = []
    for target in section:
        filtered_list.append(target[key.value])
    return filtered_list


class CsfmParser:
    MAGIC_BYTES = b'CSFM'

    def __init__(self):
        self.header = {}
        self.metadata = {}
        self.chart = {
            "scale": {},
            "time": {},
            "targets": [],
            "tempo_map": [],
            "button_sounds": {},
            "difficulty": {}
        }

    @staticmethod
    def _read_u8(f):
        return struct.unpack('<B', f.read(1))[0]

    @staticmethod
    def _read_i16(f):
        return struct.unpack('<h', f.read(2))[0]

    @staticmethod
    def _read_u16(f):
        return struct.unpack('<H', f.read(2))[0]

    @staticmethod
    def _read_i32(f):
        return struct.unpack('<i', f.read(4))[0]

    @staticmethod
    def _read_u32(f):
        return struct.unpack('<I', f.read(4))[0]

    @staticmethod
    def _read_u64(f):
        return struct.unpack('<Q', f.read(8))[0]

    @staticmethod
    def _read_f32(f):
        return struct.unpack('<f', f.read(4))[0]

    @staticmethod
    def _read_f64(f):
        return struct.unpack('<d', f.read(8))[0]

    @staticmethod
    def _read_str_at(f, offset):
        if offset == 0:
            return ""

        original_pos = f.tell()
        f.seek(offset)

        chars = bytearray()
        while True:
            c = f.read(1)
            if not c or c == b'\x00':
                break
            chars.extend(c)

        f.seek(original_pos)
        return chars.decode('utf-8', errors='ignore')

    @staticmethod
    def _read_str_ptr(f):
        offset = CsfmParser._read_u64(f)
        return CsfmParser._read_str_at(f, offset)

    def parse(self, filepath: str):
        with open(filepath, 'rb') as f:
            try:
                self._parse_header(f)
            except ValueError:
                print("Unsupported CSFM version!")
                return

            creator_info_address = f.tell()
            creator_info_size = self._read_u64(f)
            f.seek(creator_info_address + creator_info_size)

            section_count = self._read_u64(f)
            sections_offset = self._read_u64(f)
            self._read_u64(f)  # Reserved / Padding
            self._read_u64(f)  # Reserved / Padding

            if section_count < 1 or sections_offset == 0:
                return

            f.seek(sections_offset)
            for _ in range(section_count):
                section_name = self._read_str_ptr(f)
                section_offset = self._read_u64(f)
                self._read_u64(f)  # Padding
                self._read_u64(f)  # Padding

                if section_offset == 0:
                    continue

                pos = f.tell()
                f.seek(section_offset)

                if section_name == "Metadata":
                    self._parse_metadata_section(f)
                elif section_name == "Chart":
                    self._parse_chart_section(f)

                f.seek(pos)

    def _parse_header(self, f):
        magic = f.read(4)
        if magic != self.MAGIC_BYTES:
            raise ValueError(f"Invalid file magic: {magic}. Expected CSFM.")

        self.header = {
            "major_version": self._read_u16(f),
            "minor_version": self._read_u16(f),
            "endianness": f.read(2).decode('ascii'),
            "pointer_size": self._read_u16(f),
            "flags": self._read_u32(f),
            "creation_time": self._read_u64(f),
            "encoding": f.read(8).decode('ascii').strip('\x00')
        }
        f.read(32)  # 8x u32 Reserved bytes

        if self.header[HeaderProperties.MajorVersion.value] != 1:
            raise ValueError(f"This version isn't supported. Only Arcade CSFM's are supported at this time!")

    def _parse_metadata_section(self, f):
        entry_count = self._read_u64(f)
        entries_offset = self._read_u64(f)
        self._read_u64(f)  # Padding
        self._read_u64(f)  # Padding

        if entries_offset == 0:
            return

        f.seek(entries_offset)
        for _ in range(entry_count):
            key = self._read_str_ptr(f)
            val = self._read_str_ptr(f)
            self._read_u64(f)  # Padding
            self._read_u64(f)  # Padding
            self.metadata[key] = val

    def _parse_chart_section(self, f):
        chart_section_count = self._read_u64(f)
        chart_sections_offset = self._read_u64(f)
        self._read_u64(f)  # Padding
        self._read_u64(f)  # Padding

        if chart_sections_offset == 0:
            return

        f.seek(chart_sections_offset)
        for _ in range(chart_section_count):
            name_id = self._read_str_ptr(f)
            offset = self._read_u64(f)
            self._read_u64(f)
            self._read_u64(f)

            if offset == 0:
                continue

            pos = f.tell()
            f.seek(offset)

            if name_id == "Scale":
                self._parse_chart_scale(f)
            elif name_id == "Time":
                self._parse_chart_time(f)
            elif name_id == "Targets":
                self._parse_chart_targets(f)
            elif name_id == "Tempo Map":
                self._parse_chart_tempo_map(f)
            elif name_id == "Button Sounds":
                self._parse_chart_button_sounds(f)
            elif name_id == "Difficulty":
                self._parse_chart_difficulty(f)

            f.seek(pos)

    def _parse_chart_scale(self, f):
        btn_type_count = self._read_u64(f)
        btn_types_offset = self._read_u64(f)

        self.chart["scale"]["ticks_per_beat"] = self._read_i32(f)
        self._read_i32(f)  # padding
        self.chart["scale"]["placement_area"] = (self._read_f32(f), self._read_f32(f))

        rotation = self._read_f32(f)
        self.chart["scale"]["full_angle_rotation"] = 360.0 if rotation == 0.0 else rotation

        self._read_u32(f)  # padding
        for _ in range(3): self._read_u64(f)  # padding

        if btn_types_offset != 0:
            pos = f.tell()
            f.seek(btn_types_offset)
            btn_names = [self._read_str_ptr(f) for _ in range(btn_type_count)]
            self.chart["scale"]["button_type_names"] = btn_names
            f.seek(pos)

    def _parse_chart_time(self, f):
        entry_count = self._read_u64(f)
        entries_offset = self._read_u64(f)
        self._read_u64(f)
        self._read_u64(f)

        if entries_offset != 0:
            f.seek(entries_offset)
            for _ in range(entry_count):
                key = self._read_str_ptr(f)
                val = self._read_f64(f)
                self._read_u64(f)
                self._read_u64(f)
                self.chart["time"][key] = val

    def _parse_chart_targets(self, f):
        target_count = self._read_u64(f)
        field_count = self._read_u64(f)
        fields_offset = self._read_u64(f)
        self._read_u64(f)

        self.chart["targets"] = [{} for _ in range(target_count)]

        if fields_offset == 0:
            return

        f.seek(fields_offset)
        for _ in range(field_count):
            name_id = self._read_str_ptr(f)
            byte_size = self._read_u64(f)
            array_size = self._read_u64(f)
            field_offset = self._read_u64(f)
            self._read_u64(f)
            self._read_u64(f)

            if field_offset != 0:
                pos = f.tell()
                f.seek(field_offset)

                for i in range(target_count):
                    val = None
                    if name_id == "Tick":
                        val = self._read_i32(f)
                    elif name_id in ["Type", "Properties", "Hold", "Chain", "Chance"]:
                        val = self._read_u8(f)
                    elif name_id == "Position":
                        val = (self._read_f32(f), self._read_f32(f))
                    elif name_id in ["Angle", "Frequency", "Amplitude", "Distance"]:
                        val = self._read_f32(f)

                    if val is not None:
                        self.chart["targets"][i][name_id] = val
                f.seek(pos)

    def _parse_chart_tempo_map(self, f):
        tempo_count = self._read_u64(f)
        field_count = self._read_u64(f)
        fields_offset = self._read_u64(f)
        self._read_u64(f)

        self.chart["tempo_map"] = [{} for _ in range(tempo_count)]

        if fields_offset == 0:
            return

        f.seek(fields_offset)
        for _ in range(field_count):
            name_id = self._read_str_ptr(f)
            byte_size = self._read_u64(f)
            array_size = self._read_u64(f)
            field_offset = self._read_u64(f)
            self._read_u64(f)
            self._read_u64(f)

            if field_offset != 0:
                pos = f.tell()
                f.seek(field_offset)

                for i in range(tempo_count):
                    val = None
                    if name_id == "Tick":
                        val = self._read_i32(f)
                    elif name_id == "Tempo":
                        val = self._read_f32(f)
                    elif name_id == "Flying Time Factor":
                        val = self._read_f32(f)
                    elif name_id == "Time Signature":
                        val = (self._read_i16(f), self._read_i16(f))
                    elif name_id == "Flags":
                        flags = self._read_u32(f)
                        val = {
                            "has_tempo": bool(flags & 1),
                            "has_flying_time": bool((flags >> 1) & 1),
                            "has_signature": bool((flags >> 2) & 1)
                        }

                    if val is not None:
                        self.chart["tempo_map"][i][name_id] = val
                f.seek(pos)

    def _parse_chart_button_sounds(self, f):
        btn_count = self._read_u64(f)
        btn_offset = self._read_u64(f)
        self._read_u64(f)
        self._read_u64(f)

        if btn_offset != 0 and btn_count >= 4:
            f.seek(btn_offset)
            self.chart["button_sounds"] = {
                "ButtonID": self._read_u32(f),
                "SlideID": self._read_u32(f),
                "ChainSlideID": self._read_u32(f),
                "SliderTouchID": self._read_u32(f)
            }

    def _parse_chart_difficulty(self, f):
        self.chart["difficulty"] = {
            "Type": self._read_u8(f),
            "Version": self._read_u8(f),
            "LevelWhole": self._read_u8(f),
            "LevelFraction": self._read_u8(f)
        }
        self._read_u64(f)
        self._read_u64(f)

    def get_song_name(self):
        try:
            return self.metadata[MetadataProperties.SongTitle.value]
        except KeyError:
            return ""
    def get_difficulty(self,output_format:DifficultyOutput=DifficultyOutput.Full):
        type = self.chart[ChartProperties.Difficulty.value][DifficultyProperties.Type.value]
        version = self.chart[ChartProperties.Difficulty.value][DifficultyProperties.Version.value]
        whole = self.chart[ChartProperties.Difficulty.value][DifficultyProperties.LevelWhole.value]
        fraction = self.chart[ChartProperties.Difficulty.value][DifficultyProperties.LevelFraction.value]

        difficulty_string = ""
        if not version == 0:
            difficulty_string = "Extra "

        match type:
            case 0:
                difficulty_string = difficulty_string + "Easy"
            case 1:
                difficulty_string = difficulty_string + "Normal"
            case 2:
                difficulty_string = difficulty_string + "Hard"
            case 3:
                difficulty_string = difficulty_string + "Extreme"

        match output_format:
            case DifficultyOutput.Full:
                return f"{difficulty_string} {whole}.{fraction}"
            case DifficultyOutput.Level:
                return f"{difficulty_string}"
            case DifficultyOutput.StarRating:
                return f"{whole}.{fraction}"
    def get_duration(self):
        total_seconds = self.chart[ChartProperties.Time.value][ChartTimeProperties.Duration.value]

        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds * 1000) % 1000)

        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    def get_tempo_map(self,output_type:TempoMapOutput=TempoMapOutput.Full):
        tempo_list = []
        output = []

        for entry in self.chart[ChartProperties.TempoMap.value]:
            tempo_list.append((round(entry[TempoMapProperties.Tempo.value],2),(round(entry[TempoMapProperties.FlyingTimeFactor.value] * 100))))

        match output_type:
            case TempoMapOutput.Full:
                for entry in tempo_list:
                        output.append((entry[0],entry[1]))

            case TempoMapOutput.BPM:
                previous_bpm = 0.0
                for entry in tempo_list:
                    if entry[0] != previous_bpm:
                        output.append(entry[0])

                        previous_bpm = entry[0]
                    else:
                        continue

            case TempoMapOutput.PerceivedBPM:
                previous_bpm = 0.0
                for entry in tempo_list:
                    if entry[0]*(entry[1]/100) != previous_bpm:
                        output.append(round(entry[0]*(entry[1]/100),2))
                        previous_bpm = entry[0]*(entry[1]/100)
                    else:
                        continue

            case TempoMapOutput.BPMExtremes:
                lowest_bpm_seen = 9999999
                highest_bpm_seen = 0

                for entry in tempo_list:
                    if entry[0] > highest_bpm_seen:
                        highest_bpm_seen = entry[0]
                    if entry[0] < lowest_bpm_seen:
                        lowest_bpm_seen = entry[0]

                if lowest_bpm_seen == highest_bpm_seen:
                    output.append(lowest_bpm_seen)
                else:
                    output.append((lowest_bpm_seen,highest_bpm_seen))

            case TempoMapOutput.PerceivedBPMExtremes:
                lowest_bpm_seen = 9999999
                highest_bpm_seen = 0

                for entry in tempo_list:
                    if entry[0]*(entry[1]/100) > highest_bpm_seen:
                        highest_bpm_seen = entry[0]*(entry[1]/100)
                    if entry[0]*(entry[1]/100) < lowest_bpm_seen:
                        lowest_bpm_seen = entry[0]*(entry[1]/100)

                if lowest_bpm_seen == highest_bpm_seen:
                    output.append(round(lowest_bpm_seen,2))
                else:
                    output.append((round(lowest_bpm_seen,2),round(highest_bpm_seen,2)))


            case TempoMapOutput.FlyingTime:
                previous_flying_time = 0.0
                for entry in tempo_list:
                    if entry[1] != previous_flying_time:
                        output.append(entry[1])
                        previous_flying_time = entry[1]
                    else:
                        continue

            case TempoMapOutput.FlyingTimeExtremes:
                lowest_flying_time_seen = 9999999
                highest_flying_time_seen = 0

                for entry in tempo_list:
                    if entry[1] > highest_flying_time_seen:
                        highest_flying_time_seen = entry[1]
                    if entry[1] < lowest_flying_time_seen:
                        lowest_flying_time_seen = entry[1]

                if lowest_flying_time_seen == highest_flying_time_seen:
                    output.append(lowest_flying_time_seen)
                else:
                    output.append((lowest_flying_time_seen,highest_flying_time_seen))



        return output
    def get_target_list(self):
        return self.chart[ChartProperties.Targets.value]

    def get_multi_note_list(self):
        target_list = self.get_target_list()

        previous_tick = -1
        multi_note_list = []
        temp_group = []
        for target in target_list:
            if target[TargetProperties.Tick.value] == previous_tick:
                temp_group.append(target)
            else:
                if temp_group:
                    multi_note_list.append(temp_group)
                temp_group = []
                previous_tick = target[TargetProperties.Tick.value]
                temp_group.append(target)

        if temp_group:
            multi_note_list.append(temp_group)

        for entry in multi_note_list:
            if len(entry) == 1:
                multi_note_list.remove(entry)

        return multi_note_list


    def get_flying_time_at_tick(self,tick):
        current_flying_time = 1
        for tempo_map_entry in self.chart[ChartProperties.TempoMap.value]:
            if tempo_map_entry[TempoMapProperties.Tick.value] <= tick:
                current_flying_time = tempo_map_entry[TempoMapProperties.FlyingTimeFactor.value]
            else:
                break

        return current_flying_time * 100
    def get_time_from_tick(self,target_tick):
        tempo_map = self.chart[ChartProperties.TempoMap.value]
        ticks_per_beat = self.chart[ChartProperties.Scale.value][ScaleProperties.TicksPerBeat.value]

        total_seconds = 0.0
        last_tick = 0

        current_bpm = 160.0
        if tempo_map and 'Tempo' in tempo_map[0]:
            current_bpm = tempo_map[0]['Tempo']

        for tc in tempo_map:
            tc_tick = tc.get('Tick', 0)

            if tc_tick >= target_tick:
                break

            ticks_spent = tc_tick - last_tick
            beats_spent = ticks_spent / ticks_per_beat
            total_seconds += beats_spent * (60.0 / current_bpm)

            last_tick = tc_tick
            if tc.get('Flags', {}).get('has_tempo', True) and 'Tempo' in tc:
                current_bpm = tc['Tempo']

        remaining_ticks = target_tick - last_tick
        remaining_beats = remaining_ticks / ticks_per_beat
        total_seconds += remaining_beats * (60.0 / current_bpm)

        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds * 1000) % 1000)

        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    def get_target_section(self,tick, beats):
        current_tick = tick
        targets = self.get_target_list()
        ticks_per_beat = self.chart[ChartProperties.Scale.value][ScaleProperties.TicksPerBeat.value]

        ticks_in_window = beats * ticks_per_beat

        lower_bound = current_tick - ticks_in_window

        recent_targets = [
            t for t in targets
            if lower_bound <= t.get("Tick") < current_tick
        ]
        return recent_targets


    def scan_csfm(self,file,precision:TargetSpawnPrecision):
        note_spawn_precision = precision
        self.parse(file)

        print(self.get_song_name())
        print(self.get_duration())
        print(self.get_difficulty())
        print("")

        issues_list = []
        for note in self.chart[ChartProperties.Targets.value]:

            if note_check_unset_position(note):
                issues_list.append(ChartIssue(IssueLevel.Error,NoteCheck.NEWBIE_UNSET_NOTE,note,self))
                continue

            if not check_if_point_in_grid(note[TargetProperties.Position.value]):
                issues_list.append(ChartIssue(IssueLevel.Error, NoteCheck.NOTE_PLACEMENT_OUTSIDE_GRID, note, self))

            if note[TargetProperties.Amplitude.value] > 5000:
                issues_list.append(ChartIssue(IssueLevel.Info,NoteCheck.STYLE_AMPLITUDE_TOO_HIGH,note,self))
            if note[TargetProperties.Distance.value] > 5000:
                issues_list.append(ChartIssue(IssueLevel.Info,NoteCheck.STYLE_DISTANCE_TOO_HIGH,note,self))
            if note[TargetProperties.Frequency.value] > 4 or note[TargetProperties.Frequency.value] < -4:
                issues_list.append(ChartIssue(IssueLevel.Info,NoteCheck.STYLE_FREQUENCY_TOO_HIGH,note,self))


            note_spawns_on_screen,extra_info_dict = note_check_spawn_on_screen(note,note_spawn_precision)
            if note_spawns_on_screen:
                note_spawns_from_other,extra_info_dict = note_check_spawn_from_other(self,note)
                note_has_0_distance,extra_info_dict = note_check_spawn_0_distance(note)

                if note_spawns_from_other:
                    note_spawns_from_same_type , extra_info_dict = note_check_spawn_from_same(self,note)

                    if note_spawns_from_same_type:
                        issues_list.append(ChartIssue(IssueLevel.Info,NoteCheck.NOTE_SPAWN_FROM_SAME,note,self,extra_info_dict))

                    else:
                        issues_list.append(ChartIssue(IssueLevel.Error,NoteCheck.NOTE_SPAWN_FROM_OTHER,note,self,extra_info_dict))

                elif note_has_0_distance:
                    issues_list.append(ChartIssue(IssueLevel.Info,NoteCheck.NOTE_SPAWN_0_DISTANCE,note,self,extra_info_dict))

                else:
                    issues_list.append(ChartIssue(IssueLevel.Error,NoteCheck.NOTE_SPAWN_ON_SCREEN,note,self,extra_info_dict))

        for multi_note in self.get_multi_note_list():
            if multi_check_distance(multi_note,880):
                issues_list.append(ChartIssue(IssueLevel.Error, NoteCheck.STYLE_MULTI_880_DISTANCE, multi_note, self))

            if len(multi_note) > 4:
                issues_list.append(ChartIssue(IssueLevel.Error, NoteCheck.MULTI_TYPE_MORE_THAN_4, multi_note, self))


        return issues_list
    def scan_folder(self,folder,precision:TargetSpawnPrecision):
        note_spawn_precision = precision

        directory = os.fsencode(folder)

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".csfm"):
                self.scan_csfm(str(folder)+ "/" + str(filename),note_spawn_precision)






