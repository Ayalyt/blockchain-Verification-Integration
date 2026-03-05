class ModelingSettings:
    MAX_LOOP_DEPTH = 1000
    RECORD_CPP_JSON = False
    # 这个决定了是否要expaux进行merge, 本质会影响CPP中对关系运算的建模方法
    # 即在CPP建模过程中，关系运算的结果仍然是FF_Element，而不是boolean
    # 个人的感觉是没有必要的，但是得基于实验结果进行判断
    CPP_MORE_MERGE = False

    BINARY_INPUT = False
    # model the undefined behavior or not at IF branches
    IF_UNDEFINED_BEHAVIOR = False
    # require the assignment for a signal must be consistent in Circom source code and the witness calculator
    ASSIGNMENT_CONSISTENT = True

    CIRCOM_VERSION = '2.1.8'
    
    TABLE_OUTPUT = True

    CHECK_CALCULATION = True
    CHECK_CONSTRAINT = True

    ASSERT_PROPERTY = False

    HashSignalInfo_Size = 24
    Witness_size = 8
    FrElement_size = 40

    @staticmethod
    def compare_versions(v1: str, v2: str) -> int:
        """
        比较两个版本号字符串。
        :param v1: 版本号1 (如 "2.2.2")
        :param v2: 版本号2 (如 "2.1.8")
        :return: 1 如果 v1 > v2, -1 如果 v1 < v2, 0 如果相等
        """
        nums1 = list(map(int, v1.split(".")))
        nums2 = list(map(int, v2.split(".")))

        # 对齐长度，不足的补 0
        max_len = max(len(nums1), len(nums2))
        nums1.extend([0] * (max_len - len(nums1)))
        nums2.extend([0] * (max_len - len(nums2)))

        # 逐位比较
        for n1, n2 in zip(nums1, nums2):
            if n1 > n2:
                return 1
            elif n1 < n2:
                return -1
        return 0

    @staticmethod
    def old_version():
        return ModelingSettings.compare_versions(ModelingSettings.CIRCOM_VERSION, '2.2.0') < 0
