import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import time
import tkinter as tk


def sim(IntertwinedFateNum, Discounts, Budget, ExpectedCharacterNum, CharacterPoolGuarantee, CharacterPoolStage,
        ExpectedWeaponNum, WeaponPoolStage):
    start = time.time()
    # 拥有的纠缠之缘数量
    # 抽卡消耗比例
    IntertwinedFateNum = int(int(IntertwinedFateNum / 160) / Discounts)

    # 预算
    # ------------------------- 下为角色池部分 -------------------------
    # 期望抽到角色数（0-7）
    # 当前是否大保底（True/False）
    # 角色池的水位（0-89）
    # ------------------------- 下为武器池部分 -------------------------
    # 期望抽到武器数（0-5）
    # 当前是否大保底（True/False）
    # 武器池的水位（0-79）
    output = []

    # 单次抽卡的概率
    # 角色池
    def percent_character(s):
        if s <= 70:
            return 0.008
        elif s <= 79:
            return 0.008 + 0.1 * (s - 70)
        else:
            return 1

    # 武器池
    def percent_weapon(s):
        if s <= 70:
            return 0.008
        elif s <= 79:
            return 0.008 + 0.1 * (s - 70)
        else:
            return 1

    # 初始化一个零矩阵
    size = 160 * ExpectedCharacterNum + 80 * ExpectedWeaponNum + 1  # 这里加上1是为了让最后一行表示达成抽卡预期的状态
    TPmatrix = np.zeros((size, size))
    # 角色池的初始状态设置
    CharacterPoolOffset = 0
    if ExpectedCharacterNum != 0:
        if not CharacterPoolGuarantee:
            CharacterPoolOffset = CharacterPoolStage
        elif CharacterPoolGuarantee:
            CharacterPoolOffset = CharacterPoolStage + 80
    # 生成转移概率矩阵（矩阵前面的行是武器，后面的行是角色，最后一行表示的状态是已经达成抽卡预期）
    # 这一部分代码生成抽武器的状态，如果要抽的武器数为0，那么就不会运行这一部分代码
    for i in range(0, ExpectedWeaponNum):
        offset = 80 * i
        # 小保底/命定0
        for j in range(0, 80):
            x = j % 80 + 1
            if i == ExpectedWeaponNum - 1:
                # 该行属于要抽的最后一把武器的部分，那么如果出限定就会进入角色部分，要加上角色池的初始偏移量
                TPmatrix[offset + j, offset + 80 + CharacterPoolOffset] = percent_weapon(x)
            else:
                # 该行不属于要抽的最后一把武器的部分，那么抽完会进入下一把武器
                TPmatrix[offset + j, offset + 80] = percent_weapon(x)
            if j != 79:
                TPmatrix[offset + j, offset + j + 1] = 1 - percent_weapon(x)
    # 这一部分代码生成抽角色的状态，如果要抽的角色数为0，那么就不会运行这一部分代码
    for i in range(0, ExpectedCharacterNum):
        offset = 160 * i + ExpectedWeaponNum * 80
        for j in range(0, 80):
            x = j % 80 + 1
            TPmatrix[offset + j, offset + 160] = percent_character(x) * 0.5
            TPmatrix[offset + j, offset + 80] = percent_character(x) * 0.5
            if j != 79:
                TPmatrix[offset + j, offset + j + 1] = 1 - percent_character(x)
        for j in range(80, 160):
            x = j % 80 + 1
            TPmatrix[offset + j, offset + 160] = percent_character(x)
            if j != 159:
                TPmatrix[offset + j, offset + j + 1] = 1 - percent_character(x)
    # 最后一行表示已经达成抽卡预期，所以从该状态到其他状态的概率都是0，到自身的概率为1
    TPmatrix[size - 1, size - 1] = 1
    # 生成初始状态向量，如果抽武器，那么和武器池水位有关，否则和角色池水位有关
    initVector = np.zeros(size)
    if ExpectedWeaponNum != 0:
        initVector[WeaponPoolStage] = 1
    else:  # 这里是不抽武器的情况，和角色池水位有关
        initVector[CharacterPoolOffset] = 1
    # 存储达到10%、25%、50%、75%、90%概率时的抽数
    percent10num = 0
    percent25num = 0
    percent50num = 0
    percent75num = 0
    percent90num = 0
    percentlist = [0]
    # 存储达到预期次数的概率
    percentRes = -1
    resultVector = initVector
    result = 0
    i = 0
    while result < 0.999:
        # 将初始状态向量和转移概率矩阵不断相乘，相乘的次数为抽数，得到预期次数后状态的概率分布
        i += 1
        resultVector = resultVector @ TPmatrix
        result = resultVector[size - 1]
        percentlist.append(result)
        if i == IntertwinedFateNum - 1:
            percentRes = result
        if result > 0.1 and percent10num == 0:
            percent10num = i + 1
        if result > 0.25 and percent25num == 0:
            percent25num = i + 1
        if result > 0.5 and percent50num == 0:
            percent50num = i + 1
        if result > 0.75 and percent75num == 0:
            percent75num = i + 1
        if result > 0.9 and percent90num == 0:
            percent90num = i + 1
    # 画一幅概率曲线图
    plt.rcParams['font.sans-serif'] = ['SimHei']
    ax = plt.axes()
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.025))
    if len(percentlist) > 500:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(100))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(25))
    elif len(percentlist) > 200:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(50))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(12.5))
    elif len(percentlist) > 80:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(5))
    elif len(percentlist) > 30:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(2.5))
    ax.set_title('鸣潮抽卡成功率分布')
    ax.grid(True)
    plt.plot(percentlist)
    plt.xlim(xmin=0, xmax=len(percentlist) + 5)
    plt.ylim(ymin=0, ymax=1)
    if IntertwinedFateNum != 0:
        plt.vlines(x=IntertwinedFateNum, ymin=0, ymax=percentRes, label='', linestyles='dashed')
        plt.hlines(y=percentRes, xmin=0, xmax=IntertwinedFateNum, label='', linestyles='dashed')
    for i in range(int(Budget / 648) + 1):
        if len(percentlist) > IntertwinedFateNum + 50.5 * i / Discounts:
            possibility = percentlist[int(IntertwinedFateNum + 50.5 * i / Discounts)]
        else:
            possibility = 1
        output.append(f'额外氪{i}个648后成功率为{possibility * 100:.1f}%')

    output.append(f'模拟用时{time.time() - start:.3f}秒')
    return output


