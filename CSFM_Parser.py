import os
import struct
import math
from collections import defaultdict
from datetime import timedelta
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
    Strict = auto()
    Normal = auto()

class NoteCheck(Enum):
    NOTE_SPAWN_ON_SCREEN =                              "Note Spawn Issue","Note spawns on screen"
    NOTE_SPAWN_FROM_OTHER =                             "Note Spawn Issue","Note spawns from other note"
    NOTE_SPAWN_FROM_SAME =                              "Note Spawn Issue","Note spawns from same note"
    NOTE_PHANTOM =                                      "Note Spawn Issue","Note with 0 distance"

    NOTE_PLACEMENT_OUTSIDE_GRID =                       "Note Placement Issue","Note placed outside of the grid"

    MULTI_TYPE_MORE_THAN_4 =                            "Multi-Note Type Issue","Multi-Note has more than 4 notes"

    STYLE_MULTI_880_DISTANCE =                          "Style Issue","Multi-Note uses 880 or less distance"

    NEWBIE_UNSET_NOTE =                                 "New Charter Issue","Note has placeholder placements"
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

    @classmethod
    def get_target_checks(cls):
        group = [
        cls.NOTE_SPAWN_ON_SCREEN,
        #cls.NOTE_SPAWN_FROM_OTHER,
        #cls.NOTE_SPAWN_FROM_SAME,
        #cls.NOTE_SPAWN_0_DISTANCE,
        ]
        return group

class NoteCheckOnScreenReason(Enum):
    ON_SCREEN = "Note spawns on screen"
    ITSELF = "Note spawns from itself"
    SAME_TYPE = "Note spawns from note of same type"
    DIFFERENT_TYPE = "Note spawns from note of different type"

class IssueLevel(Enum):
    Info = auto()
    Warning = auto()
    ImportantWarning = auto()
    Error = auto()
class ChartIssue:
    def __init__(self,note_check:NoteCheck,note:Note,target=None,extra_info_dict:dict=None):
        self.type = note_check
        self.note = note
        self.chart = note.chart
        self.target = target
        self.note_type = note.get_type()
        self.timestamp = note.get_tick()

        self.extra_info = extra_info_dict

    def get_note_type_string(self):
        note_name_list =[]
        for target in self.note.targets:
            note_name_list.append(target.get_type().name)

        return note_name_list
    def get_target(self):
        return self.target


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

#### Note Checks ####
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

#### Multi Checks ####

def multi_check_distance(multi_note,distance):
    for note in multi_note:
        if note[TargetProperties.Distance.value] <= distance:
            return True

    return False

#####################

def round_position(position):
    return round(position[0],None),round(position[1],None)
def filter_target_properties(section, key):
    filtered_list = []
    for target in section:
        filtered_list.append(getattr(target,key))
    return filtered_list

