DAY_INBOUND = {
    'DAY': 'DAY', 
    'INBOUND': 'INBOUND'
}

AGENCY_CHOICES = {
    'PA': 'PA',
    'RH': 'RH',
    'NLK': 'NLK',
    'HN': 'HN',
    'HJ': 'HJ', 
    'SSK': 'SSK',
    'HT': 'HT', 
    'TA': 'TA',
    'LOC': 'LOC',
}

RESTAURANT_CHOICES = [
    ('홍대', '홍대'),
    ('대장금', '대장금'),
    ('OAK & VINE', 'OAK & VINE'),  
    ('CELLAR DOOR', 'CELLAR DOOR'), 
    ('LA PORCHETTA', 'LA PORCHETTA'), 
    ('FUSION SPACE', 'FUSION SPACE'), 
    ('FEAST BUFFET', 'FEAST BUFFET'), 
    ('BANG POP', 'BANG POP'),
    ('WING LOCK', 'WING LOCK'),
    ('ROCHFORD', 'ROCHFORD'),
    ('OTHERS', 'OTHERS')
]

ATTRACTION_CHOICES = [
    ('PUFFING BILLY', 'PUFFING BILLY'), 
    ('PENGUIN PARADE', 'PENGUIN PARADE'), 
    ('PENINSULA', 'PENINSULA'), 
    ('HELI 15min', 'HELI 15min'), 
    ('PENGUINE PARADE', 'PENGUINE PARADE'), 
    ('CRUISE', 'CRUISE'), 
    ('EUREKA', 'EUREKA'), 
    ('WINE TASTING', 'WINE TASTING')
]

EXPENSE_CHOICES = [
    ('WASH', 'Car Wash'),
    ('PARK', 'Parking'),
    ('ETC', 'ETC'),
]

GUIDE_ONLY_EXPENSE_CHOICES = [
    ('ETC', 'ETC')
]

DAY_ROLE = {
    '12 SEAT': '12 SEAT',
    '21 SEAT': '21 SEAT', 
    '53 SEAT': '53 SEAT', 
    'GUIDE ONLY': 'GUIDE ONLY'
}

INBOUND_ROLE = {
    'FIT': 'FIT', 
    'GROUP': 'GROUP',
}

COACH_TYPE = {
    '12 SEAT': '12 SEAT',
    '21 SEAT': '21 SEAT',
    '53 SEAT': '53 SEAT',
    'GUIDE ONLY': 'GUIDE ONLY'
}

DAY_EVENTCODE_12SEAT = {
    'GOR': 'GOR', 
    'ZGOR': 'ZGOR', 
    'PP': 'PP', 
    'PP(PEAK)': 'PP(PEAK)', 
    'PB': 'PB', 
    'PI': 'PI', 
    'SOV': 'SOV',
    'PPT': 'PPT', 
    'MON': 'MON', 
    'WN': 'WN',
    'AP/AD': 'AP/AD',
    'AM/AS': 'AM/AS',
    'OTHERS': 'OTHERS'
}

DAY_EVENTCODE_21SEAT = {
    'GOR': 'GOR', 
    'PP': 'PP', 
    'PP(PEAK)': 'PP(PEAK)',
    'PB': 'PB', 
    'PI': 'PI', 
    'SOV': 'SOV',
    'MON': 'MON', 
    'WN': 'WN',
    'AP/AD': 'AP/AD',
    'AM/AS': 'AM/AS',
    'OTHERS': 'OTHERS'
}

DAY_EVENTCODE_53SEAT = {
    'GOR': 'GOR', 
    'PP': 'PP', 
    'PP(PEAK)': 'PP(PEAK)', 
    'PB': 'PB', 
    'PI': 'PI', 
    'SOV': 'SOV',
    'WN': 'WN',
    'AP/AD': 'AP/AD',
    'AM/AS': 'AM/AS',
    'OTHERS': 'OTHERS'
}

DAY_EVENTCODE_GUIDE_ONLY = {
    'CT': 'CT'
}

INBOUND_EVENTCODE = {
    ('GOR', 'GOR'), 
    ('PP', 'PP'), 
    ('PP(PEAK)', 'PP(PEAK)'), 
    ('PB', 'PB'), 
    ('PI', 'PI'),
    ('SOV', 'SOV'),
    ('MON', 'MON'), 
    ('WN', 'WN'),
    ('YV', 'YV'),
    ('AM/AS', 'AM/AS'),
    ('OTHERS', 'OTHERS'),
}

INBOUND_HOURS = {
    'AM/AS': 'AM/AS',
    '6HRS': '6HRS', 
    '10HRS': '10HRS', 
    '12HRS': '12HRS',
}

