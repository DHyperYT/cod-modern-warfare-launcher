import os
import re
import tkinter as tk
from tkinter import ttk 

class OperatorEditor:
    def __init__(self, root, backup_path):
        self.root = root
        self.root.title("Operator Editor")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", 1)
        self.backup_path = backup_path

        # Data
        self.operators = {
            "Coalition": {
                "default_western": [
                    "Default", "Pararescue1", "Pararescue2", "Pararescue3", "CTFSO1",
                    "CTFSO2", "CTFSO3", "SKSF1", "SKSF2", "SKSF3", "USEF1", "USEF2",
                    "USEF3", "Frogman"
                ],
                "ghost_western": [
                    "Jawbone", "Mandible", "LastBreath", "Ghosted", "DarkVision",
                    "Reckoner", "Frogman", "Classic"
                ],
                "murphy_western": [
                    "Deployment", "DesertRat", "Seafarer", "Marshland", "GreyWolf",
                    "NightRaid", "Security", "LaMuerte", "Solstice", "SAS", "InkedInfil",
                    "Ripcord", "Valor", "Vigilance", "MightyArse"
                ],
                "charly_western": [
                    "Patrol", "Warden", "Scout", "Clouded", "Tundra", "Grassroots",
                    "CarbonAsh", "SAS", "Huntress", "AngelOfD", "TacticalH", "Sinister"
                ],
                "otter_western": [
                    "JungleRaid", "Swampland", "Woodland", "Sandstorm", "Desert",
                    "SAS", "Urban", "CrewExpend", "IPinchBack", "Jungle", "TF141",
                    "DemoExpert", "SnowDrift", "Irradiated"
                ],
                "dday_western": [
                    "OpenSeason", "SageBrush", "Fall", "ArcticOps", "Nightmare", 
                    "Buckshot", "ClippedIn", "DeepPockets", "Nightshift", "DemonDogs",
                    "QuickDraw", "Tailgate", "TrueVictory", "CamoCroc", "Scarecrow",
                    "Bushranger", "LoneStar", "BorderWar"
                ],
                "alice_western": [
                    "Tactical", "Maplewood", "Mechanic", "Muddin", "SmartTactical",
                    "GreyMatter", "DownRange", "StreetSmart", "DemonDogs", "BossLady",
                    "Rime"
                ],
                "raines_western": [
                    "Raider", "StuntDouble", "Touchdown", "Mariner", "RoadRage",
                    "BuffaloHunter", "DarkPacifier", "Evergreen", "DemonDogs", "Outback",
                    "Tactical", "Bunyan"
                ],
                "crowfoot_western": [
                    "Skin2", "Skin3", "Tracker", "GoodMedicine", "ColdCreek", "Scarecrow"
                ],
                "domino_western": [
                    "Commando", "ColdTimber", "Jungle", "Wetworks", "GreenMamba",
                    "UrbanAssault", "Hardened", "BattleReady", "WarcomDomino", "DesertOps",
                    "707thSMB", "SecurityDetail", "SpyGames"
                ],
                "golem_western": [
                    "JungleTerror", "NightRaid", "CounterTerror", "WinterWarrior",
                    "SpectralAss", "Black&Blue", "Minimalist", "Stuntman", "WarcomGolem",
                    "SwampFever", "Foliage", "IceCold", "WinterWarrior2", "JunkPile",
                    "BlackForest"
                ],
                "zedra_western": [
                    "DeathDealer", "ChemDivision", "DesertWork", "GreenDust", "ForestOps",
                    "DigitalDark", "DuneHunter", "Quick-witted", "Valkyrie"
                ],
                "wyatt_western": [
                    "RaidGear", "Remnant", "Sprinter", "UrbanHip", "Digital", "Warcom",
                    "GoingGray", "Run&Gun", "Desperado", "Commander", "WarPig", "Outback",
                    "TheWoodsman", "TheBagger"
                ],
                "ronin_western": ["LoneDragon"],
                "alex_western": [
                    "Indomitable", "LuckyStreak", "BackForMore", "HardWired",
                    "Eliminator", "Automation"
                ],
                "lynch_western": ["Raider"]
            },
            "Allegiance": {
                "default_eastern": ["Default"],
                "minotavr_eastern": [
                    "FullyLoaded", "SunsOut", "BeachDay", "ArmoredUp", "Tactical",
                    "Commando", "AllBusiness", "Spetsnaz", "Smoke", "SmokingOnTheJob",
                    "GunsOut", "Hidden", "Scales", "SquadLeader", "Valentaur"
                ],
                "bale_eastern": [
                    "Spetz", "Riot", "TwilightP", "UrbanCasualty", "Bleached",
                    "Sokoly", "TaskForce", "Brawler", "SnowForce", "Spetsnaz",
                    "AgentOrange", "Darkness", "Protectorate", "StoneFaced"
                ],
                "rodion_eastern": [
                    "HollywoodH", "Gungho", "NightRaid", "Recon", "WinterWear",
                    "HeavyDuty", "CasualFriday", "ShortSummers", "BurgerTown",
                    "Spetsnaz", "Incognito", "Infiltration", "Seaweed", "DeepSnow"
                ],
                "spetsnaz_eastern": ["Fixer"],
                "metalghost_eastern": [
                    "MetalPhantom", "Tombstone"
                ],
                "azur_eastern": [
                    "Smoked", "GreyedOut", "UrbanAssault", "Security", "Sheik",
                    "Nightshade", "DesertBandit", "SunBleached", "DuneBreaker",
                    "Jackals", "ArmsDealer", "Brawler", "RedReptile", "GreyMatter",
                    "BrothersKeeper"
                ],
                "grinch_eastern": [
                    "WarFace", "Wayward", "Feral", "JackalsGrinch", "Overgrowth",
                    "Webfoot", "Armadillo", "Bog", "MuddyWaters", "AllGhilliedUp",
                    "BloodInTheWater", "Nightfang"
                ],
                "zane_eastern": [
                    "Crusade", "Shades", "FatherTreason", "ZebraPrint", "Glitch",
                    "Vigilante", "Gbosa Green", "GreyedOut", "Polarized", "Striker",
                    "Jackals", "PepperDonRed", "MonsoonSeason", "Militant", "HoneyBadger"
                ],
                "yegor_eastern": [
                    "Cerulean", "Emerald", "Ruby", "OutOfTown", "SundayBest",
                    "Athleisure", "SuperStar", "BlackDrab", "Chimera", "TrackStar",
                    "NightLife", "FishBowl", "ChilledOut", "CoolBlue", "Commuter",
                    "Drawstring", "HardLabor", "ThiefInLaw", "ServiceRecord"
                ],
                "kreuger_eastern": [
                    "Phantom", "Shrouded", "SilentSigma", "Bandit", "Plague",
                    "MarshDemon", "Chimera", "Reaper", "Chemist", "Hazmat",
                    "ChemicalWarfare", "Waster", "Firestarter"
                ],
                "syd_eastern": [
                    "Mantis", "Embedded", "Judge", "Mariner", "Sahara", "Bluejacket",
                    "Chimera", "Thunderbird", "WoodlandCover", "Wetfoot", "Marathon"
                ],
                "iskra_eastern": ["Saboteur"]
            }
        }

        self.skins = {
            "default_western": [274, 816, 817, 818, 819, 820, 821, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836],
            "ghost_western": [136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153],
            "murphy_western": [154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171],
            "charly_western": [172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189],
            "otter_western": [190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207],
            "dday_western": [208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225],
            "alice_western": [226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243],
            "raines_western": [244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261],
            "crowfoot_western": [262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279],
            "domino_western": [280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297],
            "golem_western": [298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315],
            "zedra_western": [316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333],
            "wyatt_western": [334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351],
            "ronin_western": [352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369],
            "alex_western": [370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387],
            "lynch_western": [388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405],
            "default_eastern": [406],
            "minotavr_eastern": [407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424],
            "bale_eastern": [425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442],
            "rodion_eastern": [443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460],
            "spetsnaz_eastern": [461],
            "metalghost_eastern": [462, 463],
            "azur_eastern": [464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481],
            "grinch_eastern": [482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499],
            "zane_eastern": [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517],
            "yegor_eastern": [518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535],
            "kreuger_eastern": [536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553],
            "syd_eastern": [554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571],
            "iskra_eastern": [572]
        }

        self.finishing_moves = {
            "Bag'Em": 107,
            "ChipShot": 105,
            "CrickInTheNeck": 104,
            "FangsOut": 102,
            "Gutted": 93,
            "HelloStranger": 97,
            "Low Rise": 92,
            "Perforate": 94,
            "SpinCycle": 98,
            "ThreeStrikes": 91,
            "TopDog": 95,
            "UV09": 99,
            "UV10 (BushLeague)": 100,
            "UV11 (Karambit2)": 101,
            "UV13 (Payback)": 103,
            "UV16 (Bag'Em2)": 106,
            "WatchThis": 96
        }

        self.skin_name_to_id = {name: skin_id for category, skin_ids in self.skins.items() for name in self.operators.get(category, {}).get(category, []) for skin_id in skin_ids}

        self.create_ui()

    def create_ui(self):
        coalition_frame = tk.Frame(self.root)
        coalition_frame.grid(row=0, column=0, padx=10, pady=10)
        allegiance_frame = tk.Frame(self.root)
        allegiance_frame.grid(row=0, column=1, padx=10, pady=10)

        # Coalition operators
        coalition_label = tk.Label(coalition_frame, text="Select Coalition Operator")
        coalition_label.pack(padx=5, pady=5)

        self.coalition_operator_combobox = ttk.Combobox(coalition_frame, values=list(self.operators["Coalition"].keys()))
        self.coalition_operator_combobox.pack(padx=5, pady=5)
        self.coalition_operator_combobox.bind("<<ComboboxSelected>>", self.update_coalition_skins)