class Target:
    def __init__(self,chart:CsfmParser,target_properties):
        self.chart = chart

        self.tick = target_properties["Tick"]
        self.type = target_properties["Type"]
        self.has_set_properties = bool(target_properties["Properties"]) # 0 - Uses placeholder placements
        self.is_hold = bool(target_properties["Hold"])
        self.is_chain = bool(target_properties["Chain"])
        self.is_chance = bool(target_properties["Chance"])
        self.position = target_properties["Position"]
        self.angle = target_properties["Angle"]
        self.frequency = target_properties["Frequency"]
        self.distance = target_properties["Distance"]

    def get_type(self):
        match self.type:
            case 0:
                return TargetTypes.TriangleHold if self.is_hold else (TargetTypes.TriangleChance if self.is_chance else TargetTypes.Triangle)
            case 1:
                return TargetTypes.SquareHold if self.is_hold else (TargetTypes.SquareChance if self.is_chance else TargetTypes.Square)
            case 2:
                return TargetTypes.CrossHold if self.is_hold else (TargetTypes.CrossChance if self.is_chance else TargetTypes.Cross)
            case 3:
                return TargetTypes.CircleHold if self.is_hold else (TargetTypes.CircleChance if self.is_chance else TargetTypes.Circle)
            case 4:
                return TargetTypes.SlideChainL if self.is_chain else (TargetTypes.SlideLChance if self.is_chance else TargetTypes.SlideL)
            case 5:
                return TargetTypes.SlideChainR if self.is_chain else (TargetTypes.SlideRChance if self.is_chance else TargetTypes.SlideR)

        return TargetTypes.Circle
    def get_spawn_point(self):
        angle_rad = math.radians(self.angle-90)

        x = self.position[0]
        y = self.position[1]

        dx = self.distance * math.cos(angle_rad)
        dy = self.distance * math.sin(angle_rad)

        return x + dx, y + dy

    def _check_if_point_in_visible_area(self,position):
        results_dict = dict()
        for precision_setting in TargetSpawnPrecision:
            match precision_setting:
                case TargetSpawnPrecision.Normal:
                    button_size = 24
                case TargetSpawnPrecision.Strict:
                    button_size = 37  # Will complain even about shadow spawning on screen

            x_min, y_min, x_max, y_max = 0 - button_size, 0 - button_size, 1920 + button_size, 1080 + button_size

            x = position[0]
            y = position[1]

            results_dict.update({
                precision_setting.name: (x_min <= x <= x_max and y_min <= y <= y_max)
            })

        return results_dict
    def _get_spawn_source(self, point):
        timestamp = self.chart.get_flying_time_at_tick(self.tick - 1)
        first_note = self.chart.get_note_section(self.tick, flying_time_to_beats(timestamp))[0]
        section_positions = filter_target_properties(first_note.get_targets(), "position")

        if not position_check_with_tolerance(point, section_positions):
            return None

        for target in first_note.get_targets():
            other_position = round_position(target.position)
            if not position_check_with_tolerance(other_position, [point]):
                continue

            same_type = self.get_type() == target.get_type()
            same_pos = position_check_with_tolerance(other_position, [self.position])

            return self if (same_type and same_pos) else target

        return None

    def run_check(self,check:NoteCheck):
        check_info = dict()
        match check:
            case NoteCheck.NEWBIE_UNSET_NOTE:
                check_result = not bool(self.has_set_properties)
                check_info.update({"Result": check_result})

            case NoteCheck.NOTE_SPAWN_ON_SCREEN:
                point = round_position(self.get_spawn_point())
                on_screen_result = self._check_if_point_in_visible_area(point)

                check_info.update({
                    "Result": on_screen_result,
                })

                if any(on_screen_result.values()):
                    spawn_source = self._get_spawn_source(point)
                    check_info["Spawn Source"] = spawn_source
                    check_info["Note Spawn Position"] = point

                    match spawn_source:
                        case None:
                            check_info["Reason"] = NoteCheckOnScreenReason.ON_SCREEN
                        case Target():
                            target = spawn_source
                            if target.get_type() == self.get_type():
                                if target.position == self.position:
                                    check_info["Reason"] = NoteCheckOnScreenReason.ITSELF
                                else:
                                    check_info["Reason"] = NoteCheckOnScreenReason.SAME_TYPE
                            else:
                                check_info["Reason"] = NoteCheckOnScreenReason.DIFFERENT_TYPE

                return check_info

            case NoteCheck.NOTE_PHANTOM:
                check_result = self.distance == 0
                check_info.update({"Result": check_result})


            case _:
                check_result = False
                check_info.update({"Result": check_result})
