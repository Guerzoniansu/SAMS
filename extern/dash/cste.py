crop_data = {
    # globally:
    # we define the total growth period estimates (tgp) for each crop
    # The repartition for days in each growth stage 
    # (Initial phase, crop development phase, middle season stage, late season stage)
    # and the crop factors (kc) for each phase
    # Should be noted that:
    # kc decreases by 0.05 when we face low RH2M (Relative Humidity at 2 meters) & low WS2M (WindSpeed at 2 meters)
    # kc increases by 0.05 when we face high RH2M (Relative Humidity at 2 meters) & high WS2M (WindSpeed at 2 meters)

    # High RH2M => RH2M>80%, Low RH2M => RH2M<50%, Medium RH2M => in between the two pre-cited values
    # High WS2M => WS2M>5m/sec, Low WS2M => WS2M<2m/sec, Medium WS2M => in between the two pre-cited values

    # For return on water needs, we make the general assumption that the tgp is the maximum
    # still unabling the user to enter the tgp (if he has that info)

    # planting date is also an issue when considering plant growth

    'whea': {'mintgp': 120, 'maxtgp': 150, 'gsmin': [15, 25, 50, 30], 'gsmax': [15, 30, 65, 40], 'kc': [0.35, 0.75, 1.15, 0.45]},
    'rice': {'mintgp': 90, 'maxtgp': 150,'kc': {
        'transplanting': 1.1, # 60 first days
        'mid-season': {
            'lwd': 1.2, # little wind dry
            'lwh': 1.05, # little wind humid
            'swd': 1.35, # strong wind dry
            'swh': 1.3 # strong wind humid
        }, # intermediary days (tgs - 60 - 30 = tgs - 90)
        'bharvest': 1.0 # 30 last days
    }},
    'maiz': {'mintgp': 125, 'maxtgp': 180, 'gsmin': [20, 35, 40, 30], 'gsmax': [30, 50, 60, 40], 'kc': [0.40, 0.80, 1.15, 0.70]},
    # 'barl': {'mintgp': 120, 'maxtgp': 150, 'gsmin': [15, 25, 50, 30], 'gsmax': [15, 30, 65, 40], 'kc': [0.35, 0.75, 1.10, 0.45]},
    'pmil': {'mintgp': 105, 'maxtgp': 140, 'gsmin': [15, 25, 40, 25], 'gsmax': [20, 30, 55, 35], 'kc': [0.35, 0.70, 1.10, 0.65]},
    'smil': {'mintgp': 105, 'maxtgp': 140, 'gsmin': [15, 25, 40, 25], 'gsmax': [20, 30, 55, 35], 'kc': [0.35, 0.75, 1.10, 0.65]},
    'sorg': {'mintgp': 120, 'maxtgp': 130, 'gsmin': [20, 30, 40, 30], 'gsmax': [20, 35, 45, 30], 'kc': [0.35, 0.75, 1.10, 0.65]},
    'pota': {'mintgp': 105, 'maxtgp': 145, 'gsmin': [25, 30, 30, 20], 'gsmax': [30, 35, 50, 30], 'kc': [0.45, 0.75, 1.15, 0.85]},
    'swpo': {'mintgp': 105, 'maxtgp': 145, 'gsmin': [25, 30, 30, 20], 'gsmax': [30, 35, 50, 30], 'kc': [0.45, 0.75, 1.10, 0.75]},
    # 'yams': {'mintgp': 345, 'maxtgp': 360, 'gsmin': [55, 150, 60, 80], 'gsmax': [60, 150, 60, 90], 'kc': [0.45, 0.75, 1.10, 0.70]},
    # 'cass': {'mintgp': 180, 'maxtgp': 270, 'gsmin': [15, 45, 30, 90], 'gsmax': [30, 60, 90, 90], 'kc': [0.45, 0.75, 1.10, 0.85]},
    # 'bean': {'mintgp': 95, 'maxtgp': 110, 'gsmin': [15, 25, 35, 20], 'gsmax': [20, 30, 40, 20], 'kc': [0.35, 0.70, 1.10, 0.90]},
    # 'chic': {'mintgp': 90, 'maxtgp': 100, 'gsmin': [15, 25, 35, 15], 'gsmax': [20, 30, 35, 15], 'kc': [0.45, 0.75, 1.10, 0.70]},
    # 'cowp': {'mintgp': 90, 'maxtgp': 100, 'gsmin': [15, 25, 35, 15], 'gsmax': [20, 30, 35, 15], 'kc': [0.35, 0.75, 1.10, 0.80]},
    # 'pige': {'mintgp': 90, 'maxtgp': 100, 'gsmin': [15, 25, 35, 15], 'gsmax': [20, 30, 35, 15], 'kc': [0.45, 0.75, 1.10, 0.60]},
    # 'lent': {'mintgp': 150, 'maxtgp': 170, 'gsmin': [20, 30, 60, 40], 'gsmax': [25, 35, 70, 40], 'kc': [0.45, 0.75, 1.10, 0.50]},
    # 'soyb': {'mintgp': 135, 'maxtgp': 150, 'gsmin': [20, 30, 60, 25], 'gsmax': [20, 30, 70, 30], 'kc': [0.35, 0.75, 1.10, 0.60]},
    # 'bana': {'mintgp': 300, 'maxtgp': 360, 'kc': [0.7, 0.75, 0.8, 0.75, 0.9, 1.0, 1.1]}, # The values of 1.1 is used for all months after the 7th
    # 'plnt': {'mintgp': 300, 'maxtgp': 360, 'kc': [0.7, 0.75, 0.8, 0.75, 0.9, 1.0, 1.1]},
    # 'sunf': {'mintgp': 125, 'maxtgp': 130, 'gsmin': [20, 35, 45, 25], 'gsmax': [35, 35, 45, 25], 'kc': [0.45, 0.75, 1.10, 0.50]},
    # 'sugb': {'mintgp': 160, 'maxtgp': 230, 'gsmin': [25, 35, 60, 40], 'gsmax': [45, 65, 80, 40], 'kc': [0.45, 0.75, 1.10, 0.70]},
    # 'cott': {'mintgp': 180, 'maxtgp': 195, 'gsmin': [30, 50, 55, 45], 'gsmax': [30, 50, 65, 50], 'kc': [0.45, 0.75, 1.10, 0.75]},
}


