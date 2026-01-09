from skeletons.mixamo import MixamoSkeleton

ref_pose = {
    'root': (0, 0, 0),
    'mixamorig_Hips': (0.0365, 28.4712, 0.3773),
    'mixamorig_Spine': (0.0437, 31.2871, 0.2477),
    'mixamorig_Spine1': (-0.0246, 34.0407, -0.0367),
    'mixamorig_Spine2': (-0.0974, 36.6096, -0.2720),
    'mixamorig_Neck': (-0.2383, 41.2696, -0.5240),
    'mixamorig_Head': (-0.2768, 43.9052, 0.0751),
    'mixamorig_HeadTop_End': (-0.2204, 50.0000, 2.1683),
    'mixamorig_RightShoulder': (-1.4671, 39.6569, -0.5801),
    'mixamorig_RightArm': (-4.2276, 38.5962, -1.0867),
    'mixamorig_RightForeArm': (-5.4165, 30.9838, -0.8775),
    'mixamorig_RightHand': (-6.1759, 23.5113, 1.3781),
    'mixamorig_RightHandThumb1': (-5.6827, 23.0553, 2.2473),
    'mixamorig_RightHandThumb2': (-5.3951, 22.3850, 3.1489),
    'mixamorig_RightHandThumb3': (-5.2716, 21.5065, 3.4768),
    'mixamorig_RightHandThumb4': (-5.2650, 20.9674, 3.9431),
    'mixamorig_RightHandIndex1': (-6.2541, 21.4045, 2.9031),
    'mixamorig_RightHandIndex2': (-6.0202, 20.4453, 3.1755),
    'mixamorig_RightHandIndex3': (-5.4032, 19.9541, 3.1512),
    'mixamorig_RightHandIndex4': (-4.7002, 19.6751, 3.0211),
    'mixamorig_RightHandMiddle1': (-6.5534, 21.1094, 2.4040),
    'mixamorig_RightHandMiddle2': (-6.1259, 20.1892, 2.5442),
    'mixamorig_RightHandMiddle3': (-5.4267, 19.7822, 2.4323),
    'mixamorig_RightHandMiddle4': (-4.6658, 19.5579, 2.2425),
    'mixamorig_RightHandRing1': (-6.6442, 21.0335, 1.8875),
    'mixamorig_RightHandRing2': (-6.1840, 20.2201, 1.9295),
    'mixamorig_RightHandRing3': (-5.4992, 19.8360, 1.7764),
    'mixamorig_RightHandRing4': (-4.8172, 19.6829, 1.5640),
    'mixamorig_RightHandPinky1': (-6.6095, 21.0765, 1.2697),
    'mixamorig_RightHandPinky2': (-6.0561, 20.2525, 1.3590),
    'mixamorig_RightHandPinky3': (-5.5229, 20.0483, 1.2497),
    'mixamorig_RightHandPinky4': (-4.9731, 20.0925, 1.0526),
    'mixamorig_LeftShoulder': (1.0571, 39.7243, -0.7435),
    'mixamorig_LeftArm': (3.8169, 38.7672, -1.4285),
    'mixamorig_LeftForeArm': (5.1883, 31.1876, -1.7036),
    'mixamorig_LeftHand': (6.3753, 23.4805, -0.8700),
    'mixamorig_LeftHandThumb1': (5.8450, 22.7943, -0.1951),
    'mixamorig_LeftHandThumb2': (5.5996, 21.8464, 0.4253),
    'mixamorig_LeftHandThumb3': (5.4634, 20.9146, 0.5186),
    'mixamorig_LeftHandThumb4': (5.4616, 20.3337, 0.9345),
    'mixamorig_LeftHandIndex1': (6.5297, 21.0948, 0.1575),
    'mixamorig_LeftHandIndex2': (6.2732, 20.1032, 0.1452),
    'mixamorig_LeftHandIndex3': (5.7673, 19.5257, -0.0368),
    'mixamorig_LeftHandIndex4': (5.1565, 19.1359, -0.2919),
    'mixamorig_LeftHandMiddle1': (6.9149, 20.9502, -0.3490),
    'mixamorig_LeftHandMiddle2': (6.5478, 20.0051, -0.4948),
    'mixamorig_LeftHandMiddle3': (5.9517, 19.5241, -0.7780),
    'mixamorig_LeftHandMiddle4': (5.2461, 19.3061, -1.1286),
    'mixamorig_LeftHandRing1': (7.0707, 21.0035, -0.8527),
    'mixamorig_LeftHandRing2': (6.7673, 20.2078, -1.0403),
    'mixamorig_LeftHandRing3': (6.1194, 19.8686, -1.4038),
    'mixamorig_LeftHandRing4': (5.4858, 19.7580, -1.7533),
    'mixamorig_LeftHandPinky1': (7.0998, 21.1841, -1.4453),
    'mixamorig_LeftHandPinky2': (6.7779, 20.2525, -1.5922),
    'mixamorig_LeftHandPinky3': (6.3828, 19.8738, -1.7885),
    'mixamorig_LeftHandPinky4': (5.8924, 19.6649, -2.0377),
    'mixamorig_RightUpLeg': (-2.2605, 26.5911, 0.1744),
    'mixamorig_RightLeg': (-1.9643, 14.4011, 1.6591),
    'mixamorig_RightFoot': (-0.7460, 2.4167, -0.9562),
    'mixamorig_RightToeBase': (-1.2012, 0.0003, 1.9737),
    'mixamorig_RightToe_End': (-1.5949, 0.1407, 4.5080),
    'mixamorig_LeftUpLeg': (2.2766, 26.5677, -0.0823),
    'mixamorig_LeftLeg': (2.8265, 15.7142, 5.6435),
    'mixamorig_LeftFoot': (1.9961, 5.0910, -0.5540),
    'mixamorig_LeftToeBase': (2.1881, 1.6134, 1.0273),
    'mixamorig_LeftToe_End': (2.5888, 0.4910, 3.3026),
}

topology = MixamoSkeleton.TOPOLOGY
relative_offsets = {}

for bone, parent in topology.items():
    if parent is None:
        relative_offsets[bone] = ref_pose[bone]
    else:
        bx, by, bz = ref_pose[bone]
        px, py, pz = ref_pose[parent]
        relative_offsets[bone] = (bx - px, by - py, bz - pz)

import pprint
pprint.pprint(relative_offsets)