#        self.coalition_skin_combobox = ttk.Combobox(coalition_frame)
#        self.coalition_skin_combobox.pack(padx=5, pady=5)

        self.coalition_finishing_move_combobox = ttk.Combobox(coalition_frame, values=list(self.finishing_moves.keys()))
        self.coalition_finishing_move_combobox.pack(padx=5, pady=5)

        # Allegiance operators
        allegiance_label = tk.Label(allegiance_frame, text="Select Allegiance Operator")
        allegiance_label.pack(padx=5, pady=5)

        self.allegiance_operator_combobox = ttk.Combobox(allegiance_frame, values=list(self.operators["Allegiance"].keys()))
        self.allegiance_operator_combobox.pack(padx=5, pady=5)
        self.allegiance_operator_combobox.bind("<<ComboboxSelected>>", self.update_allegiance_skins)

#        self.allegiance_skin_combobox = ttk.Combobox(allegiance_frame)
#        self.allegiance_skin_combobox.pack(padx=5, pady=5)

        self.allegiance_finishing_move_combobox = ttk.Combobox(allegiance_frame, values=list(self.finishing_moves.keys()))
        self.allegiance_finishing_move_combobox.pack(padx=5, pady=5)

        save_button = tk.Button(self.root, text="Save", command=self.save_selection)
        save_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def get_skin_name_from_id(self, skin_id):
        for name, id_ in self.skin_name_to_id.items():
            if id_ == skin_id:
                return name
        return str(skin_id)

    def update_coalition_skins(self, event):
        operator = self.coalition_operator_combobox.get()
        if operator in self.operators["Coalition"]:
            skin_ids = self.skins.get(operator, [])
            skin_names = [self.get_skin_name_from_id(skin_id) for skin_id in skin_ids]

    def update_allegiance_skins(self, event):
        operator = self.allegiance_operator_combobox.get()
        if operator in self.operators["Allegiance"]:
            skin_ids = self.skins.get(operator, [])
            skin_names = [self.get_skin_name_from_id(skin_id) for skin_id in skin_ids]