def main():
    def textbox_output(result):
        result_text.config(state=tk.NORMAL)  # 设置为可编辑状态
        result_text.insert(tk.END, f"{result}\n")
        result_text.see(tk.END)
        result_text.config(state=tk.DISABLED)  # 设置为只读状态

    def clear_textbox():
        result_text.config(state=tk.NORMAL)  # 设置为可编辑状态
        result_text.delete('1.0', tk.END)  # 清空文本框内容
        result_text.config(state=tk.DISABLED)  # 设置为只读状态

    def shell():
        try:
            result = sim(int(IntertwinedFateNum.get() if IntertwinedFateNum.get() else 0.0),
                         float(Discounts.get() if Discounts.get() else 1.0),
                         int(Budget.get() if Budget.get() else 0.0),
                         int(ExpectedCharacterNum.get() if ExpectedCharacterNum.get() else 0.0),
                         bool(checkbox_1.get()),
                         int(CharacterPoolStage.get() if CharacterPoolStage.get() else 0.0),
                         int(ExpectedWeaponNum.get() if ExpectedWeaponNum.get() else 0.0),
                         int(WeaponPoolStage.get() if WeaponPoolStage.get() else 0.0))
        except ValueError:
            result = ['输入无效']

        for item in result:
            textbox_output(item)

    root = tk.Tk()
    root.title("鸣潮抽卡模拟器")
    root.geometry("576x400")

    tk.Label(root, text="星声数量:").grid(row=0, column=0, padx=5, pady=5)
    IntertwinedFateNum = tk.Entry(root)
    IntertwinedFateNum.grid(row=1, column=0, padx=5, pady=5)

    tk.Label(root, text="抽卡消耗比例(默认:1):").grid(row=0, column=1, padx=5, pady=5)
    Discounts = tk.Entry(root)
    Discounts.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(root, text="额外氪金预算(RMB):").grid(row=0, column=2, padx=5, pady=5)
    Budget = tk.Entry(root)
    Budget.grid(row=1, column=2, padx=5, pady=5)

    tk.Label(root, text="期望抽到的角色数量:").grid(row=2, column=0, padx=5, pady=5)
    ExpectedCharacterNum = tk.Entry(root)
    ExpectedCharacterNum.grid(row=3, column=0, padx=5, pady=5)

    checkbox_1 = tk.BooleanVar()
    CharacterPoolGuarantee = tk.Checkbutton(root, text="角色池大保底", variable=checkbox_1)
    CharacterPoolGuarantee.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(root, text="角色池水位:").grid(row=2, column=2, padx=5, pady=5)
    CharacterPoolStage = tk.Entry(root)
    CharacterPoolStage.grid(row=3, column=2, padx=5, pady=5)

    tk.Label(root, text="期望抽到的武器数量:").grid(row=4, column=0, padx=5, pady=5)
    ExpectedWeaponNum = tk.Entry(root)
    ExpectedWeaponNum.grid(row=5, column=0, padx=5, pady=5)

    tk.Label(root, text="武器池水位:").grid(row=4, column=2, padx=5, pady=5)
    WeaponPoolStage = tk.Entry(root)
    WeaponPoolStage.grid(row=5, column=2, padx=5, pady=5)

    button_sim = tk.Button(root, text="模拟", command=shell)
    button_sim.grid(row=8, column=0, padx=5, pady=5)

    button_show_plot = tk.Button(root, text="生成概率曲线图", command=plt.show)
    button_show_plot.grid(row=8, column=1, padx=5, pady=5)

    button_clear = tk.Button(root, text="清空结果", command=clear_textbox)
    button_clear.grid(row=8, column=2, padx=5, pady=5)

    result_text = tk.Text(root, height=10, state='normal')
    result_text.grid(row=9, column=0, padx=5, pady=5, columnspan=3)
    result_text.config(state=tk.DISABLED)

    root.mainloop()


if __name__ == '__main__':
    main()