DAY_RATE_12SEAT = {
    'GOR': [300, 309, 318, 327, 336], 
    'ZGOR': [313, 322, 331, 341, 350], 
    'PP': [300, 309, 318, 327, 336], 
    'PP(PEAK)': [338, 348, 358, 368, 378], 
    'PB': [138, 142, 146, 150, 154], 
    'PI': [225, 231, 238, 245, 252],
    'SOV': [213, 219, 225, 232, 238],
    'WN': [213, 219, 225, 232, 238], 
    'PPT': [90, 90, 90, 90, 90], 
    'MON': [213, 219, 225, 232, 238], 
    'AP/AD': [50, 50, 50, 50, 50],
    'AM/AS': [80, 80, 80, 80, 80],
    'OTHERS': [0, 0, 0, 0, 0]
}

SPONSORED_DAY_RATE_12SEAT = {
    'GOR': [273, 281, 289, 297, 305],
    'ZGOR': [285, 293, 302, 310, 319],
    'PP': [273, 281, 289, 297, 305],
    'PP(PEAK)': [307, 316, 325, 334, 343],
    'PB': [125, 128, 132, 136, 140],
    'PI': [205, 211, 217, 223, 229],
    'SOV': [205, 211, 217, 223, 229],
    'WN': [205, 211, 217, 223, 229], 
    'PPT': [82, 82, 82, 82, 82],
    'MON': [194, 199, 205, 211, 217],
    'AP/AD': [50, 50, 50, 50, 50],
    'AM/AS': [73, 73, 73, 73, 73],
}

DAY_RATE_21SEAT = {
    'GOR': [324, 333, 343, 353, 362], 
    'PP': [324, 333, 343, 353, 362], 
    'PP(PEAK)': [365, 375, 386, 397, 408], 
    'PB': [149, 153, 157, 162, 166], 
    'PI': [243, 250, 257, 264, 272], 
    'SOV': [230, 236, 243, 250, 257],
    'WN': [230, 236, 243, 250, 257],
    'MON': [230, 236, 243, 250, 257], 
    'AP/AD': [55, 55, 55, 55, 55],
    'AM/AS': [80, 80, 80, 80, 80]
}

SPONSORED_DAY_RATE_21SEAT = {
    'GOR': [295, 303, 312, 321, 330],
    'ZGOR': [307, 317, 326, 335, 344],
    'PP': [295, 303, 312, 321, 330],
    'PP(PEAK)': [332, 341, 351, 361, 371],
    'PB': [135, 139, 143, 147, 151],
    'PI': [221, 227, 234, 240, 247],
    'SOV': [221, 227, 234, 240, 247],
    'PPT': [82, 82, 82, 82, 82],
    'MON': [209, 215, 221, 227, 234],
    'AP/AD': [55, 55, 55, 55, 55],
    'AM/AS': [73, 73, 73, 73, 73],
}

DAY_RATE_53SEAT = {
    'GOR': [403, 415, 427, 439, 451], 
    'PP': [372, 383, 394, 405, 416], 
    'PP(PEAK)': [419, 431, 444, 456, 469], 
    'PB': [171, 176, 181, 186, 191], 
    'PI': [279, 287, 295, 304, 312], 
    'SOV': [264, 271, 279, 287, 295],
    'WN': [264, 271, 279, 287, 295],
    'AP/AD': [60, 60, 60, 60, 60], 
    'AM/AS': [80, 80, 80, 80, 80]
}

SPONSORED_DAY_RATE_53SEAT = {
    'GOR': [367, 378, 389, 400, 411],
    'PP': [339, 349, 359, 369, 379],
    'PP(PEAK)': [381, 392, 403, 415, 426],
    'PB': [155, 159, 164, 168, 173],
    'PI': [254, 261, 269, 276, 284],
    'SOV': [254, 261, 269, 276, 284],
    'WN': [254, 261, 269, 276, 284], 
    'AP/AD': [60, 60, 60, 60, 60],
    'AM/AS': [73, 73, 73, 73, 73]
}

DAY_RATE_GUIDE_ONLY = {
    'CT': [63, 64, 66, 68, 70]
}

SPONSORED_DAY_RATE_GUIDE_ONLY = {
    'CT': [57, 58, 60, 62, 63]
}

INBOUND_RATE_12SEAT = {
    'AM/AS': [80, 80, 80, 80, 80], 
    '6HRS': [160, 164, 169, 174, 179], 
    '10HRS': [260, 267, 275, 283, 291], 
    '12HRS': [310, 319, 328, 337, 347]
}

SPONSORED_INBOUND_RATE_12SEAT = {
    'AM/AS': [73, 73, 73, 73, 73],
    '6HRS': [146, 150, 154, 159, 163],
    '10HRS': [237, 244, 251, 258, 265],
    '12HRS': [282, 290, 298, 307, 315]
}

INBOUND_RATE_GUIDE_ONLY = {
    'AM/AS': [80, 80, 80, 80, 80], 
    '6HRS': [140, 144, 148, 152, 156], 
    '10HRS': [250, 257, 265, 272, 280], 
    '12HRS': [290, 298, 307, 316, 324]
}

SPONSORED_INBOUND_RATE_GUIDE_ONLY = {
    'AM/AS': [73, 73, 73, 73, 73],
    '6HRS': [128, 131, 135, 139, 143],
    '10HRS': [228, 234, 241, 248, 255],
    '12HRS': [264, 271, 279, 287, 295]
}