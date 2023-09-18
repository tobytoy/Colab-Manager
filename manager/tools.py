import numpy as np

def distance_map(ch_pt, r_pt):
    _diff = np.array(ch_pt) - np.array(r_pt)
    acc   = 0

    if type(_diff) is np.ndarray:
        for _ in _diff:
            acc += (_**2)
        _d = np.sqrt(acc)
        return _d, _diff

    elif type(_diff) is list:
        for _ in _diff:
            acc += (_**2)
        _d = np.sqrt(acc)
        return _d, _diff

    elif type(_diff) is tuple:
        for _ in _diff:
            acc += (_**2)
        _d = np.sqrt(acc)
        return _d, _diff

    else:
        return abs(_diff), _diff
    return abs(r_pt - ch_pt)

def changeAngleList(keypoints, k1, k2):
    _f = lambda pt1, pt2: float( np.angle( np.complex(pt2[1] - pt1[1], pt1[0] - pt2[0]) ) )
    return [_f(keypoint[k1], keypoint[k2])  for keypoint in keypoints]

def changeAngleLength(pt1, pt2):
    y1 = pt1[0]; x1 = pt1[1]
    y2 = pt2[0]; x2 = pt2[1]
    x_diff =     x2 - x1
    y_diff = - ( y2 - y1 )

    vector = np.complex(x_diff, y_diff)
    _angle  = float( np.angle(vector) )
    _length = float( (x_diff ** 2 + y_diff ** 2) ** (0.5) )
    return _angle, _length

def changeVector(pt1, pt2):
    y1 = pt1[0]; x1 = pt1[1]
    y2 = pt2[0]; x2 = pt2[1]
    x_diff = float(     x2 - x1   )
    y_diff = float( - ( y2 - y1 ) )
    return y_diff, x_diff

def next_coordinate_from_angle(y, x, _angle, _length):
    x_new = x + np.cos(_angle) * _length
    y_new = y - np.sin(_angle) * _length
    return y_new, x_new

def next_coordinate_from_vector(y, x, y_diff, x_diff):
    x_new = x + x_diff
    y_new = y - y_diff
    return y_new, x_new

# 對於肩膀 髖骨 互算
# 5, 6, 11, 12
def angleLengthTwice(keypoints, twice_list):
    twice_dictionary = {
        'al_13':{},
        'al_24':{},
        'al_31':{},
        'al_42':{},
    }
    index_1, index_2, index_3, index_4 = twice_list

    _keys = changeAngleLength(keypoints[index_1], keypoints[index_3])
    twice_dictionary['al_13']['angle']  = _keys[0]
    twice_dictionary['al_13']['length'] = _keys[1]

    _keys = changeAngleLength(keypoints[index_2], keypoints[index_4])
    twice_dictionary['al_24']['angle']  = _keys[0]
    twice_dictionary['al_24']['length'] = _keys[1]

    _keys = changeAngleLength(keypoints[index_3], keypoints[index_1])
    twice_dictionary['al_31']['angle']  = _keys[0]
    twice_dictionary['al_31']['length'] = _keys[1]

    _keys = changeAngleLength(keypoints[index_4], keypoints[index_2])
    twice_dictionary['al_42']['angle']  = _keys[0]
    twice_dictionary['al_42']['length'] = _keys[1]

    return twice_dictionary


def vectorTwice(keypoints, twice_list):
    twice_dictionary = {
        'al_13':{},
        'al_24':{},
        'al_31':{},
        'al_42':{},
    }
    index_1, index_2, index_3, index_4 = twice_list

    _keys = changeVector(keypoints[index_1], keypoints[index_3])
    twice_dictionary['al_13']['y_diff'] = _keys[0]
    twice_dictionary['al_13']['x_diff'] = _keys[1]

    _keys = changeVector(keypoints[index_2], keypoints[index_4])
    twice_dictionary['al_24']['y_diff'] = _keys[0]
    twice_dictionary['al_24']['x_diff'] = _keys[1]

    _keys = changeVector(keypoints[index_3], keypoints[index_1])
    twice_dictionary['al_31']['y_diff'] = _keys[0]
    twice_dictionary['al_31']['x_diff'] = _keys[1]

    _keys = changeVector(keypoints[index_4], keypoints[index_2])
    twice_dictionary['al_42']['y_diff'] = _keys[0]
    twice_dictionary['al_42']['x_diff'] = _keys[1]

    return twice_dictionary