#    def get_selected_coalition_skin_id(self):
#        selected_skin = self.coalition_skin_combobox.get()
#        return self.skin_name_to_id.get(selected_skin, None)

#    def get_selected_allegiance_skin_id(self):
# doesnt work        selected_skin = self.allegiance_skin_combobox.get()
#        return self.skin_name_to_id.get(selected_skin, None)

    def save_selection(self):
        file_path = os.path.join(self.backup_path, 'players', 'operators.cfg')
        
        selected_coalition_operator = self.coalition_operator_combobox.get()
# doesnt work        selected_coalition_skin_id = self.get_selected_coalition_skin_id()
        selected_coalition_finishing_move = self.coalition_finishing_move_combobox.get()
        
        selected_allegiance_operator = self.allegiance_operator_combobox.get()
# doesnt work        selected_allegiance_skin_id = self.get_selected_allegiance_skin_id()
        selected_allegiance_finishing_move = self.allegiance_finishing_move_combobox.get()
        
        with open(file_path, 'w') as file:
            if selected_coalition_operator:
                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operators 0 {selected_coalition_operator}\n")
#doesnt work            if selected_coalition_skin_id:
#doesnt work                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operatorCustomization {selected_coalition_operator} skin {selected_coalition_skin_id}\n")
            if selected_coalition_finishing_move:
                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operatorCustomization {selected_coalition_operator} execution {self.finishing_moves.get(selected_coalition_finishing_move, '')}\n")
            
            if selected_allegiance_operator:
                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operators 1 {selected_allegiance_operator}\n")
# doesnt work           if selected_allegiance_skin_id:
#                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operatorCustomization {selected_allegiance_operator} skin {selected_allegiance_skin_id}\n")
            if selected_allegiance_finishing_move:
                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operatorCustomization {selected_allegiance_operator} execution {self.finishing_moves.get(selected_allegiance_finishing_move, '')}\n")
    
