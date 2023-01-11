""" Samling av all information som programmet behöver kring vilka enheter som finns och vilka aktiviteter de har"""

GY_AKTIVITER = {"p": "410200", "e": "410600", "a": "410500", "n": "-1"}
GRU_AKTIVITER = {"p": "310200", "e": "310600", "a": "310500", "n": "-1"}

# DICT
ID_AKTIVITET = {"655119": GY_AKTIVITER,  # GY EK
                "655123": GY_AKTIVITER,  # GY ES
                "655122": GY_AKTIVITER,  # GY SA
                "656510": GRU_AKTIVITER,  # GRU 4-6
                "656520": GRU_AKTIVITER,  # GRU 7-9
                "656310": GRU_AKTIVITER,  # fritids
                "655125": GY_AKTIVITER,  # IMS går som GY
                "654100": GY_AKTIVITER,  # St:Lars ES- Musik
                "654200": GY_AKTIVITER,  # St:Lars ES- bild
                "654300": GY_AKTIVITER,  # St:Lars NA
                "654400": GY_AKTIVITER,  # St:Lars IMA
                "654500": GY_AKTIVITER  # St:Lars Slask ska inte användas
                }

ALLA_ENHETER = set(ID_AKTIVITET.keys())

# SET
ENHETER_SOM_HAR_CBS = {"655119",  # Gy EK
                       "655122",  # Gy ES
                       "655123",  # Gy SA
                       # "656510",  # 4-6
                       "656520",  # 7-9
                       # "656310",  # Fritids

                       "654100",  # Stlars Es Musik
                       "654200",  # Stlars Es Bild
                       "654300",  # Stlars NA
                       "654400"  # Stlars IMA
                       }

FOLKUNGA_GY_ENHETER = {"655119",  # Gy EK
                       "655122",  # Gy ES
                       "655123"  # Gy SA
                       }

FOLKUNGA_GRU_ENHETER = {"656510",  # 4-6
                        "656520"  # 7-9
                        # "656310" # Fritids har aldrig elever direkt
                        }
STLARS_ENHETER = {"654100",  # St:Lars ES- Musik
                  "654200",  # St:Lars ES- bild
                  "654300",  # St:Lars NA
                  "654400"  # St:Lars IMA
                  # "654500" # St:Lars Slask ska inte användas
                  }