def angleLengthVectorTwice(keypoints, twice_list):
    twice_dictionary = {
        'al_13':{},
        'al_24':{},
        'al_31':{},
        'al_42':{},
    }
    index_1, index_2, index_3, index_4 = twice_list

    _keys = changeAngleLength(keypoints[index_1], keypoints[index_3])
    twice_dictionary['al_13']['angle']  = _keys[0]
    twice_dictionary['al_13']['length'] = _keys[1]

    _keys = changeAngleLength(keypoints[index_2], keypoints[index_4])
    twice_dictionary['al_24']['angle']  = _keys[0]
    twice_dictionary['al_24']['length'] = _keys[1]

    _keys = changeAngleLength(keypoints[index_3], keypoints[index_1])
    twice_dictionary['al_31']['angle']  = _keys[0]
    twice_dictionary['al_31']['length'] = _keys[1]

    _keys = changeAngleLength(keypoints[index_4], keypoints[index_2])
    twice_dictionary['al_42']['angle']  = _keys[0]
    twice_dictionary['al_42']['length'] = _keys[1]

    _keys = changeVector(keypoints[index_1], keypoints[index_3])
    twice_dictionary['al_13']['y_diff'] = _keys[0]
    twice_dictionary['al_13']['x_diff'] = _keys[1]

    _keys = changeVector(keypoints[index_2], keypoints[index_4])
    twice_dictionary['al_24']['y_diff'] = _keys[0]
    twice_dictionary['al_24']['x_diff'] = _keys[1]

    _keys = changeVector(keypoints[index_3], keypoints[index_1])
    twice_dictionary['al_31']['y_diff'] = _keys[0]
    twice_dictionary['al_31']['x_diff'] = _keys[1]

    _keys = changeVector(keypoints[index_4], keypoints[index_2])
    twice_dictionary['al_42']['y_diff'] = _keys[0]
    twice_dictionary['al_42']['x_diff'] = _keys[1]

    return twice_dictionary

def angleLengthTriple(keypoints, triple_list):
    triple_dictionary = {
        'al_12':{},
        'al_23':{},
        'al_13':{},
    }
    index_1, index_2, index_3 = triple_list

    _keys = changeAngleLength(keypoints[index_1], keypoints[index_2])
    triple_dictionary['al_12']['angle']  = _keys[0]
    triple_dictionary['al_12']['length'] = _keys[1]

    _keys = changeAngleLength(keypoints[index_2], keypoints[index_3])
    triple_dictionary['al_23']['angle']  = _keys[0]
    triple_dictionary['al_23']['length'] = _keys[1]

    _keys = changeAngleLength(keypoints[index_1], keypoints[index_3])
    triple_dictionary['al_13']['angle']  = _keys[0]
    triple_dictionary['al_13']['length'] = _keys[1]

    return triple_dictionary

def vectorTriple(keypoints, triple_list):
    triple_dictionary = {
        'al_12':{},
        'al_23':{},
        'al_13':{},
    }
    index_1, index_2, index_3 = triple_list

    _keys = changeVector(keypoints[index_1], keypoints[index_2])
    triple_dictionary['al_12']['y_diff'] = _keys[0]
    triple_dictionary['al_12']['x_diff'] = _keys[1]

    _keys = changeVector(keypoints[index_2], keypoints[index_3])
    triple_dictionary['al_23']['y_diff'] = _keys[0]
    triple_dictionary['al_23']['x_diff'] = _keys[1]

    _keys = changeVector(keypoints[index_1], keypoints[index_3])
    triple_dictionary['al_13']['y_diff'] = _keys[0]
    triple_dictionary['al_13']['x_diff'] = _keys[1]

    return triple_dictionary

