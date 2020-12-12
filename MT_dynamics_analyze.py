from ij.gui import Roi
from ij.plugin.frame import RoiManager
from ij import IJ
from ij import ImagePlus
import os

imp = IJ.getImage()
IJ.run(imp, "Set Scale...", "distance=1 known=1")  # スケールをデフォルト(pixel値)に戻す

rm = RoiManager.getInstance()

x = []
y = []

scale = 1 / 6.3   # µm/pixel Ti2 100倍
intv = 3  # time intervalを3sに設定
pauseTimeThreshold = intv * 5  # 5 frame以上の間
pauseLenThreshold = scale * 2  # 2 pixel 以上動かない

# まず空のリストをRoiの数だけ作成する
for i in range(rm.getCount()):
    x.append([])
    y.append([])


# 各Roiのx,yの値をリストに格納していく
for i in range(rm.getCount()):

    plygn = rm.getRoi(i).getFloatPolygon()  # Roi i番目のfloatpolygon インスタンスを得る

    for j in range(plygn.npoints):
        x[i].append(plygn.xpoints[j])
        y[i].append(plygn.ypoints[j])




#  時間の進行が0以下になっていたらプラスに補正する
for i in range(len(y)):

    for j in range(len(y[i])-1):

        if y[i][j + 1] - y[i][j] <= 0:
            y[i][j + 1] = y[i][j] + 1
  

# 上端と下端の値yを補正
for i in range(rm.getCount()):
    plygn = rm.getRoi(i).getFloatPolygon()
    y[i][0] = 0
    y[i][plygn.npoints - 1] = IJ.getImage().getHeight()  # カイモグラフの時間軸が縦のときのframe 枚数に等しい

dls = []  # 移動距離dlengthのリスト
vels = []  # 速度velocityのリスト
dts = []  # 経過時間のリスト

# 空のリストをリストxの要素の数だけ作成する
for i in range(len(x)):
    dls.append([])
    vels.append([])
    dts.append([])

for i in range(len(x)):
    for j in range(len(x[i]) - 1):
        # 移動距離とその経過時間,速度を計算する
        dx = x[i][j + 1] - x[i][j]
        dl = dx * scale  # µm

        dy = y[i][j + 1] - y[i][j]
        dt = dy * intv  # sec

        vel = 60 * (dl / dt)

        # 各リストに計算値を追加する
        dls[i].append(dl)
        dts[i].append(dt)
        vels[i].append(vel)

# 以下状態判定

pauseTimeThreshold = intv * 5  # 5 frameの間
pauseLength = scale * 3  # 3 pixel 以上動かない
states = []  # stateを格納するためのリスト

for i in range(len(dls)):  # 空のリストを要素の数だけ追加
    states.append([])

for i in range(len(dls)):
    for j in range(len(dls[i])):

        if abs(dls[i][j]) <= pauseLenThreshold and dts[i][j] >= pauseTimeThreshold:  # 1 pauseの定義に一致するものをリストに加える
            states[i].append("pause")

        elif abs(dls[i][j]) > pauseLenThreshold:
            if dls[i][j] > 0:  # 2 絶対値pauseLenThresholdより大きく正の場合, growth
                states[i].append("growth")
            elif dls[i][j] < 0:  # 3 絶対値pauseLenThresholdより大きく負の場合, shrink
                states[i].append("shrink")



        elif abs(dls[i][j]) <= pauseLenThreshold and dts[i][
            j] < pauseTimeThreshold:  # もし移動量がpauseLength以下かつpauseTimeThresholdより小さい場合
            if dls[i][j] > 0:  # 4
                states[i].append("growth")
            elif dls[i][j] < 0:  # 5
                states[i].append("shrink")

            elif dls[i][j] == 0:  # もし移動量0のとき

                if j == 0:  # 6 初期値のときはdlzeroとする
                    states[i].append("dlzero")
                else:  # 7 それ以外はprestateをstateとして加える

                    states[i].append(states[i][j - 1])

# 以下移動量0かつ Puasetimethreshold > dtのstateについて補正

d0_total_t = 0  # 移動量0が連続する場合、その時間を足して格納するための変数
count = 0  # 移動量0が連続する場合、その連続回数を足して格納するための変数

for i in range(len(states)):
    for j in range(len(states[i])):
        if j >= 0 and abs(dls[i][j]) == 0 and dts[i][j] < pauseTimeThreshold and states[i][j] != "pause":  # (1)
            # print ("(1): i = {}, j = {}, dts[i][j] = {}".format(i, j, dts[i][j]))
            
            if j == len(states[i])-1: # もしこの状態が観測の最後のとき
                states[i][len(states[i])-1] = states[i][len(states[i])-2] # 前の状態をその状態とする。

            elif dls[i][j] == dls[i][j + 1]:  # (2)
                # print ("(2): i = {}, j = {}, dts[i][j] = {}".format(i, j, dts[i][j]))
                if dls[i][j - 1] != 0 or j == 0:  # (3) dls = 0が現れるのが初めてのとき
                    d0_total_t = dts[i][j] + dts[i][j + 1]
                    count += 2
                    # print ("(3): i = {}, j = {}, dts[i][j] = {}, count = {} d0_total_t = {}".format(i, j, dts[i][j], count,  d0_total_t))
                else:  # (4)
                    d0_total_t += dts[i][j + 1]
                    count += 1
                    # print ("(4): i = {}, j = {}, dts[i][j] = {}, count = {}, d0_total_t = {}".format(i, j, dts[i][j], count, d0_total_t))



            elif dls[i][j] != dls[i][j + 1] and count != 0:  # (5)
                # print(("(5): i = {}, j = {}, dts[i][j] = {}, count = {}, d0_total_t = {}".format(i, j, dts[i][j], count, d0_total_t)))
                if d0_total_t >= pauseTimeThreshold:  # (6)
                    # print(("(6): i = {}, j = {}, dts[i][j] = {}, count = {}, d0_total_t = {}".format(i, j, dts[i][j], count, d0_total_t)))
                    for k, _ in enumerate(states[i][j + 1 - count: j + 1]):
                        # print k, _
                        states[i][j + 1 - count + k] = "pause"
                count = 0

            if states[i][j] == "dlzero":  # (7)
                #  print "(7), i = {}, j = {} dts = {}".format(i, j, dts[i][j])
                for n, _ in enumerate(states[i]):
                    if "dlzero" != states[i][n]:  # (8)
                        #  print "(8), i = {}, n = {}, j = {}, dts = {}".format(i, n, j, dts[i][j])
                        for m, _ in enumerate(states[i][0:n]):
                            states[i][m] = states[i][n]

                        break  # (9)
                #  print "(9), i = {}, n = {}, j = {}, state = {}".format(i, n, j, states[i][j])

