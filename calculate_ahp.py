import numpy as np
import pandas as pd
from fractions import Fraction

# 自定义的判断矩阵
ahpscore = np.array([
    [1,Fraction(1,7),Fraction(1,5)],
    [7,1,3],
    [5,Fraction(1,3),1]
    ])

def checkMatrix(data):
    """
    检查判断矩阵是否符合要求，如果符合要求返回 1，不符合要求返回 0。
    """
    if len(data)>11:
        print("错误，参数超过11个")
        return 0
    if len(data[0,])!=len(data[:,-1]):
        print("错误，判断矩阵不是方阵")
        return 0
    for i in range(len(data)):
        if data[i,i] != 1:
            print("错误，判断矩阵主对角线元素不全为1")
            return 0
        for j in range(i+1,len(data)):
            if data[i,j]!=Fraction(1,data[j,i]):
                print("错误，判断矩阵非正反矩阵")
                return 0
    return 1



def calu_consistency(data):
    """
    检验判断矩阵的一致性，
    计算满足一致性要求的矩阵的特征向量，
    返回其最大特征值和最大特征值对应的特性向量
    """
    w,v = np.linalg.eig(ahpscore.astype("float64"))
    for i in w:
        # 删除特征值向量中的虚部不为0的向量
        if i.imag != 0:
            w = np.setdiff1d(w,i)
    maxW = np.max(w)
    # maxVindex：最大特征值对应的特征向量
    maxVindex = np.where(w == maxW)[0]
    CI = (maxW-len(data))/(len(data)-1)

    #RI:平均一致性列表
    RI = np.array([0,0,0.58,0.9,1.12,1.24,1.32,1.41,1.45,1.49,1.51])
    CR = np.round(CI/RI[len(data)-1],4).real
    if CR > 0.1:
        print("CR = %f,一致性检验不通过" %(CR))
    else:
        return {
            "eigenvalues": maxW,
            "eigenvectors ":v[:,maxVindex].real
        }

if __name__ == "__main__":
    data = ahpscore
    if checkMatrix(data) == 1:
        print(calu_consistency(data))
    


