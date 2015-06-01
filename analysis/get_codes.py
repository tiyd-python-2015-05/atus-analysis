


d = [line.rstrip('\n') for line in open('list_activity_codes.txt')]

# print(d)

nums = [int(line[:2]) for line in d]

level = 0
loc = [0, 0, 0]
for i in range(len(d)):
    line = d[i]
    i = nums[i]
    if i <= loc[level]:
        level += 1

    print(str(i)+" ", end="")
