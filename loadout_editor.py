import os
import re
import tkinter as tk
from tkinter import ttk

class LoadoutEditor:
    PRIMARY_WEAPONS = {
        "Kilo141 (HK433)": "iw8_ar_kilo433",
        "FAL": "iw8_ar_falima",
        "M4A1": "iw8_ar_mike4",
        "FR5.56 (FAMAS)": "iw8_ar_falpha",
        "Oden (ShAK-12)": "iw8_ar_asierra12",
        "M13 (MCX)": "iw8_ar_mcharlie",
        "FNScar17": "iw8_ar_scharlie",
        "Kilo47 (AK-47)": "iw8_ar_akilo47",
        "RAM-7 (Tavor)": "iw8_ar_tango21",
        "Grau (SG552)": "iw8_ar_sierra552",
        "CR 56 AMAX (UNRELEASED)": "iw8_ar_galima",
        "AUG": "iw8_sm_augolf",
        "P90": "iw8_sm_papa90",
        "MP5": "iw8_sm_mpapa5",
        "Uzi": "iw8_sm_uzulu",
        "PP19Bizon": "iw8_sm_beta",
        "MP7": "iw8_sm_mpapa7",
        "Striker45": "iw8_sm_smgolf45",
        "Vector (UNRELEASED)": "iw8_sm_victor",
        "ISO (UNRELEASED)": "iw8_sm_charlie9",
        "Model680": "iw8_sh_romeo870",
        "R9-0": "iw8_sh_dpapa12",
        "725": "iw8_sh_charlie725",
        "Origin12": "iw8_sh_oscar12",
        "VLKRogue": "iw8_sh_mike26",
        "PKM": "iw8_lm_pkilo",
        "SA87": "iw8_lm_lima86",
        "M91 (M240)": "iw8_lm_kilo121",
        "MG34": "iw8_lm_mgolf34",
        "Holger-26 (MG36)": "iw8_lm_mgolf36",
        "BruenMk9 (M249)": "iw8_lm_mkilo3",
        "EBR-14 (M14)": "iw8_sn_golf28",
        "MK2Carbine": "iw8_sn_sbeta",
        "Kar98K": "iw8_sn_kilo98",
        "Bugged EBR-14": "iw8_sn_mike14",
        "Crossbow": "iw8_sn_crossbow",
        "SKS": "iw8_sn_sksierra",
        "Dragunov": "iw8_sn_delta",
        "HDR": "iw8_sn_hdromeo",
        "AX-50": "iw8_sn_alpha50",
        "RiotShield": "iw8_me_riotshield"
    }

    SECONDARY_WEAPONS = {
        "X16 (Glock21)": "iw8_pi_golf21",
        "1911": "iw8_pi_mike1911",
        ".357 (M586)": "iw8_pi_cpapa",
        "M19 (M18)": "iw8_pi_papa320",
        ".50GS (DEagle)": "iw8_pi_decho",
        "Renetti (M9)": "iw8_pi_mike9",
        "PILA": "iw8_la_gromeo",
        "Strela-P (CarlG)": "iw8_la_kgolf",
        "JOKR (Javelin)": "iw8_la_juliet",
        "RPG-7": "iw8_la_rpapa7",
        "Fists": "iw8_fists",
        "CombatKnife": "iw8_knife"
    }

    def __init__(self, master, backup_path):
        self.master = master
        self.file_path = os.path.join(backup_path, 'players', 'loadouts.cfg')
        self.weapon_vars = []

        self.master.title("Loadout Editor")
        self.master.geometry("650x350")
        self.master.resizable(False, False)

        self.setup_gui()
        self.load_loadouts()

    def setup_gui(self):
        tk.Label(self.master, text="Primary Weapons").grid(row=0, column=0, columnspan=2)
        tk.Label(self.master, text="Secondary Weapons").grid(row=0, column=2, columnspan=2)

        for i in range(10):
            tk.Label(self.master, text=f"Loadout {i+1} Primary Weapon:").grid(row=i+1, column=0)
            primary_var = tk.StringVar()
            secondary_var = tk.StringVar()
            self.weapon_vars.append((primary_var, secondary_var))

            primary_menu = ttk.Combobox(
                self.master,
                textvariable=primary_var,
                values=list(self.PRIMARY_WEAPONS.keys()),
                state='readonly'
            )
            primary_menu.grid(row=i+1, column=1)
            primary_menu.current(0)

            tk.Label(self.master, text=f"Loadout {i+1} Secondary Weapon:").grid(row=i+1, column=2)
            secondary_menu = ttk.Combobox(
                self.master,
                textvariable=secondary_var,
                values=list(self.SECONDARY_WEAPONS.keys()),
                state='readonly'
            )
            secondary_menu.grid(row=i+1, column=3)
            secondary_menu.current(0)

        tk.Button(
            self.master,
            text="Update Loadouts",
            command=self.on_update_loadouts
        ).grid(row=11, column=1, columnspan=2, pady=10)

    def load_loadouts(self):
        loadouts = self.read_loadouts()
        for i in range(10):
            primary_weapon = loadouts.get(f'Loadout {i+1}', {}).get('Primary', 'None')
            secondary_weapon = loadouts.get(f'Loadout {i+1}', {}).get('Secondary', 'None')
            self.weapon_vars[i][0].set(primary_weapon)
            self.weapon_vars[i][1].set(secondary_weapon)

    def read_loadouts(self):
        loadouts = {}
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    for i in range(10):
                        loadout_key = f'setPrivateLoadout loadouts {i} weaponSetups'
                        primary_match = re.search(f'{loadout_key} 0 weapon (iw8_[^\\s]+)', content)
                        secondary_match = re.search(f'{loadout_key} 1 weapon (iw8_[^\\s]+)', content)

                        primary_weapon_id = primary_match.group(1) if primary_match else None
                        secondary_weapon_id = secondary_match.group(1) if secondary_match else None

                        primary_weapon = next((k for k, v in self.PRIMARY_WEAPONS.items() if v == primary_weapon_id), 'None')
                        secondary_weapon = next((k for k, v in self.SECONDARY_WEAPONS.items() if v == secondary_weapon_id), 'None')

                        loadouts[f'Loadout {i+1}'] = {
                            'Primary': primary_weapon,
                            'Secondary': secondary_weapon
                        }
            except Exception as e:
                print(f"Error reading file: {e}")
        return loadouts

    def save_loadouts(self, loadouts):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as file:
                for i in range(10):
                    primary_weapon_id = self.PRIMARY_WEAPONS.get(loadouts[f'Loadout {i+1}']['Primary'], 'iw8_ar_kilo433')
                    secondary_weapon_id = self.SECONDARY_WEAPONS.get(loadouts[f'Loadout {i+1}']['Secondary'], 'iw8_pi_mike1911')

                    file.write(f'setPrivateLoadout loadouts {i} weaponSetups 0 weapon {primary_weapon_id}\n')
                    file.write(f'setPrivateLoadout loadouts {i} weaponSetups 1 weapon {secondary_weapon_id}\n')
        except Exception as e:
            print(f"Error writing file: {e}")

    def on_update_loadouts(self):
        current_loadouts = self.read_loadouts()
        for i in range(10):
            primary_weapon = self.weapon_vars[i][0].get()
            secondary_weapon = self.weapon_vars[i][1].get()
            current_loadouts[f'Loadout {i+1}']['Primary'] = primary_weapon
            current_loadouts[f'Loadout {i+1}']['Secondary'] = secondary_weapon
        self.save_loadouts(current_loadouts)
