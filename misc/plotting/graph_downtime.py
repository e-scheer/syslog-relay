import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

queue_sizes = [(64, 45600), (128, 91200), (256, 182400), (512, 364800)]

for size_mb, qsize in queue_sizes:
    max_duration = 300
    xAxis = []
    yAxis = []
    for i in range(1, max_duration):
        xAxis.append(i)
        yAxis.append(int(qsize / i))

    plt.clf()
    fig, ax=plt.subplots()
    plt.plot(xAxis,yAxis)

    trans = transforms.blended_transform_factory(
        ax.get_yticklabels()[0].get_transform(), ax.transData)

    ax.axhline(y=yAxis[-1], color="red", linestyle='--')    
    ax.text(0, yAxis[-1], "{:.0f}".format(yAxis[-1]), color="red", transform=trans, 
            ha="right", va="center")

    plt.xlabel('Maximum downtime in seconds')
    plt.ylabel('Maximum number of messages per second')
    plt.savefig(f'max_downtime_for_{qsize}_msgs_{max_duration}_secs')