class Note:
    def __init__(self, chart:CsfmParser, target_list: list[Target]):
        self.chart = chart
        self.targets = target_list

        self.tick = self.targets[0].tick
        self.type = self._get_target_types()

    def _get_target_types(self):
        type_list = []
        for target in self.targets:
            type_list.append(target.get_type())
        return type_list
    def get_type(self):
        return self.type
    def get_tick(self):
        return self.tick
    def get_targets(self):
        return self.targets
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
        target_list = []
        for entry in self.chart[ChartProperties.Targets.value]:
            target = Target(self,entry)
            target_list.append(target)
        return target_list
    def get_note_list(self):
        target_list = self.get_target_list()

        previous_tick = -1
        grouped_note_list = []
        note_list = []
        temp_group = []

        for target in target_list:
            if target.tick == previous_tick:
                temp_group.append(target)
            else:
                if temp_group:
                    grouped_note_list.append(temp_group)
                temp_group = []
                previous_tick = target.tick
                temp_group.append(target)

        if temp_group:
            grouped_note_list.append(temp_group)

        for entry in grouped_note_list:
            note = Note(self,entry)
            note_list.append(note)

        return note_list

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
    def get_note_section(self, tick, beats):
        current_tick = tick
        notes = self.get_note_list()
        ticks_per_beat = self.chart[ChartProperties.Scale.value][ScaleProperties.TicksPerBeat.value]

        ticks_in_window = beats * ticks_per_beat

        lower_bound = current_tick - ticks_in_window

        recent_notes = []

        for note in notes:
            if lower_bound <= note.get_tick() < current_tick:
                recent_notes.append(note)

        return recent_notes

    def export_dsc(self, output_filepath, has_song=True, has_movie=True):

        # TODO Needs fixing offset adjustment. Currently it breaks charts that export properly in Comfy Studio

        chart = self.chart
        time_data = chart[ChartProperties.Time.value]
        tpb = chart[ChartProperties.Scale.value][ScaleProperties.TicksPerBeat.value]
        tempo_map = chart[ChartProperties.TempoMap.value]

        script_command_list = defaultdict(list)

        def queue_command(seconds, opcode, params=[]):
            time_point = int(seconds * 100000.0)
            script_command_list[time_point].append((opcode, params))


        print(time_data.get(ChartTimeProperties.SongOffset.value))
        print(time_data.get(ChartTimeProperties.MovieOffset.value))

        song_offset = abs(time_data.get(ChartTimeProperties.SongOffset.value)) if has_song else 0.0
        movie_offset = abs(time_data.get(ChartTimeProperties.MovieOffset.value)) if has_movie else 0.0

        song_play_time = (min(-song_offset,0.0))
        movie_play_time = (min(-movie_offset,0.0))




        delay_offset = max(max(song_offset,movie_offset),0.0)


        print(delay_offset)
        print(f"Before adjustment: {song_play_time}")
        print(f"Before adjustment: {movie_play_time}")

        if song_offset > 0.0 or movie_offset >= 0.0:
            if song_offset > movie_offset:
                movie_play_time += abs(song_offset)
            elif movie_offset > song_offset:
                song_play_time += abs(movie_offset)


        print(f"After adjustment: {song_play_time}")
        print(f"After adjustment: {movie_play_time}")

        queue_command(0.0, Opcodes.CHANGE_FIELD, [1])
        queue_command(0.0, Opcodes.MIKU_DISP, [0, 0])

        if has_song:
            queue_command(song_play_time, Opcodes.MUSIC_PLAY, [])
        if has_movie:
            queue_command(movie_play_time, Opcodes.MOVIE_PLAY, [1])
            queue_command(movie_play_time, Opcodes.MOVIE_DISP, [1])

        last_flying_time = -1
        last_processed_time = 0.0
        min_gap = 0.0001

        for target in chart[ChartProperties.Targets.value]:
            target_tick = target.get(TargetProperties.Tick.value, 0)
            raw_seconds = calculate_time_seconds(target_tick, tpb, tempo_map)
            target_seconds = max(0.0, raw_seconds - delay_offset)

            if 0.0 < (target_seconds - last_processed_time) <= min_gap:
                target_seconds = last_processed_time + min_gap
            last_processed_time = target_seconds

            flying_time_ms = 1500
            if flying_time_ms != last_flying_time:
                queue_command(target_seconds, Opcodes.TARGET_FLYING_TIME, [flying_time_ms])
                last_flying_time = flying_time_ms

            pos_x, pos_y = target.get(TargetProperties.Position.value, (0.0, 0.0))
            angle = target.get(TargetProperties.Angle.value, 0.0)
            distance = target.get(TargetProperties.Distance.value, 0.0)
            amplitude = target.get(TargetProperties.Amplitude.value, 0.0)
            frequency = target.get(TargetProperties.Frequency.value, 0.0)

            target_params = [
                get_target_type_enum(target).value,
                int(pos_x * 250.0),
                int(pos_y * 250.0),
                int(angle * 1000.0),
                int(distance * 250.0),
                int(amplitude),
                int(frequency)
            ]
            queue_command(target_seconds, Opcodes.TARGET, target_params)

        duration_seconds = time_data.get(ChartTimeProperties.Duration.value, 0.0) + delay_offset
        queue_command(duration_seconds, Opcodes.PV_END, [])

        binary_data = bytearray(struct.pack('<I', 0x14050921))

        for time_point in sorted(script_command_list.keys()):
            binary_data.extend(struct.pack('<Ii', Opcodes.TIME.value, time_point))

            for opcode, params in script_command_list[time_point]:
                binary_data.extend(struct.pack('<I', opcode.value))
                for p in params:
                    binary_data.extend(struct.pack('<i', p))

        binary_data.extend(struct.pack('<I', Opcodes.END.value))

        with open(output_filepath, 'wb') as f:
            f.write(binary_data)

        print(f"DSC exported to: {output_filepath}")

    def scan_csfm(self,file):
        self.parse(file)

        print(self.get_song_name())
        print(self.get_duration())
        print(self.get_difficulty())
        print("")

        note_list = self.get_note_list()

        issues_list = []

        for note in note_list:
            for target in note.targets:
                for note_check in NoteCheck.get_target_checks():
                    check_info = target.run_check(note_check)
                    if any(check_info["Result"].values()):
                         issues_list.append(ChartIssue(note_check,note,target,check_info))

        return issues_list
    def scan_folder(self,folder):

        directory = os.fsencode(folder)

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".csfm"):
                self.scan_csfm(str(folder)+ "/" + str(filename))