import matplotlib.pyplot as plt
import sys

with open(sys.argv[1], "r") as f:
    data = f.read().splitlines()
data = [i.split(" ") for i in data]
score = [float(d[0]) for d in data]
loss = [float(d[1]) for d in data]
avg = 100
arg_min = -3
arg_max = 5
y = [sum(score[i-avg:i])/avg for i, _ in enumerate(score[avg:])]
ax = plt.subplot(5, 1, 1)
ax.set_ylim([arg_min, arg_max])
plt.xlabel("epoch")
plt.ylabel("Average score")
plt.title("Average score (moving average of 50 games)")
plt.grid()
plt.plot(y[avg:])

y = [sum(loss[i-avg:i])/avg for i, _ in enumerate(loss[avg:])]
ax = plt.subplot(5, 1, 2)
plt.title("DQN Network Loss")
plt.xlabel("epoch")
plt.ylabel("Network Loss")
#ax.set_ylim([arg_min, arg_max])
plt.grid()
plt.plot(y[avg:])

ax = plt.subplot(5, 1, 3)
ax.set_xlim([arg_min, arg_max])
plt.grid()
plt.xlabel("score")
plt.ylabel("#count")
plt.title("score count hist before 200 epoch")
plt.hist(score[0:200], bins=20)

ax = plt.subplot(5, 1, 4)
ax.set_xlim([arg_min, arg_max])
plt.grid()
plt.xlabel("score")
plt.ylabel("#count")
plt.title("score count hist after 200 epoch")
plt.hist(score[200:8000], bins=20)


# ax = plt.subplot(5, 1, 5)
# ax.set_xlim([arg_min, arg_max])
# plt.grid()
# plt.hist(score[8000:], bins=20)

plt.show()
print(sum(score[-avg:])/ avg)