#  以下event判定
events = []

for i in range(len(states)):
    events.append([])

for i in range(len(states)):
    for j in range(len(states[i])):
        if j < len(states[i]) - 1:
            if j == 0:
                events[i].append("{}".format(states[i][j]))

            if states[i][j] == states[i][j + 1]:
                events[i].append("{}".format(states[i][j + 1]))
            elif states[i][j] == "growth" and states[i][j + 1] == "shrink":
                events[i].append("gs")
            elif states[i][j] == "growth" and states[i][j + 1] == "pause":
                events[i].append("gp")
            elif states[i][j] == "pause" and states[i][j + 1] == "shrink":
                events[i].append("ps")
            elif states[i][j] == "pause" and states[i][j + 1] == "growth":
                events[i].append("pg")
            elif states[i][j] == "shrink" and states[i][j + 1] == "growth":
                events[i].append("sg")
            elif states[i][j] == "shrink" and states[i][j + 1] == "pause":
                events[i].append("sp")

IJ.log("\\Clear")  # logのclear command
IJ.log(
    "indx" + "\t" + "id" + "\t" + "dt_s" + "\t" + "dlength_um" + "\t" + "velocity_um/min" + "\t" + "state" + "\t" + "event"+ "\t" + "event_bool")

for i in range(len(vels)):
    for j in range(len(vels[i])):
        IJ.log(str(j) + "\t" + str(i) + "\t" + str(dts[i][j]) + "\t" + str(dls[i][j]) + "\t" + str(
            vels[i][j]) + "\t" + str(states[i][j]) + "\t" + str(events[i][j])+ "\t" + str("TRUE"))

# logの結果をsave        
from ij import IJ
import os
from ij import WindowManager as wm

imDir = IJ.getDirectory("image")  # 現在のactiveなImageのDirectoryをimDirとして取得
os.chdir(imDir + "..")  # 現在の作業ディレクトリをimDirのひとつ上に指定
u1_Dir = os.getcwd()  # このディレクトリの
base = os.path.basename(u1_Dir)  # basenameを保存ファイル名として使うために取得する

os.chdir(u1_Dir + "/..")
u2_Dir = os.getcwd()  # imageDirectoryのふたつ上の階層に

if not os.path.exists(u2_Dir + os.sep + "analyze"):  # anlyzeというフォルダを作成
    os.makedirs(u2_Dir + os.sep + "analyze")

svDir = u2_Dir + os.sep + "analyze"  # ここを保存先とする

wm.setWindow(wm.getWindow("Log"))

IJ.saveAs("Text", svDir + os.sep + base + "-analyze_MT_dynamics")

n = len(dls) 

seq_growth_dls =[]
seq_growth_dl = 0
seq_shrink_dls = []
seq_shrink_dl = 0
for i in range(len(states)):
    seq_growth_dls.append([])
    seq_shrink_dls.append([])
 
for i in range(len(states)):
    for j in range(len(states[i])):
        if states[i][j]== "growth":
            if j < len(states[i])-1 and states[i][j] == states[i][j+1]:
                # print states[i][j], i, j 
                seq_growth_dl += dls[i][j]
            else:
                seq_growth_dl += dls[i][j]
                seq_growth_dls[i].append(seq_growth_dl)
                seq_growth_dl = 0
        
        elif states[i][j] == "shrink":
            if j < len(states[i])-1 and states[i][j] == states[i][j+1]:
                seq_shrink_dl += dls[i][j]
            else:
                seq_shrink_dl += dls[i][j]
                seq_shrink_dls[i].append(seq_shrink_dl)
                seq_shrink_dl = 0


mean_seq_growth_dls = []
mean_seq_shrink_dls = []


for i in range(len(seq_shrink_dls)):

    if len(seq_shrink_dls[i]) == 0:
        mean_shrink_dl = 0
        mean_seq_shrink_dls.append(mean_shrink_dl)
    else:
        mean_shrink_dl = abs(sum(seq_shrink_dls[i])/len(seq_shrink_dls[i]))
        mean_seq_shrink_dls.append(mean_shrink_dl)


for i in range(len(seq_growth_dls)):

    if len(seq_growth_dls[i]) == 0:
        mean_growth_dl = 0
        mean_seq_growth_dls.append(mean_growth_dl)

    else:    
        mean_growth_dl = sum(seq_growth_dls[i])/len(seq_growth_dls[i])
        mean_seq_growth_dls.append(mean_growth_dl)

# IJ.log("\\Clear")  # logのclear command

print(seq_shrink_dls)
print(seq_growth_dls)
print(mean_seq_growth_dls)
print(mean_seq_shrink_dls)
   


                