def angleLengthVectorTriple(keypoints, triple_list):
    triple_dictionary = {
        'al_12':{},
        'al_23':{},
        'al_13':{},
    }
    index_1, index_2, index_3 = triple_list

    _keys = changeAngleLength(keypoints[index_1], keypoints[index_2])
    triple_dictionary['al_12']['angle']  = _keys[0]
    triple_dictionary['al_12']['length'] = _keys[1]

    _keys = changeAngleLength(keypoints[index_2], keypoints[index_3])
    triple_dictionary['al_23']['angle']  = _keys[0]
    triple_dictionary['al_23']['length'] = _keys[1]

    _keys = changeAngleLength(keypoints[index_1], keypoints[index_3])
    triple_dictionary['al_13']['angle']  = _keys[0]
    triple_dictionary['al_13']['length'] = _keys[1]

    _keys = changeVector(keypoints[index_1], keypoints[index_2])
    triple_dictionary['al_12']['y_diff'] = _keys[0]
    triple_dictionary['al_12']['x_diff'] = _keys[1]

    _keys = changeVector(keypoints[index_2], keypoints[index_3])
    triple_dictionary['al_23']['y_diff'] = _keys[0]
    triple_dictionary['al_23']['x_diff'] = _keys[1]

    _keys = changeVector(keypoints[index_1], keypoints[index_3])
    triple_dictionary['al_13']['y_diff'] = _keys[0]
    triple_dictionary['al_13']['x_diff'] = _keys[1]

    return triple_dictionary

def changeWholeBodyAngleLengthDictionary(keypoints):
    whole_body_dictionary = {
        'left_arm'  : {},
        'right_arm' : {},
        'left_leg'  : {},
        'right_leg' : {},
        'body'      : {},
        'keypoints' : keypoints,
    }

    whole_body_dictionary['left_arm']  = angleLengthTriple(keypoints, (5,7,9))
    whole_body_dictionary['right_arm'] = angleLengthTriple(keypoints, (6,8,10))
    whole_body_dictionary['left_leg']  = angleLengthTriple(keypoints, (11,13,15))
    whole_body_dictionary['right_leg'] = angleLengthTriple(keypoints, (12,14,16))
    whole_body_dictionary['body']      = angleLengthTwice(keypoints , (5,6,11,12))

    return whole_body_dictionary

def changeWholeBodyVectorDictionary(keypoints):
    whole_body_dictionary = {
        'left_arm'  : {},
        'right_arm' : {},
        'left_leg'  : {},
        'right_leg' : {},
        'body'      : {},
        'keypoints' : keypoints,
    }

    whole_body_dictionary['left_arm']  = vectorTriple(keypoints, (5,7,9))
    whole_body_dictionary['right_arm'] = vectorTriple(keypoints, (6,8,10))
    whole_body_dictionary['left_leg']  = vectorTriple(keypoints, (11,13,15))
    whole_body_dictionary['right_leg'] = vectorTriple(keypoints, (12,14,16))
    whole_body_dictionary['body']      = vectorTwice(keypoints , (5,6,11,12))

    return whole_body_dictionary

def changeWholeBodyAngleLengthVectorDictionary(keypoints):
    whole_body_dictionary = {
        'left_arm'  : {},
        'right_arm' : {},
        'left_leg'  : {},
        'right_leg' : {},
        'body'      : {},
        'keypoints' : keypoints,
    }

    whole_body_dictionary['left_arm']  = angleLengthVectorTriple(keypoints, (5,7,9))
    whole_body_dictionary['right_arm'] = angleLengthVectorTriple(keypoints, (6,8,10))
    whole_body_dictionary['left_leg']  = angleLengthVectorTriple(keypoints, (11,13,15))
    whole_body_dictionary['right_leg'] = angleLengthVectorTriple(keypoints, (12,14,16))
    whole_body_dictionary['body']      = angleLengthVectorTwice(keypoints , (5,6,11,12))

    return whole_body_dictionary

