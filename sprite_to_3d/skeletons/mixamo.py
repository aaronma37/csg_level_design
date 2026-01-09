import numpy as np

class MixamoSkeleton:
    TOPOLOGY = {
        'root': None,
        'mixamorig_Hips': 'root',
        'mixamorig_Spine': 'mixamorig_Hips',
        'mixamorig_Spine1': 'mixamorig_Spine',
        'mixamorig_Spine2': 'mixamorig_Spine1',
        'mixamorig_Neck': 'mixamorig_Spine2',
        'mixamorig_Head': 'mixamorig_Neck',
        'mixamorig_HeadTop_End': 'mixamorig_Head',
        'mixamorig_RightShoulder': 'mixamorig_Spine2',
        'mixamorig_RightArm': 'mixamorig_RightShoulder',
        'mixamorig_RightForeArm': 'mixamorig_RightArm',
        'mixamorig_RightHand': 'mixamorig_RightForeArm',
        'mixamorig_RightHandThumb1': 'mixamorig_RightHand',
        'mixamorig_RightHandThumb2': 'mixamorig_RightHandThumb1',
        'mixamorig_RightHandThumb3': 'mixamorig_RightHandThumb2',
        'mixamorig_RightHandThumb4': 'mixamorig_RightHandThumb3',
        'mixamorig_RightHandIndex1': 'mixamorig_RightHand',
        'mixamorig_RightHandIndex2': 'mixamorig_RightHandIndex1',
        'mixamorig_RightHandIndex3': 'mixamorig_RightHandIndex2',
        'mixamorig_RightHandIndex4': 'mixamorig_RightHandIndex3',
        'mixamorig_RightHandMiddle1': 'mixamorig_RightHand',
        'mixamorig_RightHandMiddle2': 'mixamorig_RightHandMiddle1',
        'mixamorig_RightHandMiddle3': 'mixamorig_RightHandMiddle2',
        'mixamorig_RightHandMiddle4': 'mixamorig_RightHandMiddle3',
        'mixamorig_RightHandRing1': 'mixamorig_RightHand',
        'mixamorig_RightHandRing2': 'mixamorig_RightHandRing1',
        'mixamorig_RightHandRing3': 'mixamorig_RightHandRing2',
        'mixamorig_RightHandRing4': 'mixamorig_RightHandRing3',
        'mixamorig_RightHandPinky1': 'mixamorig_RightHand',
        'mixamorig_RightHandPinky2': 'mixamorig_RightHandPinky1',
        'mixamorig_RightHandPinky3': 'mixamorig_RightHandPinky2',
        'mixamorig_RightHandPinky4': 'mixamorig_RightHandPinky3',
        'mixamorig_LeftShoulder': 'mixamorig_Spine2',
        'mixamorig_LeftArm': 'mixamorig_LeftShoulder',
        'mixamorig_LeftForeArm': 'mixamorig_LeftArm',
        'mixamorig_LeftHand': 'mixamorig_LeftForeArm',
        'mixamorig_LeftHandThumb1': 'mixamorig_LeftHand',
        'mixamorig_LeftHandThumb2': 'mixamorig_LeftHandThumb1',
        'mixamorig_LeftHandThumb3': 'mixamorig_LeftHandThumb2',
        'mixamorig_LeftHandThumb4': 'mixamorig_LeftHandThumb3',
        'mixamorig_LeftHandIndex1': 'mixamorig_LeftHand',
        'mixamorig_LeftHandIndex2': 'mixamorig_LeftHandIndex1',
        'mixamorig_LeftHandIndex3': 'mixamorig_LeftHandIndex2',
        'mixamorig_LeftHandIndex4': 'mixamorig_LeftHandIndex3',
        'mixamorig_LeftHandMiddle1': 'mixamorig_LeftHand',
        'mixamorig_LeftHandMiddle2': 'mixamorig_LeftHandMiddle1',
        'mixamorig_LeftHandMiddle3': 'mixamorig_LeftHandMiddle2',
        'mixamorig_LeftHandMiddle4': 'mixamorig_LeftHandMiddle3',
        'mixamorig_LeftHandRing1': 'mixamorig_LeftHand',
        'mixamorig_LeftHandRing2': 'mixamorig_LeftHandRing1',
        'mixamorig_LeftHandRing3': 'mixamorig_LeftHandRing2',
        'mixamorig_LeftHandRing4': 'mixamorig_LeftHandRing3',
        'mixamorig_LeftHandPinky1': 'mixamorig_LeftHand',
        'mixamorig_LeftHandPinky2': 'mixamorig_LeftHandPinky1',
        'mixamorig_LeftHandPinky3': 'mixamorig_LeftHandPinky2',
        'mixamorig_LeftHandPinky4': 'mixamorig_LeftHandPinky3',
        'mixamorig_RightUpLeg': 'mixamorig_Hips',
        'mixamorig_RightLeg': 'mixamorig_RightUpLeg',
        'mixamorig_RightFoot': 'mixamorig_RightLeg',
        'mixamorig_RightToeBase': 'mixamorig_RightFoot',
        'mixamorig_RightToe_End': 'mixamorig_RightToeBase',
        'mixamorig_LeftUpLeg': 'mixamorig_Hips',
        'mixamorig_LeftLeg': 'mixamorig_LeftUpLeg',
        'mixamorig_LeftFoot': 'mixamorig_LeftLeg',
        'mixamorig_LeftToeBase': 'mixamorig_LeftFoot',
        'mixamorig_LeftToe_End': 'mixamorig_LeftToeBase',
    }

    BIND_MATRICES = {
        'mixamorig_Hips': [0.998391, 0.002547, 0.056656, 0.036500, -0.005147, 0.998938, 0.045786, 28.471235, -0.056479, -0.046004, 0.997343, 0.377341, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_Spine': [0.999709, -0.023933, 0.002861, 0.000000, 0.023725, 0.998013, 0.058378, 2.818849, -0.004252, -0.058293, 0.998290, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_Spine1': [0.999990, -0.004262, 0.001060, 0.000000, 0.004273, 0.999927, -0.011333, 2.769102, -0.001011, 0.011337, 0.999935, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_Spine2': [0.999990, -0.004229, 0.001093, 0.000000, 0.004266, 0.999302, -0.037100, 2.580688, -0.000935, 0.037104, 0.999311, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_Neck': [0.999972, -0.000356, -0.007416, 0.000000, 0.000485, 0.999850, 0.017318, 4.668913, 0.007409, -0.017321, 0.999823, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_Head': [0.996739, 0.048978, -0.064126, -0.000000, -0.045928, 0.997781, 0.048207, 2.586169, 0.066344, -0.045105, 0.996777, 0.786490, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_HeadTop_End': [1.000000, -0.000000, 0.000000, 0.000000, -0.000000, 1.000000, 0.000000, 5.803246, 0.000000, 0.000000, 1.000000, 2.802378, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightShoulder': [-0.187110, -0.916348, 0.353973, -1.265138, -0.205043, -0.315969, -0.926348, 3.099394, 0.960702, -0.245908, -0.128769, -0.223295, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightArm': [0.938921, 0.199229, -0.280596, 0.000000, -0.343325, 0.486490, -0.803402, 3.000398, -0.023554, 0.850667, 0.525176, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightForeArm': [0.963818, 0.266560, -0.000000, 0.000000, -0.266560, 0.963818, 0.000000, 7.707514, 0.000000, -0.000000, 1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHand': [0.995357, 0.095396, 0.012779, 0.000000, -0.096060, 0.992908, 0.070041, 7.842416, -0.006007, -0.070944, 0.997462, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandThumb1': [0.820682, 0.559676, 0.115077, 0.742445, -0.489833, 0.792826, -0.362615, 0.682344, -0.294183, 0.241223, 0.924807, 0.435739, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandThumb2': [0.839211, -0.536490, -0.088897, 0.000000, 0.541867, 0.838761, 0.053480, 1.159664, 0.045872, -0.093051, 0.994604, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandThumb3': [0.940120, 0.325725, -0.100388, 0.000000, -0.299945, 0.930505, 0.210224, 0.945753, 0.161887, -0.167525, 0.972486, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandThumb4': [0.967631, 0.095337, -0.233668, 0.000000, -0.098051, 0.995181, 0.000001, 0.712851, 0.232542, 0.022911, 0.972316, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandIndex1': [0.999181, -0.034811, 0.020636, 0.625593, 0.040059, 0.923123, -0.382412, 2.521500, -0.005738, 0.382925, 0.923762, 0.143373, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandIndex2': [0.998374, -0.053392, 0.019957, 0.000000, 0.053393, 0.753413, -0.655377, 1.024291, 0.019956, 0.655377, 0.755038, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandIndex3': [0.999656, -0.025874, 0.004219, -0.000000, 0.025874, 0.947875, -0.317591, 0.788981, 0.004219, 0.317591, 0.948218, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandIndex4': [0.999998, -0.000175, 0.002005, 0.000000, 0.000175, 1.000000, 0.000000, 0.767443, -0.002005, -0.000000, 0.999998, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandMiddle1': [0.994783, -0.094964, 0.037255, 0.000000, 0.099020, 0.811143, -0.576405, 2.638934, 0.024518, 0.577087, 0.816315, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandMiddle2': [0.998591, -0.050170, 0.017296, 0.000000, 0.050170, 0.786284, -0.615825, 1.024291, 0.017296, 0.615825, 0.787693, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandMiddle3': [0.999786, -0.020520, 0.002627, 0.000000, 0.020520, 0.967543, -0.251871, 0.816665, 0.002627, 0.251871, 0.967757, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandMiddle4': [0.999998, -0.000333, 0.001857, 0.000000, 0.000333, 1.000000, 0.000001, 0.815723, -0.001857, 0.000000, 0.999998, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandRing1': [0.987477, -0.150982, 0.045760, -0.516326, 0.143439, 0.738441, -0.658886, 2.520199, 0.065689, 0.657198, 0.750850, 0.011932, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandRing2': [0.998879, -0.045285, 0.013755, 0.000000, 0.045285, 0.830043, -0.555858, 0.935510, 0.013755, 0.555858, 0.831163, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandRing3': [0.999706, -0.023978, 0.003609, 0.000000, 0.023978, 0.955406, -0.294320, 0.799971, 0.003609, 0.294320, 0.955700, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandRing4': [0.999999, 0.001599, 0.000291, 0.000000, -0.001599, 0.999999, -0.000000, 0.730513, -0.000291, 0.000000, 1.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandPinky1': [0.995432, -0.080860, 0.050763, -1.053719, 0.093210, 0.707964, -0.700070, 2.235917, 0.020669, 0.701604, 0.712267, 0.134736, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandPinky2': [0.998568, -0.050520, 0.017572, 0.000000, 0.050520, 0.782880, -0.620118, 0.996608, 0.017572, 0.620118, 0.784312, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandPinky3': [0.999325, -0.035778, 0.008279, 0.000000, 0.035778, 0.897697, -0.439159, 0.581354, 0.008280, 0.439159, 0.898371, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightHandPinky4': [0.999995, 0.000082, 0.003138, -0.000000, -0.000082, 1.000000, -0.000000, 0.585728, -0.003138, 0.000000, 0.999995, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftShoulder': [-0.123334, 0.923823, -0.362409, 1.265249, 0.203776, -0.333838, -0.920341, 3.099339, -0.971218, -0.187359, -0.147079, -0.223295, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftArm': [0.931310, -0.142709, 0.335106, 0.000000, 0.360906, 0.485536, -0.796242, 3.000260, -0.049075, 0.862490, 0.503689, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftForeArm': [0.989566, -0.144079, -0.000000, 0.000000, 0.144079, 0.989566, 0.000000, 7.707514, 0.000000, -0.000000, 1.000000, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHand': [0.982666, -0.080567, 0.166961, 0.000000, 0.067126, 0.994147, 0.084646, 7.842416, -0.172803, -0.071971, 0.982323, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandThumb1': [0.875704, -0.481063, -0.041481, -0.742390, 0.451613, 0.846424, -0.282156, 0.682704, 0.170846, 0.228352, 0.958471, 0.436348, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandThumb2': [0.891382, 0.452186, 0.031072, 0.000000, -0.447099, 0.888470, -0.103554, 1.159138, -0.074432, 0.078414, 0.994138, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandThumb3': [0.908965, -0.407160, -0.089458, -0.000000, 0.414283, 0.858398, 0.302528, 0.946334, -0.046387, -0.312048, 0.948933, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandThumb4': [0.966428, -0.081336, 0.243724, 0.000000, 0.083865, 0.996477, 0.000001, 0.714402, -0.242865, 0.020439, 0.969845, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandIndex1': [0.999161, 0.026090, -0.031577, -0.625620, -0.038114, 0.874562, -0.483413, 2.521777, 0.015003, 0.484211, 0.874823, 0.143401, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandIndex2': [0.998668, 0.049928, -0.012996, -0.000000, -0.049928, 0.871855, -0.487213, 1.024291, -0.012995, 0.487213, 0.873186, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandIndex3': [0.999562, 0.029286, -0.004275, 0.000000, -0.029286, 0.957847, -0.285782, 0.788981, -0.004274, 0.285782, 0.958285, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandIndex4': [1.000000, 0.000026, -0.000756, -0.000000, -0.000026, 1.000000, 0.000000, 0.768191, 0.000756, 0.000000, 1.000000, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandMiddle1': [0.993777, 0.101455, -0.045971, -0.000000, -0.108279, 0.783187, -0.612285, 2.639183, -0.026115, 0.613453, 0.789299, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandMiddle2': [0.998487, 0.052963, -0.014762, 0.000000, -0.052964, 0.854446, -0.516833, 1.024291, -0.014760, 0.516833, 0.855959, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandMiddle3': [0.999333, 0.035937, -0.006511, 0.000000, -0.035937, 0.935803, -0.350687, 0.816665, -0.006510, 0.350687, 0.936470, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandMiddle4': [0.999998, -0.000056, -0.002049, 0.000000, 0.000056, 1.000000, -0.000000, 0.817467, 0.002049, -0.000000, 0.999998, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandRing1': [0.984064, 0.171329, -0.047592, 0.516326, -0.162893, 0.761254, -0.627661, 2.520448, -0.071307, 0.625411, 0.777031, 0.011904, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandRing2': [0.997410, 0.067343, -0.025279, 0.000000, -0.067343, 0.750743, -0.657152, 0.872032, -0.025277, 0.657153, 0.753334, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandRing3': [0.999605, 0.027850, -0.003858, 0.000000, -0.027850, 0.961959, -0.271771, 0.816665, -0.003857, 0.271771, 0.962354, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandRing4': [1.000000, -0.000031, 0.000986, 0.000000, 0.000031, 1.000000, 0.000000, 0.732036, -0.000986, 0.000000, 1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandPinky1': [0.991689, 0.120519, -0.045034, 1.053719, -0.123950, 0.801142, -0.585497, 2.236221, -0.034485, 0.586213, 0.809422, 0.134791, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandPinky2': [0.998734, 0.048768, -0.012358, 0.000000, -0.048768, 0.878150, -0.475892, 0.996608, -0.012356, 0.475892, 0.879417, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandPinky3': [0.999383, 0.034613, -0.006025, 0.000000, -0.034614, 0.940592, -0.337770, 0.581354, -0.006024, 0.337770, 0.941209, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftHandPinky4': [0.999999, 0.000590, -0.001567, 0.000000, -0.000590, 1.000000, -0.000001, 0.588414, 0.001567, 0.000002, 0.999999, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightUpLeg': [-0.984671, 0.022359, -0.172982, -2.272210, -0.035194, -0.996820, 0.071489, -1.874674, -0.170833, 0.076481, 0.982327, -0.418631, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightLeg': [0.998655, -0.037261, 0.036051, -0.000000, 0.022997, 0.941547, 0.336095, 12.283603, -0.046467, -0.334813, 0.941138, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightFoot': [0.997807, 0.039529, -0.053095, 0.000000, -0.065089, 0.439911, -0.895679, 12.326874, -0.012048, 0.897171, 0.441519, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightToeBase': [1.000000, 0.000000, 0.000000, 0.000000, -0.000000, 0.739495, -0.673162, 3.825008, -0.000000, 0.673162, 0.739495, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_RightToe_End': [0.999731, 0.000000, 0.023214, 0.000000, 0.000000, 1.000000, -0.000000, 2.568507, -0.023214, 0.000000, 0.999731, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftUpLeg': [-0.997948, 0.022915, 0.059784, 2.272210, 0.004858, -0.903972, 0.427565, -1.874674, 0.063841, 0.426978, 0.902006, -0.418631, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftLeg': [0.998650, -0.004497, -0.051748, 0.000000, 0.046426, 0.524088, 0.850398, 12.283576, 0.023296, -0.851652, 0.523589, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftFoot': [0.998446, 0.032986, -0.044909, 0.000000, -0.055707, 0.572268, -0.818173, 12.326874, -0.001288, 0.819403, 0.573216, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftToeBase': [1.000000, -0.000000, 0.000000, 0.000000, 0.000000, 0.771348, -0.636414, 3.825008, -0.000000, 0.636414, 0.771348, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
        'mixamorig_LeftToe_End': [0.999718, 0.000000, -0.023736, -0.000000, 0.000000, 1.000000, -0.000000, 2.568507, 0.023736, -0.000000, 0.999718, -0.000000, 0.000000, 0.000000, 0.000000, 1.000000],
    }

    @classmethod
    def get_topology(cls):
        return cls.TOPOLOGY

    @classmethod
    def get_bones(cls):
        return list(cls.TOPOLOGY.keys())

    @classmethod
    def get_t_pose(cls, height, bone_scales=None):
        """
        Calculates world positions for all bones in T-pose.
        Accounts for hierarchical bone scaling using proper matrix math.
        """
        scale = height / 50.0
        world_matrices = {}
        world_pose = {}
        
        # Identity for root
        world_matrices['root'] = np.identity(4)
        world_pose['root'] = (0, 0, 0)
        
        for bone, parent in cls.TOPOLOGY.items():
            if bone == 'root': continue
            
            # 1. Get local bind matrix (T * R)
            bind_m = cls.BIND_MATRICES.get(bone)
            if bind_m:
                # Ensure exactly 16 elements
                m_data = list(bind_m[:16])
                while len(m_data) < 16:
                    if len(m_data) == 15: # Common case: missing last element of identity row
                        m_data.append(1.0)
                    else:
                        m_data.append(0.0)
                local_m = np.array(m_data).reshape(4, 4)
            else:
                local_m = np.identity(4)
            
            # 2. Construct world matrix (NO SCALE for basis inheritance to avoid shear)
            # Child_World = Parent_World_No_Scale * Local_Bind_T_R
            p_mat = world_matrices.get(parent, np.identity(4))
            
            # Calculate parent world scale to apply to this joint's translation
            ps = [1.0, 1.0, 1.0]
            if bone_scales and parent in bone_scales:
                ps = bone_scales[parent]
            
            # Shift translation by parent scale
            local_t = local_m[0:3, 3].copy()
            local_t[0] *= ps[0]
            local_t[1] *= ps[1]
            local_t[2] *= ps[2]
            
            # New world matrix for this bone
            m = p_mat.copy()
            # Position: Parent_Pos + Parent_Rot * (Scaled_Local_Offset)
            m[0:3, 3] = p_mat[0:3, 3] + p_mat[0:3, 0:3] @ local_t
            # Rotation: Parent_Rot * Local_Rot
            m[0:3, 0:3] = p_mat[0:3, 0:3] @ local_m[0:3, 0:3]
            
            world_matrices[bone] = m
            
            # 3. Final T-Pose world position (with global height scale)
            pos = m[0:3, 3]
            world_pose[bone] = (pos[0] * scale, pos[1] * scale, pos[2] * scale)
            
        return world_pose